
# YouTube Hub - Versión Android

## Requisitos para Compilar

Para compilar la aplicación Android necesitas:

1. **Sistema Linux** (Ubuntu 20.04+ recomendado) o WSL2 en Windows
2. **Python 3.8+**
3. **Java JDK 11**
4. **Android SDK** y **NDK**
5. **Buildozer**

## Instalación de Dependencias en Ubuntu/Debian

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Instalar Buildozer
pip3 install buildozer cython

# Instalar dependencias de Kivy
pip3 install kivy kivymd
```

## Compilar el APK

1. **Preparar el proyecto:**
   ```bash
   cd /ruta/a/tu/proyecto
   ```

2. **Dar permisos al script:**
   ```bash
   chmod +x build_apk.sh
   ```

3. **Ejecutar la compilación:**
   ```bash
   ./build_apk.sh
   ```

4. **El APK estará en:**
   ```
   bin/youtubehub-1.0-arm64-v8a-debug.apk
   ```

## Instalación en Android

1. Transfiere el APK a tu dispositivo Android
2. Habilita "Instalar apps de orígenes desconocidos" en Configuración
3. Instala el APK
4. Abre la app "YouTube Hub"

## Notas Importantes

- **Versión mínima:** Android 10 (API 29)
- **Permisos necesarios:** Internet, almacenamiento
- **Primera ejecución:** Configura tus API keys en la sección de Configuración

## Limitaciones de la App Móvil

- La automatización de grupos de Facebook puede no funcionar igual que en la versión web
- Algunas funciones pueden requerir adaptación adicional
- La base de datos SQLite es local al dispositivo

## Desarrollo y Testing

Para probar la app sin compilar APK:

```bash
python mobile_app.py
```

Esto abrirá una ventana de escritorio simulando la app móvil.

## Compilar para Release (Producción)

Para generar un APK firmado para publicar en Play Store:

```bash
buildozer android release
```

Necesitarás crear un keystore para firmar la aplicación.
