import os
import requests
import logging

logger = logging.getLogger(__name__)

class DiscordWebhook:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK')
    
    def send_message(self, content, username="YouTube Hub", avatar_url=None):
        """Send message to Discord webhook"""
        if not self.webhook_url:
            raise ValueError("Discord webhook URL not found. Please set DISCORD_WEBHOOK environment variable.")
        
        payload = {
            'content': content,
            'username': username
        }
        
        if avatar_url:
            payload['avatar_url'] = avatar_url
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Message sent to Discord successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to send Discord message: {e}")
            raise ValueError(f"Failed to send message to Discord: {str(e)}")
    
    def send_video_notification(self, video):
        """Send a formatted video notification to Discord"""
        embed = {
            "title": video.title,
            "description": video.description[:500] + "..." if len(video.description) > 500 else video.description,
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
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info("Video notification sent to Discord successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
            raise ValueError(f"Failed to send notification to Discord: {str(e)}")
