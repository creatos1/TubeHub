import requests
import re
import logging
from urllib.parse import urlparse, parse_qs
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self):
        logger.info("YouTubeAPI: Inicializando clase YouTubeAPI")
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.api_key = ConfigManager.get_config('YT_API_KEY')
        logger.info(f"YouTubeAPI: API key {'configurada' if self.api_key else 'no encontrada'}")
    
    def extract_video_id(self, url):
        """Extract YouTube video ID from various URL formats"""
        logger.info(f"YouTubeAPI: Extrayendo video ID de URL: {url}")
        
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            logger.debug(f"YouTubeAPI: Probando patrón: {pattern}")
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"YouTubeAPI: Video ID extraído exitosamente: {video_id}")
                return video_id
        
        # Try parsing as query parameter
        try:
            logger.debug("YouTubeAPI: Intentando extraer usando urlparse")
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    logger.info(f"YouTubeAPI: Video ID extraído por query param: {video_id}")
                    return video_id
        except Exception as e:
            logger.error(f"YouTubeAPI: Error al procesar URL: {e}")
        
        logger.warning(f"YouTubeAPI: No se pudo extraer video ID de la URL: {url}")
        return None
    
    def get_video_details(self, video_id):
        """Fetch video details from YouTube Data API"""
        logger.info(f"YouTubeAPI: Obteniendo detalles del video: {video_id}")
        
        # Refresh API key from database
        self.api_key = ConfigManager.get_config('YT_API_KEY')
        
        if not self.api_key:
            logger.error("YouTubeAPI: API key no configurada")
            raise ValueError("YouTube API key no configurada. Configúrala en la página de Configuración.")
        
        url = f"{self.base_url}/videos"
        params = {
            'key': self.api_key,
            'id': video_id,
            'part': 'snippet,statistics,contentDetails'
        }
        
        logger.info(f"YouTubeAPI: Realizando petición a: {url}")
        logger.debug(f"YouTubeAPI: Parámetros: {params}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            logger.info(f"YouTubeAPI: Respuesta HTTP: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"YouTubeAPI: Datos recibidos: {len(str(data))} caracteres")
            
            if not data.get('items'):
                logger.warning(f"YouTubeAPI: No se encontraron datos para video {video_id}")
                raise ValueError("Video no encontrado o es privado/no disponible")
            
            video_data = data['items'][0]
            snippet = video_data['snippet']
            statistics = video_data.get('statistics', {})
            content_details = video_data.get('contentDetails', {})
            
            logger.info(f"YouTubeAPI: Video encontrado: {snippet['title']}")
            logger.info(f"YouTubeAPI: Vistas: {statistics.get('viewCount', 0)}, Likes: {statistics.get('likeCount', 0)}")
            
            result = {
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail_url': snippet['thumbnails']['high']['url'],
                'published_at': snippet['publishedAt'],
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0))
            }
            
            logger.info("YouTubeAPI: Detalles del video obtenidos exitosamente")
            return result
            
        except requests.RequestException as e:
            logger.error(f"YouTubeAPI: Error en petición HTTP: {e}")
            raise ValueError(f"Error al conectar con YouTube API: {str(e)}")
        except Exception as e:
            logger.error(f"YouTubeAPI: Error inesperado: {e}")
            raise ValueError(f"Error al procesar datos del video: {str(e)}")
