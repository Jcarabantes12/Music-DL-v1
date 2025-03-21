import os
import json
import hashlib
import winreg

# Extrae el aspecto de la pantalla del usuario seleccionada
def nightMode():
    # Windows
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"SOFTWARE/Microsoft/Windows/CurrentVersion/Themes/Personalize")
        value, regtype = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)

        if value == 1:
            return "Light"
        else:
            return "Dark"
    except:
        return "Dark"

# Extrae la ruta del perfil del usuario para crear la carpeta de la aplicación
def userProfile():
    # Windows
    return os.getenv("USERPROFILE")

# Se establece la configuración por defecto de la aplicación
def defaultConfig():
    # Nombre de la aplicación
    app_name = "Music-DL"

    style_css = r"app/gui/styles/main.css"

    # Version de la aplicación
    version = "v0.5.0"


    # Icono de la aplicación
    app_icon = r"app/resources/icons/app.png"
    # Icono del boton agregar a la cola
    addLine_icon = r"app/resources/icons/add.png"
    # Icono de imagen no disponible
    no_image = r"app/resources/icons/no_image.png"

    ffmpeg_path = r"app/resources/bin/ffmpeg.exe"

    # Dimenciones de la ventana
    window_dimensions = "Maximized"


    # Generos musicales
    # Si se desea añadir un genero se agrega aqui y luego se carga la interfaz, para que lo lea
    genres = [
        "Dubstep",
        "Rock",
        "Rock Alternativo",
        "Heavy Metal",
        "Reguetón",
        "Trap",
        "Ranchera",
        "Pop",
        "Balada",
        "Hip Hop Romantico",
        "Pop Rock",
        "Electro House",
        "Hip Hop",
        "Jazz",
        "Rap",
        "Italo Disco",
        "Blues",
        "Rock And Roll",
        "R&B",
        "Rock En Español",
        "Hard Rock"
    ]

    # Formatos del album
    formats = [
        "flac"
    ]

    # Aspecto de pantalla del usuario
    night_mode = nightMode()

    # Ruta de la carpeta personal del usuario
    # Para crear la carpeta de la aplicación
    user_profile = userProfile().replace("\\", "/")

    # Ruta de la carpeta de la aplicación
    # Una carpeta unica para la aplicación y todo lo que se crea se añadira aqui
    music_dl_app = os.path.join(user_profile, app_name).replace("\\", "/")
    # Se crea la carpeta de la aplicación si no existe
    if not os.path.exists(music_dl_app):
        os.makedirs(music_dl_app)

    # Ruta de la carpeta temporal
    # Estara los archivo temporales como el cover, json de la url, json del album, etc.
    # Que se eliminaran
    music_dl_app__temp = os.path.join(music_dl_app, "Temp").replace("\\", "/")
    # Se crea la carpeta Temp si no existe
    if not os.path.exists(music_dl_app__temp):
        os.makedirs(music_dl_app__temp)

    # Ruta de la carpeta de configuración
    # Estara la configuración que le usuario a modificado en formato json
    music_dl_app__resources = os.path.join(music_dl_app, "Resources").replace("\\", "/")
    music_dl_app__config = os.path.join(music_dl_app, "Config").replace("\\", "/")
    # Se crea la carpeta Resources si no existen
    if not os.path.exists(music_dl_app__resources):
        os.makedirs(music_dl_app__resources)
    # Se crea la carpeta Config si no existen
    if not os.path.exists(music_dl_app__config):
        os.makedirs(music_dl_app__config)
    
    # Ruta de la carpeta de salida
    # Todas las descargas apareceran aqui
    music_dl_app__output = os.path.join(music_dl_app, "Output").replace("\\", "/")
    # Se crea la carpeta de salida si no existe
    if not os.path.exists(music_dl_app__output):
        os.makedirs(music_dl_app__output)

    json_config = {
        "app_name": app_name,
        "style_css" : style_css,
        "app_version": version,
        "icons": {
            "app_icon": app_icon,
            "addLine_icon": addLine_icon,
            "noImage_icon": no_image
        },
        "ffmpeg_path": ffmpeg_path,
        "window_dimensions": window_dimensions,
        "night_mode": night_mode,
        "app_dir": music_dl_app,
        "app_config": music_dl_app__config,
        "app_temp": music_dl_app__temp,
        "app_output": music_dl_app__output,
        "Genres": genres,
        "Formats": formats
    }

    with open(fr"{music_dl_app__config}/app_config.json", "w", encoding="utf-8") as load_app_config:
        json.dump(json_config, load_app_config, indent=4)

    return fr"{music_dl_app__config}/app_config.json"
