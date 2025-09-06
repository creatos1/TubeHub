import os
import requests
import re
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self):
        self.api_key = os.getenv('YT_API_KEY')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
    
    def extract_video_id(self, url):
        """Extract YouTube video ID from various URL formats"""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try parsing as query parameter
        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    return query_params['v'][0]
        except Exception as e:
            logger.error(f"Error parsing URL: {e}")
        
        return None
    
    def get_video_details(self, video_id):
        """Fetch video details from YouTube Data API"""
        if not self.api_key:
            raise ValueError("YouTube API key not found. Please set YT_API_KEY environment variable.")
        
        url = f"{self.base_url}/videos"
        params = {
            'key': self.api_key,
            'id': video_id,
            'part': 'snippet,statistics,contentDetails'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                raise ValueError("Video not found or is private/unavailable")
            
            video_data = data['items'][0]
            snippet = video_data['snippet']
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            
            return {
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'published_at': snippet['publishedAt'],
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0))
            }
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise ValueError(f"Failed to fetch video data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ValueError(f"Error processing video data: {str(e)}")
