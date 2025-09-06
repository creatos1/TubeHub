import requests
import logging
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FacebookAPI:
    """Maneja las publicaciones en grupos de Facebook"""
    
    def __init__(self):
        logger.info("FacebookAPI: Inicializando clase FacebookAPI")
        self.access_token = ConfigManager.get_config('FB_ACCESS_TOKEN')
        self.group_id = ConfigManager.get_config('FB_GROUP_ID')
        self.base_url = 'https://graph.facebook.com/v18.0'
        logger.info(f"FacebookAPI: Token {'configurado' if self.access_token else 'no encontrado'}")
        logger.info(f"FacebookAPI: Group ID {'configurado' if self.group_id else 'no encontrado'}")
    
    def post_to_group(self, message, link=None):
        """Publica un mensaje en el grupo de Facebook"""
        logger.info("FacebookAPI: Iniciando publicación en grupo de Facebook")
        
        # Refresh credentials from database
        self.access_token = ConfigManager.get_config('FB_ACCESS_TOKEN')
        group_input = ConfigManager.get_config('FB_GROUP_ID')
        
        if not self.access_token:
            logger.error("FacebookAPI: Access token no configurado")
            raise ValueError("Facebook access token no configurado. Configúralo en la página de Configuración.")
        
        if not group_input:
            logger.error("FacebookAPI: Group ID no configurado")
            raise ValueError("Facebook Group ID no configurado. Configúralo en la página de Configuración.")
        
        # Extraer el Group ID correcto
        self.group_id = self.extract_group_id(group_input)
        
        url = f"{self.base_url}/{self.group_id}/feed"
        
        payload = {
            'message': message,
            'access_token': self.access_token
        }
        
        if link:
            payload['link'] = link
            logger.info(f"FacebookAPI: Incluyendo enlace en la publicación: {link}")
        
        logger.info(f"FacebookAPI: Publicando en grupo {self.group_id}")
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
        
        return self.post_to_group(message, video.youtube_url)
    
    @staticmethod
    def extract_group_id(group_input):
        """Extrae el ID numérico del grupo desde una URL o ID directo"""
        logger.info(f"FacebookAPI: Extrayendo Group ID de: {group_input}")
        
        # Si ya es un ID numérico, devolverlo
        if group_input.isdigit():
            logger.info(f"FacebookAPI: ID numérico detectado: {group_input}")
            return group_input
        
        # Intentar extraer de URLs de Facebook
        import re
        patterns = [
            r'facebook\.com/groups/(\d+)',
            r'facebook\.com/groups/(\w+)',
            r'/groups/(\d+)',
            r'/groups/(\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, group_input)
            if match:
                extracted_id = match.group(1)
                logger.info(f"FacebookAPI: ID extraído de URL: {extracted_id}")
                return extracted_id
        
        # Si no se puede extraer, devolver el input original
        logger.warning(f"FacebookAPI: No se pudo extraer ID, usando input original: {group_input}")
        return group_input

    @staticmethod
    def test_facebook_credentials(access_token, group_input):
        """Prueba las credenciales de Facebook"""
        logger.info("FacebookAPI: Probando credenciales de Facebook")
        
        # Extraer el Group ID correcto
        group_id = FacebookAPI.extract_group_id(group_input)
        
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
            
            # Verificar acceso al grupo
            group_url = f"https://graph.facebook.com/v18.0/{group_id}"
            group_params = {
                'access_token': access_token,
                'fields': 'name,privacy'
            }
            
            logger.info(f"FacebookAPI: Consultando grupo con ID: {group_id}")
            group_response = requests.get(group_url, params=group_params, timeout=10)
            logger.info(f"FacebookAPI: Verificación de grupo - HTTP {group_response.status_code}")
            
            if group_response.status_code == 200:
                group_data = group_response.json()
                group_name = group_data.get('name', 'Grupo')
                logger.info(f"FacebookAPI: Acceso al grupo confirmado: {group_name}")
                return True, f"Credenciales válidas. Usuario: {user_name}, Grupo: {group_name}"
            else:
                error_data = group_response.json() if group_response.headers.get('content-type', '').startswith('application/json') else {}
                error_message = error_data.get('error', {}).get('message', 'No se puede acceder al grupo')
                logger.error(f"FacebookAPI: Error accediendo al grupo: {error_message}")
                
                # Sugerir usar solo el ID numérico si detectamos una URL
                if 'facebook.com' in group_input:
                    return False, f"Error: Usa solo el ID numérico del grupo (ej: {group_id}), no la URL completa"
                else:
                    return False, f"Error accediendo al grupo: {error_message}"
                
        except requests.RequestException as e:
            logger.error(f"FacebookAPI: Error de conexión: {e}")
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            logger.error(f"FacebookAPI: Error inesperado: {e}")
            return False, f"Error inesperado: {str(e)}"