from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Video, Config
from youtube_api import YouTubeAPI
from discord_webhook import DiscordWebhook
from config_manager import ConfigManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

youtube_api = YouTubeAPI()
discord_webhook = DiscordWebhook()

@app.route('/')
def index():
    """Display all saved videos"""
    logger.info("Routes: Accediendo a página de inicio")
    try:
        videos = Video.query.order_by(Video.added_at.desc()).all()
        logger.info(f"Routes: Encontrados {len(videos)} videos en la colección")
        return render_template('index.html', videos=videos)
    except Exception as e:
        logger.error(f"Routes: Error al cargar página de inicio: {e}")
        flash('Error al cargar la página', 'error')
        return render_template('index.html', videos=[])

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    """Add a new video from YouTube URL"""
    if request.method == 'GET':
        logger.info("Routes: Accediendo a página de agregar video")
        return render_template('add_video.html')
    
    logger.info("Routes: Procesando solicitud para agregar video")
    url = request.form.get('url', '').strip()
    logger.info(f"Routes: URL recibida: {url}")
    
    if not url:
        logger.warning("Routes: URL vacía recibida")
        flash('Por favor ingresa una URL de YouTube', 'error')
        return render_template('add_video.html')
    
    try:
        # Extract video ID
        logger.info("Routes: Extrayendo video ID de la URL")
        video_id = youtube_api.extract_video_id(url)
        if not video_id:
            logger.warning(f"Routes: No se pudo extraer video ID de: {url}")
            flash('URL de YouTube inválida. Verifica la URL e intenta de nuevo.', 'error')
            return render_template('add_video.html')
        
        logger.info(f"Routes: Video ID extraído: {video_id}")
        
        # Check if video already exists
        logger.info("Routes: Verificando si el video ya existe")
        existing_video = Video.query.filter_by(youtube_id=video_id).first()
        if existing_video:
            logger.warning(f"Routes: Video {video_id} ya existe en la colección")
            flash(f'El video "{existing_video.title}" ya está en tu colección', 'warning')
            return redirect(url_for('index'))
        
        # Fetch video details from YouTube API
        logger.info("Routes: Obteniendo detalles del video desde YouTube API")
        video_details = youtube_api.get_video_details(video_id)
        
        # Parse published date
        published_at = None
        if video_details.get('published_at'):
            try:
                published_at = datetime.fromisoformat(video_details['published_at'].replace('Z', '+00:00'))
                logger.debug(f"Routes: Fecha de publicación procesada: {published_at}")
            except Exception as e:
                logger.warning(f"Routes: No se pudo procesar fecha de publicación: {video_details.get('published_at')} - {e}")
        
        # Create new video record
        logger.info("Routes: Creando registro del video en la base de datos")
        video = Video(
            youtube_id=video_id,
            title=video_details['title'],
            description=video_details['description'],
            thumbnail_url=video_details['thumbnail_url'],
            duration=video_details['duration'],
            view_count=video_details['view_count'],
            like_count=video_details['like_count'],
            published_at=published_at
        )
        
        db.session.add(video)
        db.session.commit()
        
        logger.info(f"Routes: Video '{video.title}' agregado exitosamente")
        flash(f'¡Video "{video.title}" agregado exitosamente a tu colección!', 'success')
        return redirect(url_for('index'))
        
    except ValueError as e:
        logger.error(f"Routes: Error de validación: {e}")
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Routes: Error inesperado agregando video: {e}")
        flash('Ocurrió un error inesperado. Intenta de nuevo.', 'error')
    
    return render_template('add_video.html')

@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    """Delete a video from the collection"""
    logger.info(f"Routes: Eliminando video con ID: {video_id}")
    
    try:
        video = Video.query.get_or_404(video_id)
        video_title = video.title
        logger.info(f"Routes: Video encontrado para eliminar: '{video_title}'")
        
        db.session.delete(video)
        db.session.commit()
        
        logger.info(f"Routes: Video '{video_title}' eliminado exitosamente")
        flash(f'Video "{video_title}" eliminado exitosamente', 'success')
    except Exception as e:
        logger.error(f"Routes: Error al eliminar video: {e}")
        flash('Error al eliminar video. Intenta de nuevo.', 'error')
    
    return redirect(url_for('index'))

@app.route('/send_to_discord/<int:video_id>', methods=['POST'])
def send_to_discord(video_id):
    """Send video to Discord webhook"""
    logger.info(f"Routes: Enviando video a Discord, ID: {video_id}")
    
    try:
        video = Video.query.get_or_404(video_id)
        logger.info(f"Routes: Video encontrado para enviar: '{video.title}'")
        
        discord_webhook.send_video_notification(video)
        logger.info(f"Routes: Video '{video.title}' enviado a Discord exitosamente")
        flash(f'¡Video "{video.title}" enviado a Discord exitosamente!', 'success')
    except ValueError as e:
        logger.error(f"Routes: Error de validación enviando a Discord: {e}")
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Routes: Error inesperado enviando a Discord: {e}")
        flash('Error al enviar a Discord. Intenta de nuevo.', 'error')
    
    return redirect(url_for('index'))

@app.route('/get_formatted_message/<int:video_id>')
def get_formatted_message(video_id):
    """Get formatted message for copying"""
    logger.info(f"Routes: Obteniendo mensaje formateado para video ID: {video_id}")
    
    try:
        video = Video.query.get_or_404(video_id)
        logger.info(f"Routes: Generando mensaje formateado para: '{video.title}'")
        message = video.formatted_message
        logger.debug(f"Routes: Mensaje generado: {len(message)} caracteres")
        return jsonify({'message': message})
    except Exception as e:
        logger.error(f"Routes: Error obteniendo mensaje formateado: {e}")
        return jsonify({'error': 'Error al obtener mensaje'}), 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Display and handle configuration"""
    logger.info("Routes: Accediendo a página de configuración")
    
    if request.method == 'POST':
        logger.info("Routes: Procesando actualización de configuración")
        
        action = request.form.get('action')
        logger.info(f"Routes: Acción recibida: {action}")
        
        if action == 'update_youtube':
            api_key = request.form.get('youtube_api_key', '').strip()
            logger.info("Routes: Actualizando YouTube API key")
            
            if api_key:
                # Test the API key
                logger.info("Routes: Probando YouTube API key")
                is_valid, message = ConfigManager.test_youtube_api(api_key)
                
                if is_valid:
                    ConfigManager.set_config('YT_API_KEY', api_key)
                    logger.info("Routes: YouTube API key guardada exitosamente")
                    flash(f'YouTube API key configurada exitosamente: {message}', 'success')
                else:
                    logger.warning(f"Routes: YouTube API key inválida: {message}")
                    flash(f'Error con YouTube API key: {message}', 'error')
            else:
                logger.warning("Routes: YouTube API key vacía")
                flash('YouTube API key no puede estar vacía', 'error')
        
        elif action == 'update_discord':
            webhook_url = request.form.get('discord_webhook', '').strip()
            logger.info("Routes: Actualizando Discord webhook")
            
            if webhook_url:
                # Test the webhook
                logger.info("Routes: Probando Discord webhook")
                is_valid, message = ConfigManager.test_discord_webhook(webhook_url)
                
                if is_valid:
                    ConfigManager.set_config('DISCORD_WEBHOOK', webhook_url)
                    logger.info("Routes: Discord webhook guardado exitosamente")
                    flash(f'Discord webhook configurado exitosamente: {message}', 'success')
                else:
                    logger.warning(f"Routes: Discord webhook inválido: {message}")
                    flash(f'Error con Discord webhook: {message}', 'error')
            else:
                logger.warning("Routes: Discord webhook vacío")
                flash('Discord webhook no puede estar vacío', 'error')
        
        elif action == 'test_youtube':
            logger.info("Routes: Probando YouTube API key existente")
            api_key = ConfigManager.get_config('YT_API_KEY')
            if api_key:
                is_valid, message = ConfigManager.test_youtube_api(api_key)
                flash(f'Prueba YouTube API: {message}', 'success' if is_valid else 'error')
            else:
                flash('No hay YouTube API key configurada', 'error')
        
        elif action == 'test_discord':
            logger.info("Routes: Probando Discord webhook existente")
            webhook_url = ConfigManager.get_config('DISCORD_WEBHOOK')
            if webhook_url:
                is_valid, message = ConfigManager.test_discord_webhook(webhook_url)
                flash(f'Prueba Discord webhook: {message}', 'success' if is_valid else 'error')
            else:
                flash('No hay Discord webhook configurado', 'error')
    
    # Get current configuration status
    youtube_configured = ConfigManager.get_config('YT_API_KEY') is not None
    discord_configured = ConfigManager.get_config('DISCORD_WEBHOOK') is not None
    
    logger.info(f"Routes: Estado de configuración - YouTube: {youtube_configured}, Discord: {discord_configured}")
    
    return render_template('config.html', 
                         youtube_configured=youtube_configured,
                         discord_configured=discord_configured)

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html'), 500
