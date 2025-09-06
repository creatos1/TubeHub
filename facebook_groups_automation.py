
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class FacebookGroupsAutomation:
    """Automatiza las publicaciones en grupos de Facebook usando Selenium"""
    
    def __init__(self):
        logger.info("FacebookGroupsAutomation: Inicializando automatización de grupos")
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Configura el driver de Chrome"""
        logger.info("FacebookGroupsAutomation: Configurando Chrome WebDriver")
        
        chrome_options = Options()
        # Configuraciones esenciales para entornos como Replit
        chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # User agent para evitar detección
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("FacebookGroupsAutomation: Driver configurado exitosamente")
        except Exception as e:
            logger.error(f"FacebookGroupsAutomation: Error configurando driver: {e}")
            raise Exception(f"No se pudo configurar Chrome WebDriver: {e}")
        
    def login_facebook(self, email=None, password=None):
        """Inicia sesión en Facebook"""
        logger.info("FacebookGroupsAutomation: Iniciando sesión en Facebook")
        
        try:
            self.driver.get("https://www.facebook.com")
            time.sleep(3)
            
            # Buscar campos de login
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.driver.find_element(By.ID, "pass")
            
            if email and password:
                # Login automático con credenciales
                email_field.send_keys(email)
                password_field.send_keys(password)
                
                login_button = self.driver.find_element(By.NAME, "login")
                login_button.click()
                
                # Esperar a que se complete el login
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search']")))
                logger.info("FacebookGroupsAutomation: Login automático exitoso")
                
            else:
                # Login manual - esperar a que el usuario inicie sesión
                logger.info("FacebookGroupsAutomation: Esperando login manual del usuario")
                print("Por favor, inicia sesión manualmente en la ventana del navegador...")
                
                # Esperar hasta que aparezca el campo de búsqueda (indica login exitoso)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search']")))
                logger.info("FacebookGroupsAutomation: Login manual detectado")
                
            return True
            
        except Exception as e:
            logger.error(f"FacebookGroupsAutomation: Error en login: {e}")
            return False
    
    def post_to_group(self, group_url, message, link=None):
        """Publica en un grupo específico de Facebook"""
        logger.info(f"FacebookGroupsAutomation: Publicando en grupo: {group_url}")
        
        try:
            # Navegar al grupo
            self.driver.get(group_url)
            time.sleep(5)
            
            # Buscar el área de crear publicación
            post_box_selectors = [
                "[data-testid='status-attachment-mentions-input']",
                "[data-pagelet='FeedComposer']",
                "div[role='textbox'][data-testid]",
                "div[contenteditable='true']"
            ]
            
            post_box = None
            for selector in post_box_selectors:
                try:
                    post_box = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if not post_box:
                raise Exception("No se pudo encontrar el área de publicación")
            
            # Hacer clic en el área de publicación
            post_box.click()
            time.sleep(2)
            
            # Escribir el mensaje
            post_box.send_keys(message)
            time.sleep(2)
            
            # Si hay un enlace, agregarlo
            if link:
                post_box.send_keys(f"\n\n{link}")
                time.sleep(3)  # Esperar a que Facebook procese el enlace
            
            # Buscar y hacer clic en el botón de publicar
            publish_selectors = [
                "[data-testid='react-composer-post-button']",
                "div[aria-label='Publicar']",
                "div[aria-label='Post']",
                "button[type='submit']"
            ]
            
            publish_button = None
            for selector in publish_selectors:
                try:
                    publish_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if publish_button.is_enabled():
                        break
                except:
                    continue
            
            if publish_button:
                publish_button.click()
                time.sleep(5)
                logger.info("FacebookGroupsAutomation: Publicación enviada exitosamente")
                return True, "Publicación enviada exitosamente"
            else:
                logger.error("FacebookGroupsAutomation: No se encontró botón de publicar")
                return False, "No se pudo encontrar el botón de publicar"
                
        except Exception as e:
            logger.error(f"FacebookGroupsAutomation: Error publicando en grupo: {e}")
            return False, f"Error publicando: {str(e)}"
    
    def post_video_to_groups(self, video, group_urls):
        """Publica un video en múltiples grupos"""
        logger.info(f"FacebookGroupsAutomation: Publicando video en {len(group_urls)} grupos")
        
        # Crear mensaje formateado
        message = f"🎥 Nuevo video: {video.title}\n\n"
        
        if video.description:
            description = video.description[:300] + "..." if len(video.description) > 300 else video.description
            message += f"{description}\n\n"
        
        message += f"👁️ {video.view_count:,} visualizaciones\n"
        message += f"👍 {video.like_count:,} likes\n\n"
        message += f"¡Míralo aquí! 👇"
        
        results = []
        
        for group_url in group_urls:
            logger.info(f"FacebookGroupsAutomation: Publicando en: {group_url}")
            success, msg = self.post_to_group(group_url, message, video.youtube_url)
            results.append({
                'group_url': group_url,
                'success': success,
                'message': msg
            })
            
            # Pausa entre publicaciones para evitar ser detectado como spam
            time.sleep(10)
        
        return results
    
    def close_driver(self):
        """Cierra el navegador"""
        if self.driver:
            logger.info("FacebookGroupsAutomation: Cerrando navegador")
            self.driver.quit()
            self.driver = None
