
# YouTube Hub - Configuración Local

## Requisitos Previos

1. **Python 3.11 o superior** instalado en tu sistema
2. **Visual Studio Code** con la extensión de Python
3. **Google Chrome** instalado (para la automatización de Facebook)

## Instalación

1. **Clona o descarga** el proyecto en tu laptop

2. **Instala las dependencias** desde la terminal de VS Code:
   ```bash
   pip install flask flask-sqlalchemy requests selenium webdriver-manager werkzeug
   ```

3. **Configura las variables de entorno** (opcional):
   - Puedes crear un archivo `.env` para las API keys
   - O configurarlas directamente en la aplicación web

## Ejecución

1. **Abre** el proyecto en Visual Studio Code

2. **Ejecuta** el archivo principal desde la terminal integrada:
   ```bash
   python main.py
   ```

3. **Abre tu navegador** y ve a:
   ```
   http://127.0.0.1:5000
   ```

## Configuración Inicial

1. Ve a la página de **Configuración** (`/config`)
2. Configura tu **YouTube API Key**
3. Configura el **Discord Webhook** (opcional)
4. Configura las **credenciales de Facebook** (opcional)
5. Agrega **grupos de Facebook** para automatización (opcional)

## Funcionalidades

- ✅ **Agregar videos** de YouTube a tu colección
- ✅ **Ver detalles** completos de cada video
- ✅ **Enviar a Discord** via webhook
- ✅ **Enviar a Facebook** (página)
- ✅ **Automatización de grupos** de Facebook
- ✅ **Copiar mensajes** formateados

## Desarrollo

- El modo **debug** está habilitado por defecto
- Los cambios se recargan automáticamente
- Los logs aparecen en la terminal de VS Code
- La base de datos SQLite se crea automáticamente

## Notas

- Para la automatización de Facebook, Chrome se abrirá en modo visual
- Si quieres modo headless, descomenta la línea en `facebook_groups_automation.py`
- El proyecto funciona completamente offline excepto por las APIs externas
