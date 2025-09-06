from app import app

if __name__ == '__main__':
    # Para desarrollo local, usar localhost en lugar de 0.0.0.0
    # Si quieres que sea accesible desde otros dispositivos en tu red, cambia a '0.0.0.0'
    app.run(host='127.0.0.1', port=5000, debug=True)
