
import os
os.environ['KIVY_NO_ARGS'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivy.core.window import Window
from kivy.metrics import dp

# Importar módulos del sistema existente
from youtube_api import YouTubeAPI
from discord_webhook import DiscordWebhook
from facebook_api import FacebookAPI
from config_manager import ConfigManager
from app import db
from models import Video

class VideoCard(MDCard):
    def __init__(self, video, **kwargs):
        super().__init__(**kwargs)
        self.video = video
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(10)
        self.spacing = dp(10)
        
        # Título
        title_label = Label(
            text=video.title,
            size_hint_y=None,
            height=dp(40),
            font_size='16sp',
            bold=True
        )
        
        # Estadísticas
        stats_label = Label(
            text=f"👁️ {video.view_count:,} | 👍 {video.like_count:,}",
            size_hint_y=None,
            height=dp(30),
            font_size='14sp'
        )
        
        # Botones
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        
        discord_btn = MDRaisedButton(
            text="Discord",
            on_release=lambda x: self.send_to_discord()
        )
        
        facebook_btn = MDRaisedButton(
            text="Facebook",
            on_release=lambda x: self.send_to_facebook()
        )
        
        delete_btn = MDFlatButton(
            text="Eliminar",
            on_release=lambda x: self.delete_video()
        )
        
        buttons_layout.add_widget(discord_btn)
        buttons_layout.add_widget(facebook_btn)
        buttons_layout.add_widget(delete_btn)
        
        self.add_widget(title_label)
        self.add_widget(stats_label)
        self.add_widget(buttons_layout)
    
    def send_to_discord(self):
        try:
            discord_webhook = DiscordWebhook()
            discord_webhook.send_video_notification(self.video)
            MDApp.get_running_app().show_message("Enviado a Discord exitosamente")
        except Exception as e:
            MDApp.get_running_app().show_message(f"Error: {str(e)}")
    
    def send_to_facebook(self):
        try:
            facebook_api = FacebookAPI()
            is_success, message = facebook_api.post_video_notification(self.video)
            MDApp.get_running_app().show_message(message)
        except Exception as e:
            MDApp.get_running_app().show_message(f"Error: {str(e)}")
    
    def delete_video(self):
        MDApp.get_running_app().confirm_delete(self.video)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(title="YouTube Hub")
        layout.add_widget(toolbar)
        
        # Lista de videos
        self.scroll = ScrollView()
        self.videos_layout = GridLayout(cols=1, spacing=dp(10), padding=dp(10), size_hint_y=None)
        self.videos_layout.bind(minimum_height=self.videos_layout.setter('height'))
        
        self.scroll.add_widget(self.videos_layout)
        layout.add_widget(self.scroll)
        
        # Botones de navegación
        nav_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5), padding=dp(5))
        
        add_btn = MDRaisedButton(
            text="Agregar Video",
            on_release=lambda x: self.go_to_add_video()
        )
        
        config_btn = MDRaisedButton(
            text="Configuración",
            on_release=lambda x: self.go_to_config()
        )
        
        refresh_btn = MDRaisedButton(
            text="Actualizar",
            on_release=lambda x: self.load_videos()
        )
        
        nav_layout.add_widget(add_btn)
        nav_layout.add_widget(config_btn)
        nav_layout.add_widget(refresh_btn)
        
        layout.add_widget(nav_layout)
        self.add_widget(layout)
        
        self.load_videos()
    
    def load_videos(self):
        self.videos_layout.clear_widgets()
        videos = Video.query.order_by(Video.added_at.desc()).all()
        
        if not videos:
            no_videos = Label(text="No hay videos guardados", size_hint_y=None, height=dp(50))
            self.videos_layout.add_widget(no_videos)
        else:
            for video in videos:
                card = VideoCard(video)
                self.videos_layout.add_widget(card)
    
    def go_to_add_video(self):
        self.manager.current = 'add_video'
    
    def go_to_config(self):
        self.manager.current = 'config'

class AddVideoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Agregar Video",
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        # Campo de URL
        self.url_field = MDTextField(
            hint_text="URL de YouTube",
            multiline=False,
            size_hint_y=None,
            height=dp(60)
        )
        
        # Botón agregar
        add_btn = MDRaisedButton(
            text="Agregar Video",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: self.add_video()
        )
        
        layout.add_widget(Label(size_hint_y=0.3))
        layout.add_widget(self.url_field)
        layout.add_widget(add_btn)
        layout.add_widget(Label(size_hint_y=0.5))
        
        self.add_widget(layout)
    
    def add_video(self):
        url = self.url_field.text.strip()
        
        if not url:
            MDApp.get_running_app().show_message("Por favor ingresa una URL")
            return
        
        try:
            youtube_api = YouTubeAPI()
            video_id = youtube_api.extract_video_id(url)
            
            if not video_id:
                MDApp.get_running_app().show_message("URL inválida")
                return
            
            # Verificar si existe
            existing = Video.query.filter_by(youtube_id=video_id).first()
            if existing:
                MDApp.get_running_app().show_message("El video ya existe")
                return
            
            # Obtener detalles
            details = youtube_api.get_video_details(video_id)
            
            from datetime import datetime
            published_at = None
            if details.get('published_at'):
                try:
                    published_at = datetime.fromisoformat(details['published_at'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Crear video
            video = Video(
                youtube_id=video_id,
                title=details['title'],
                description=details['description'],
                thumbnail_url=details['thumbnail_url'],
                duration=details['duration'],
                view_count=details['view_count'],
                like_count=details['like_count'],
                published_at=published_at
            )
            
            db.session.add(video)
            db.session.commit()
            
            MDApp.get_running_app().show_message("Video agregado exitosamente")
            self.url_field.text = ""
            self.go_back()
            
        except Exception as e:
            MDApp.get_running_app().show_message(f"Error: {str(e)}")
    
    def go_back(self):
        self.manager.current = 'home'
        home_screen = self.manager.get_screen('home')
        home_screen.load_videos()

class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Configuración",
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        layout.add_widget(toolbar)
        
        scroll = ScrollView()
        config_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, padding=dp(10))
        config_layout.bind(minimum_height=config_layout.setter('height'))
        
        # YouTube API
        config_layout.add_widget(Label(text="YouTube API Key", size_hint_y=None, height=dp(30), bold=True))
        self.yt_field = MDTextField(hint_text="Ingresa tu API Key", multiline=False, size_hint_y=None, height=dp(60))
        save_yt_btn = MDRaisedButton(text="Guardar YouTube API", size_hint_y=None, height=dp(50), on_release=lambda x: self.save_youtube())
        
        config_layout.add_widget(self.yt_field)
        config_layout.add_widget(save_yt_btn)
        
        # Discord
        config_layout.add_widget(Label(text="Discord Webhook", size_hint_y=None, height=dp(30), bold=True))
        self.discord_field = MDTextField(hint_text="URL del Webhook", multiline=False, size_hint_y=None, height=dp(60))
        save_discord_btn = MDRaisedButton(text="Guardar Discord", size_hint_y=None, height=dp(50), on_release=lambda x: self.save_discord())
        
        config_layout.add_widget(self.discord_field)
        config_layout.add_widget(save_discord_btn)
        
        # Facebook
        config_layout.add_widget(Label(text="Facebook", size_hint_y=None, height=dp(30), bold=True))
        self.fb_token_field = MDTextField(hint_text="Access Token", multiline=False, size_hint_y=None, height=dp(60))
        self.fb_page_field = MDTextField(hint_text="Page ID", multiline=False, size_hint_y=None, height=dp(60))
        save_fb_btn = MDRaisedButton(text="Guardar Facebook", size_hint_y=None, height=dp(50), on_release=lambda x: self.save_facebook())
        
        config_layout.add_widget(self.fb_token_field)
        config_layout.add_widget(self.fb_page_field)
        config_layout.add_widget(save_fb_btn)
        
        scroll.add_widget(config_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_config()
    
    def load_config(self):
        yt_key = ConfigManager.get_config('YT_API_KEY')
        if yt_key:
            self.yt_field.text = yt_key
        
        discord = ConfigManager.get_config('DISCORD_WEBHOOK')
        if discord:
            self.discord_field.text = discord
        
        fb_token = ConfigManager.get_config('FB_ACCESS_TOKEN')
        if fb_token:
            self.fb_token_field.text = fb_token
        
        fb_page = ConfigManager.get_config('FB_PAGE_ID')
        if fb_page:
            self.fb_page_field.text = fb_page
    
    def save_youtube(self):
        api_key = self.yt_field.text.strip()
        if api_key:
            ConfigManager.set_config('YT_API_KEY', api_key)
            MDApp.get_running_app().show_message("YouTube API guardada")
    
    def save_discord(self):
        webhook = self.discord_field.text.strip()
        if webhook:
            ConfigManager.set_config('DISCORD_WEBHOOK', webhook)
            MDApp.get_running_app().show_message("Discord webhook guardado")
    
    def save_facebook(self):
        token = self.fb_token_field.text.strip()
        page_id = self.fb_page_field.text.strip()
        if token and page_id:
            ConfigManager.set_config('FB_ACCESS_TOKEN', token)
            ConfigManager.set_config('FB_PAGE_ID', page_id)
            MDApp.get_running_app().show_message("Facebook configurado")
    
    def go_back(self):
        self.manager.current = 'home'

class YouTubeHubApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        
        # Inicializar base de datos
        from app import app as flask_app
        with flask_app.app_context():
            db.create_all()
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(AddVideoScreen(name='add_video'))
        sm.add_widget(ConfigScreen(name='config'))
        
        return sm
    
    def show_message(self, message):
        if self.dialog:
            self.dialog.dismiss()
        
        self.dialog = MDDialog(
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()
    
    def confirm_delete(self, video):
        self.dialog = MDDialog(
            text=f"¿Eliminar '{video.title}'?",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar",
                    on_release=lambda x: self.delete_video_confirmed(video)
                )
            ]
        )
        self.dialog.open()
    
    def delete_video_confirmed(self, video):
        try:
            db.session.delete(video)
            db.session.commit()
            self.dialog.dismiss()
            self.show_message("Video eliminado")
            
            # Actualizar lista
            home_screen = self.root.get_screen('home')
            home_screen.load_videos()
        except Exception as e:
            self.show_message(f"Error: {str(e)}")

if __name__ == '__main__':
    YouTubeHubApp().run()
