import requests
import logging
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FacebookAPI:
    """Maneja las publicaciones en páginas de Facebook"""
    
    def __init__(self):
        logger.info("FacebookAPI: Inicializando clase FacebookAPI")
        self.access_token = ConfigManager.get_config('FB_ACCESS_TOKEN')
        self.page_id = ConfigManager.get_config('FB_PAGE_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'
        logger.info(f"FacebookAPI: Token {'configurado' if self.access_token else 'no encontrado'}")
        logger.info(f"FacebookAPI: Page ID {'configurado' if self.page_id else 'no encontrado'}")
    
    def post_to_page(self, message, link=None):
        """Publica un mensaje en la página de Facebook"""
        logger.info("FacebookAPI: Iniciando publicación en página de Facebook")
        
        # Refresh credentials from database
        self.access_token = ConfigManager.get_config('FB_ACCESS_TOKEN')
        page_input = ConfigManager.get_config('FB_PAGE_ID')
        
        if not self.access_token:
            logger.error("FacebookAPI: Access token no configurado")
            raise ValueError("Facebook access token no configurado. Configúralo en la página de Configuración.")
        
        if not page_input:
            logger.error("FacebookAPI: Page ID no configurado")
            raise ValueError("Facebook Page ID no configurado. Configúralo en la página de Configuración.")
        
        # Extraer el Page ID correcto
        self.page_id = self.extract_page_id(page_input)
        
        # Primero obtener el Page Access Token
        page_token = self.get_page_access_token(self.page_id)
        
        url = f"{self.base_url}/{self.page_id}/feed"
        
        payload = {
            'message': message,
            'access_token': page_token
        }
        
        if link:
            payload['link'] = link
            logger.info(f"FacebookAPI: Incluyendo enlace en la publicación: {link}")
        
        logger.info(f"FacebookAPI: Publicando en página {self.page_id}")
        logger.debug(f"FacebookAPI: Mensaje: {len(message)} caracteres")
        
        try:
            response = requests.post(url, data=payload, timeout=30)
            logger.info(f"FacebookAPI: Respuesta HTTP: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data:
                    logger.info(f"FacebookAPI: Publicación exitosa, ID: {data['id']}")
                    return True, f"Publicación exitosa (ID: {data['id']})"
                else:
                    logger.warning("FacebookAPI: Respuesta sin ID de publicación")
                    return False, "Respuesta inesperada de Facebook API"
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': {'message': response.text}}
                error_message = error_data.get('error', {}).get('message', 'Error desconocido')
                logger.error(f"FacebookAPI: Error HTTP {response.status_code}: {error_message}")
                return False, f"Error al publicar: {error_message}"
                
        except requests.RequestException as e:
            logger.error(f"FacebookAPI: Error de conexión: {e}")
            raise ValueError(f"Error de conexión con Facebook: {str(e)}")
        except Exception as e:
            logger.error(f"FacebookAPI: Error inesperado: {e}")
            raise ValueError(f"Error inesperado: {str(e)}")
    
    def post_video_notification(self, video):
        """Publica una notificación de video en Facebook"""
        logger.info(f"FacebookAPI: Publicando notificación de video: {video.title}")
        
        # Crear mensaje formateado para Facebook
        message = f"🎥 Nuevo video: {video.title}\n\n"
        
        # Agregar descripción limitada
        if video.description:
            description = video.description[:300] + "..." if len(video.description) > 300 else video.description
            message += f"{description}\n\n"
        
        # Agregar estadísticas
        message += f"👁️ {video.view_count:,} visualizaciones\n"
        message += f"👍 {video.like_count:,} likes\n\n"
        message += f"¡Míralo aquí! 👇"
        
        logger.info(f"FacebookAPI: Mensaje preparado: {len(message)} caracteres")
        
        return self.post_to_page(message, video.youtube_url)
    
    @staticmethod
    def extract_page_id(page_input):
        """Extrae el ID de la página desde una URL o ID directo"""
        logger.info(f"FacebookAPI: Extrayendo Page ID de: {page_input}")
        
        # Si ya es un ID numérico, devolverlo
        if page_input.isdigit():
            logger.info(f"FacebookAPI: ID numérico detectado: {page_input}")
            return page_input
        
        # Intentar extraer de URLs de Facebook
        import re
        patterns = [
            r'facebook\.com/(\w+)',
            r'facebook\.com/pages/[\w\-]+/(\d+)',
            r'facebook\.com/profile\.php\?id=(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_input)
            if match:
                extracted_id = match.group(1)
                logger.info(f"FacebookAPI: ID extraído de URL: {extracted_id}")
                return extracted_id
        
        # Si no se puede extraer, devolver el input original
        logger.warning(f"FacebookAPI: No se pudo extraer ID, usando input original: {page_input}")
        return page_input
    
    def get_page_access_token(self, page_id):
        """Obtiene el Page Access Token necesario para publicar en la página"""
        logger.info(f"FacebookAPI: Obteniendo Page Access Token para página {page_id}")
        
        url = f"{self.base_url}/me/accounts"
        params = {
            'access_token': self.access_token,
            'fields': 'access_token,id,name'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"FacebookAPI: Respuesta de páginas - HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get('data', [])
                
                for page in pages:
                    if page['id'] == page_id:
                        page_token = page['access_token']
                        page_name = page['name']
                        logger.info(f"FacebookAPI: Page Access Token obtenido para: {page_name}")
                        return page_token
                
                logger.error(f"FacebookAPI: Página {page_id} no encontrada en las páginas administradas")
                raise ValueError(f"No tienes permisos para administrar la página {page_id}")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', 'Error obteniendo páginas')
                logger.error(f"FacebookAPI: Error obteniendo páginas: {error_message}")
                raise ValueError(f"Error obteniendo páginas: {error_message}")
                
        except requests.RequestException as e:
            logger.error(f"FacebookAPI: Error de conexión obteniendo pages: {e}")
            raise ValueError(f"Error de conexión: {str(e)}")

    @staticmethod
    def test_facebook_credentials(access_token, page_input):
        """Prueba las credenciales de Facebook"""
        logger.info("FacebookAPI: Probando credenciales de Facebook")
        
        # Extraer el Page ID correcto
        page_id = FacebookAPI.extract_page_id(page_input)
        
        try:
            # Primero verificar que el token sea válido
            url = "https://graph.facebook.com/v18.0/me"
            params = {'access_token': access_token}
            
            response = requests.get(url, params=params, timeout=10)
            logger.info(f"FacebookAPI: Verificación de token - HTTP {response.status_code}")
            
            if response.status_code != 200:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', 'Token inválido')
                logger.error(f"FacebookAPI: Token inválido: {error_message}")
                return False, f"Token inválido: {error_message}"
            
            user_data = response.json()
            user_name = user_data.get('name', 'Usuario')
            logger.info(f"FacebookAPI: Token válido para usuario: {user_name}")
            
            # Verificar acceso a las páginas administradas
            pages_url = "https://graph.facebook.com/v18.0/me/accounts"
            pages_params = {
                'access_token': access_token,
                'fields': 'id,name,access_token'
            }
            
            logger.info("FacebookAPI: Consultando páginas administradas")
            pages_response = requests.get(pages_url, params=pages_params, timeout=10)
            logger.info(f"FacebookAPI: Verificación de páginas - HTTP {pages_response.status_code}")
            
            if pages_response.status_code == 200:
                pages_data = pages_response.json()
                pages = pages_data.get('data', [])
                
                # Buscar la página específica
                target_page = None
                for page in pages:
                    if page['id'] == page_id or page['name'].lower() == page_id.lower():
                        target_page = page
                        break
                
                if target_page:
                    page_name = target_page['name']
                    logger.info(f"FacebookAPI: Acceso a la página confirmado: {page_name}")
                    return True, f"Credenciales válidas. Usuario: {user_name}, Página: {page_name}"
                else:
                    available_pages = [f"{p['name']} (ID: {p['id']})" for p in pages[:3]]
                    logger.warning(f"FacebookAPI: Página {page_id} no encontrada")
                    if pages:
                        return False, f"Página '{page_id}' no encontrada. Páginas disponibles: {', '.join(available_pages)}"
                    else:
                        return False, "No tienes páginas de Facebook administradas. Crea una página primero."
            else:
                error_data = pages_response.json() if pages_response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', 'No se puede acceder a las páginas')
                logger.error(f"FacebookAPI: Error accediendo a páginas: {error_message}")
                return False, f"Error accediendo a páginas: {error_message}"
                
        except requests.RequestException as e:
            logger.error(f"FacebookAPI: Error de conexión: {e}")
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            logger.error(f"FacebookAPI: Error inesperado: {e}")
            return False, f"Error inesperado: {str(e)}"