from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Video
from youtube_api import YouTubeAPI
from discord_webhook import DiscordWebhook
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

youtube_api = YouTubeAPI()
discord_webhook = DiscordWebhook()

@app.route('/')
def index():
    """Display all saved videos"""
    videos = Video.query.order_by(Video.added_at.desc()).all()
    return render_template('index.html', videos=videos)

@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    """Add a new video from YouTube URL"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        
        if not url:
            flash('Please enter a YouTube URL', 'error')
            return render_template('add_video.html')
        
        try:
            # Extract video ID
            video_id = youtube_api.extract_video_id(url)
            if not video_id:
                flash('Invalid YouTube URL. Please check the URL and try again.', 'error')
                return render_template('add_video.html')
            
            # Check if video already exists
            existing_video = Video.query.filter_by(youtube_id=video_id).first()
            if existing_video:
                flash(f'Video "{existing_video.title}" is already in your collection', 'warning')
                return redirect(url_for('index'))
            
            # Fetch video details from YouTube API
            video_details = youtube_api.get_video_details(video_id)
            
            # Parse published date
            published_at = None
            if video_details.get('published_at'):
                try:
                    published_at = datetime.fromisoformat(video_details['published_at'].replace('Z', '+00:00'))
                except:
                    logger.warning(f"Could not parse published date: {video_details.get('published_at')}")
            
            # Create new video record
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
            
            flash(f'Successfully added "{video.title}" to your collection!', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            logger.error(f"Unexpected error adding video: {e}")
            flash('An unexpected error occurred. Please try again.', 'error')
    
    return render_template('add_video.html')

@app.route('/delete_video/<int:video_id>', methods=['POST'])
def delete_video(video_id):
    """Delete a video from the collection"""
    video = Video.query.get_or_404(video_id)
    video_title = video.title
    
    try:
        db.session.delete(video)
        db.session.commit()
        flash(f'Successfully deleted "{video_title}"', 'success')
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        flash('Failed to delete video. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/send_to_discord/<int:video_id>', methods=['POST'])
def send_to_discord(video_id):
    """Send video to Discord webhook"""
    video = Video.query.get_or_404(video_id)
    
    try:
        discord_webhook.send_video_notification(video)
        flash(f'Successfully sent "{video.title}" to Discord!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        logger.error(f"Error sending to Discord: {e}")
        flash('Failed to send to Discord. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/get_formatted_message/<int:video_id>')
def get_formatted_message(video_id):
    """Get formatted message for copying"""
    video = Video.query.get_or_404(video_id)
    return jsonify({'message': video.formatted_message})

@app.route('/config')
def config():
    """Display configuration instructions"""
    return render_template('config.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html'), 500
