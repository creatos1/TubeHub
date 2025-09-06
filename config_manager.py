import logging
from models import Config
from app import db

logger = logging.getLogger(__name__)

class ConfigManager:
    """Maneja las configuraciones de la aplicación"""
    
    @staticmethod
    def get_config(key_name):
        """Obtiene una configuración de la base de datos"""
        try:
            logger.info(f"ConfigManager: Buscando configuración para {key_name}")
            config = Config.query.filter_by(key_name=key_name).first()
            if config:
                logger.info(f"ConfigManager: Configuración {key_name} encontrada")
                return config.key_value
            else:
                logger.warning(f"ConfigManager: Configuración {key_name} no encontrada")
                return None
        except Exception as e:
            logger.error(f"ConfigManager: Error al obtener configuración {key_name}: {e}")
            return None
    
    @staticmethod
    def set_config(key_name, key_value):
        """Establece una configuración en la base de datos"""
        try:
            logger.info(f"ConfigManager: Estableciendo configuración {key_name}")
            config = Config.query.filter_by(key_name=key_name).first()
            
            if config:
                config.key_value = key_value
                logger.info(f"ConfigManager: Actualizando configuración existente {key_name}")
            else:
                config = Config(key_name=key_name, key_value=key_value)
                db.session.add(config)
                logger.info(f"ConfigManager: Creando nueva configuración {key_name}")
            
            db.session.commit()
            logger.info(f"ConfigManager: Configuración {key_name} guardada exitosamente")
            return True
        except Exception as e:
            logger.error(f"ConfigManager: Error al guardar configuración {key_name}: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def test_youtube_api(api_key):
        """Prueba si la API key de YouTube es válida"""
        try:
            logger.info("ConfigManager: Probando API key de YouTube")
            import requests
            
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'key': api_key,
                'id': 'dQw4w9WgXcQ',  # Never Gonna Give You Up - video público conocido
                'part': 'snippet'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    logger.info("ConfigManager: API key de YouTube es válida")
                    return True, "API key válida"
                else:
                    logger.warning("ConfigManager: API key de YouTube no retorna datos")
                    return False, "API key no retorna datos válidos"
            elif response.status_code == 403:
                logger.error("ConfigManager: API key de YouTube inválida o sin permisos")
                return False, "API key inválida o sin permisos"
            else:
                logger.error(f"ConfigManager: Error HTTP {response.status_code} al probar YouTube API")
                return False, f"Error HTTP: {response.status_code}"
                
        except Exception as e:
            logger.error(f"ConfigManager: Error al probar YouTube API: {e}")
            return False, f"Error de conexión: {str(e)}"
    
    @staticmethod
    def test_discord_webhook(webhook_url):
        """Prueba si el webhook de Discord es válido"""
        try:
            logger.info("ConfigManager: Probando webhook de Discord")
            import requests
            
            test_payload = {
                'content': '🧪 Test de conexión desde YouTube Hub - Esta es una prueba automática',
                'username': 'YouTube Hub Test'
            }
            
            response = requests.post(webhook_url, json=test_payload, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("ConfigManager: Webhook de Discord es válido")
                return True, "Webhook válido - mensaje de prueba enviado"
            else:
                logger.error(f"ConfigManager: Webhook inválido, código {response.status_code}")
                return False, f"Webhook inválido (código {response.status_code})"
                
        except Exception as e:
            logger.error(f"ConfigManager: Error al probar Discord webhook: {e}")
            return False, f"Error de conexión: {str(e)}"
    
    @staticmethod
    def test_facebook_credentials(access_token, page_id):
        """Prueba las credenciales de Facebook"""
        try:
            logger.info("ConfigManager: Probando credenciales de Facebook")
            from facebook_api import FacebookAPI
            
            return FacebookAPI.test_facebook_credentials(access_token, page_id)
            
        except Exception as e:
            logger.error(f"ConfigManager: Error al probar Facebook credentials: {e}")
            return False, f"Error al probar credenciales: {str(e)}"
    
    @staticmethod
    def get_facebook_groups():
        """Obtiene la lista de grupos de Facebook configurados"""
        try:
            logger.info("ConfigManager: Obteniendo lista de grupos de Facebook")
            groups_config = ConfigManager.get_config('FB_GROUPS')
            if groups_config:
                # Los grupos se guardan como URLs separadas por comas
                groups = [url.strip() for url in groups_config.split(',') if url.strip()]
                logger.info(f"ConfigManager: Encontrados {len(groups)} grupos configurados")
                return groups
            else:
                logger.warning("ConfigManager: No hay grupos configurados")
                return []
        except Exception as e:
            logger.error(f"ConfigManager: Error obteniendo grupos: {e}")
            return []
    
    @staticmethod
    def set_facebook_groups(group_urls):
        """Establece la lista de grupos de Facebook"""
        try:
            logger.info(f"ConfigManager: Guardando {len(group_urls)} grupos de Facebook")
            groups_str = ','.join(group_urls)
            return ConfigManager.set_config('FB_GROUPS', groups_str)
        except Exception as e:
            logger.error(f"ConfigManager: Error guardando grupos: {e}")
            return False
    
    @staticmethod
    def get_facebook_credentials():
        """Obtiene las credenciales de login de Facebook"""
        try:
            email = ConfigManager.get_config('FB_EMAIL')
            password = ConfigManager.get_config('FB_PASSWORD')
            return email, password
        except Exception as e:
            logger.error(f"ConfigManager: Error obteniendo credenciales de login: {e}")
            return None, None