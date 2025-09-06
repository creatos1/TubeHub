import requests
import logging
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class DiscordWebhook:
    def __init__(self):
        logger.info("DiscordWebhook: Inicializando clase DiscordWebhook")
        self.webhook_url = ConfigManager.get_config('DISCORD_WEBHOOK')
        logger.info(f"DiscordWebhook: Webhook {'configurado' if self.webhook_url else 'no encontrado'}")
    
    def send_message(self, content, username="YouTube Hub", avatar_url=None):
        """Send message to Discord webhook"""
        logger.info(f"DiscordWebhook: Enviando mensaje a Discord (usuario: {username})")
        
        # Refresh webhook URL from database
        self.webhook_url = ConfigManager.get_config('DISCORD_WEBHOOK')
        
        if not self.webhook_url:
            logger.error("DiscordWebhook: Webhook URL no configurada")
            raise ValueError("Discord webhook no configurado. Configúralo en la página de Configuración.")
        
        payload = {
            'content': content,
            'username': username
        }
        
        if avatar_url:
            payload['avatar_url'] = avatar_url
        
        logger.info(f"DiscordWebhook: Payload preparado: {len(content)} caracteres de contenido")
        logger.debug(f"DiscordWebhook: Enviando a webhook: {self.webhook_url[:50]}...")
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            logger.info(f"DiscordWebhook: Respuesta HTTP: {response.status_code}")
            response.raise_for_status()
            logger.info("DiscordWebhook: Mensaje enviado a Discord exitosamente")
            return True
            
        except requests.RequestException as e:
            logger.error(f"DiscordWebhook: Error al enviar mensaje: {e}")
            raise ValueError(f"Error al enviar mensaje a Discord: {str(e)}")
    
    def send_video_notification(self, video):
        """Send a formatted video notification to Discord"""
        logger.info(f"DiscordWebhook: Enviando notificación de video: {video.title}")
        
        # Refresh webhook URL from database
        self.webhook_url = ConfigManager.get_config('DISCORD_WEBHOOK')
        
        if not self.webhook_url:
            logger.error("DiscordWebhook: Webhook URL no configurada")
            raise ValueError("Discord webhook no configurado. Configúralo en la página de Configuración.")
        
        description = video.description[:500] + "..." if len(video.description) > 500 else video.description
        
        embed = {
            "title": video.title,
            "description": description,
            "url": video.youtube_url,
            "color": 16711680,  # Red color for YouTube
            "thumbnail": {
                "url": video.thumbnail_url
            },
            "fields": [
                {
                    "name": "Views",
                    "value": f"{video.view_count:,}",
                    "inline": True
                },
                {
                    "name": "Likes",
                    "value": f"{video.like_count:,}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "YouTube Hub",
                "icon_url": "https://www.youtube.com/favicon.ico"
            }
        }
        
        payload = {
            'embeds': [embed],
            'username': 'YouTube Hub'
        }
        
        logger.info(f"DiscordWebhook: Embed preparado para video {video.youtube_id}")
        logger.debug(f"DiscordWebhook: Tamaño del payload: {len(str(payload))} caracteres")
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            logger.info(f"DiscordWebhook: Respuesta HTTP: {response.status_code}")
            response.raise_for_status()
            logger.info("DiscordWebhook: Notificación de video enviada a Discord exitosamente")
            return True
            
        except requests.RequestException as e:
            logger.error(f"DiscordWebhook: Error al enviar notificación: {e}")
            raise ValueError(f"Error al enviar notificación a Discord: {str(e)}")
