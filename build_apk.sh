
#!/bin/bash

# Este script compila la aplicación Android
echo "Iniciando compilación de APK..."

# Instalar buildozer si no está instalado
pip install buildozer

# Limpiar builds anteriores
buildozer android clean

# Compilar APK
buildozer -v android debug

echo "Compilación completada. El APK estará en bin/"
