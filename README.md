# Music-DL

Music-DL es una aplicación de escritorio que permite descargar música desde YouTube Music y convertirla automáticamente a formato FLAC con metadatos.

## Características

- Interfaz gráfica intuitiva construida con PyQt6
- Descarga de álbumes completos desde YouTube Music 
- Conversión automática a formato FLAC de alta calidad
- Extracción y adición de metadatos:
  - Portada del álbum
  - Título de las canciones
  - Artista
  - Nombre del álbum 
  - Año de lanzamiento
  - Género musical
  - Numeración de pistas
- Cola de descargas múltiples
- Soporte para modo claro/oscuro automático (descontinuado)
- Organización automática de archivos por artista/álbum

## Requisitos

- Python 3.x
- FFmpeg
- Dependencias de Python listadas en requirements.txt:
  - PyQt6==6.8.1
  - yt-dlp==2025.2.19
  - requests==2.32.3

## Instalación

1. Clonar el repositorio
2. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecutar el archivo principal:
```bash
python music-dl.py
```

2. Pegar la URL del álbum de YouTube Music
3. Seleccionar el género musical
4. (Opcional) Modificar la carpeta de destino
5. Hacer clic en "AGREGAR" para iniciar la descarga

Los archivos descargados se guardarán en la carpeta Output organizados por artista/álbum.

## Estructura del Proyecto

```
Music-DL/
├── app/
│   ├── core/            # Lógica principal
│   ├── gui/            # Interfaz gráfica
│   ├── resources/      # Recursos (iconos, binarios)
│   └── services/       # Servicios de descarga
├── requirements.txt    # Dependencias
└── music-dl.py        # Punto de entrada
```

## Créditos

Este proyecto utiliza las siguientes herramientas de código abierto:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Para la descarga de videos
- [FFmpeg](https://ffmpeg.org/) - Para la conversión de audio
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Para la interfaz gráfica

## Licencia

Este proyecto está bajo la Licencia MIT.
