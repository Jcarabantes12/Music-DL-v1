#!python3.13.0

import os
import re
import sys
import json
import time
import yt_dlp
import subprocess
import requests
from pathlib import Path
from app.core.config import defaultConfig
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QComboBox,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
    QApplication,
    QTableWidget,
    QTableWidgetItem
)
from PyQt6.QtCore import (
    Qt,
    QSize,
    QThread,
    QMargins,
    pyqtSignal,
    QMutex,
    QTimer
)
from PyQt6.QtGui import (
    QIcon,
    QPixmap,
)            

# Carga la configuración de la ventana
with open(defaultConfig(), "r", encoding="utf-8") as load_config:
    global Config
    Config = json.load(load_config)

# Ventana principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(Config["app_name"] + " | " + Config["app_version"]) # Título de la ventana
        self.setWindowIcon(QIcon(Config["icons"]["app_icon"])) # Icono de la ventana

        self.load_interface() # Carga la interfaz de usuario

        # Carga los estilos CSS de la ventana
        with open(Config["style_css"], "r") as load_style:
            self.setStyleSheet(load_style.read())

        if Config["window_dimensions"] == "Maximized":
            self.showMaximized() # Maximiza la ventana


    # Interfaz de usuario
    def load_interface(self):
        # Widget principal
        main_Wg = QWidget() # Agrupa el area contenedor
        main_Wg.setObjectName("main_Wg") # Nombre del objeto para los estilos
        
        # Area contenedor
        container_area_LyHB = QHBoxLayout() # Agrupa el area de inputs y el area de contenido
        container_area_LyHB.setContentsMargins(QMargins(10, 10, 10, 10)) # Margenes (left, top, right, bottom)
        container_area_LyHB.setSpacing(10) # Espaciado entre widgets
        
        # Area de inputs
        input_area_Wg = QWidget() # Contiene el layout grid
        input_area_Wg.setObjectName("input_area_Wg") # Nombre del objeto para los estilos
        input_area_Wg.setFixedWidth(500) # Tamaño horizontal

        input_area_LyG = QGridLayout() # Layout grid de inputs
        input_area_LyG.setContentsMargins(QMargins(10, 10, 10, 10)) # Margenes (left, top, right, bottom)
        input_area_LyG.setSpacing(10) # Espaciado entre widgets

        # Area de contenido
        content_area_LyVB = QVBoxLayout() # Agrupa el area de cola y area de información
        content_area_LyVB.setContentsMargins(QMargins(0, 0, 0, 0)) # Margenes (left, top, right, bottom)
        content_area_LyVB.setSpacing(10) # Espaciado entre widgets
        
        # Area de cola
        line_area_Wg = QWidget() # Contiene el layout grid de la cola
        line_area_Wg.setObjectName("line_area_Wg") # Nombre del objeto para los estilos
        line_area_Wg.setMinimumWidth(input_area_Wg.width() + 200)
        line_area_Wg.setMinimumHeight(400)

        line_area_LyVB = QVBoxLayout() # Layout vertical de cola
        line_area_LyVB.setContentsMargins(QMargins(10, 0, 10, 10)) # Margenes (left, top, right, bottom)
        line_area_LyVB.setSpacing(10) # Espaciado entre widgets

        line_list_LyVB = QVBoxLayout()
        line_list_LyVB.setContentsMargins(QMargins(0, 0, 0, 0)) # Margenes (left, top, right, bottom)
        line_list_LyVB.setSpacing(10) # Espaciado entre widgets

        # Area de información
        info_area_Wg = QWidget() # Contiene el layout grid de información
        info_area_Wg.setObjectName("info_area_Wg") # Nombre del objeto para los estilos
        info_area_Wg.setFixedHeight(225) # Tamaño horizontal

        info_area_LyG = QGridLayout() # Layout grid de información
        info_area_LyG.setContentsMargins(QMargins(10, 0, 10, 10)) # Margenes (left, top, right, bottom)
        info_area_LyG.setSpacing(10) # Espaciado entre widgets


        # Area de inputs
        # Icono de la ventana como título
        title_ICON = QLabel()
        title_ICON.setObjectName("title_ICON") # ID CSS
        title_ICON.setPixmap(QPixmap(Config["icons"]["app_icon"]).scaled(QSize(125, 125))) # Carga el icono de la aplicación (con escala de 125x125)
        title_ICON.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop) # CentroH/ArribaV

        # Título de la URL
        url_title_L = QLabel()
        url_title_L.setObjectName("url_title_L") # ID CSS
        url_title_L.setText("URL:") # Texto

        # Entrada de la URL
        self.url_input_LE = QLineEdit()
        self.url_input_LE.setObjectName("url_input_LE") # ID CSS
        self.url_input_LE.setPlaceholderText("https://music.youtube.com/playlist?list=0000000000") # URL de ejemplo

        # Título de formato
        format_title_L = QLabel()
        format_title_L.setObjectName("format_title_L") # ID CSS
        format_title_L.setText("Formato:") # Texto

        # Lista de formatos
        self.format_CB = QComboBox()
        self.format_CB.setObjectName("format_CB") # ID CSS
        self.format_CB.addItems(sorted(Config["Formats"])) # Lista de formatos
        self.format_CB.setCurrentText("Flac") # Formato por defecto

        # Título de generos
        genre_title_L = QLabel()
        genre_title_L.setObjectName("genre_title_L") # ID CSS
        genre_title_L.setText("Genero:") # Texto

        # Lista de generos
        self.genre_CB = QComboBox()
        self.genre_CB.setObjectName("genre_CB") # ID CSS
        self.genre_CB.addItems(sorted(Config["Genres"])) # Lista de generos
        self.genre_CB.setCurrentText("Dubstep") # Genero por defecto

        # Título de la ruta
        directory_title_L = QLabel()
        directory_title_L.setObjectName("directory_title_L") # ID CSS
        directory_title_L.setText("Guardar en:") # Texto

        # Entrada de la Guardar en
        self.directory_input_LE = QLineEdit()
        self.directory_input_LE.setObjectName("directory_input_LE") # ID CSS
        self.directory_input_LE.setPlaceholderText(Config["app_output"])

        # Espacio
        space_item_SI = QSpacerItem(
            0, # 0px horizontal
            20, # 20px vertical
            QSizePolicy.Policy.Ignored, # Ignora el eje X
            QSizePolicy.Policy.Expanding # Expande el eje Y
        ) # Empuja los widget hacia arriba

        # Boton de agregar a la cola
        add_button_PB = QPushButton()
        add_button_PB.setObjectName("add_button_PB")
        add_button_PB.setText(" " + "AGREGAR") # Texto
        add_button_PB.setIcon(QIcon(Config["icons"]["addLine_icon"])) # Icono del boton
        add_button_PB.setIconSize(QSize(25, 25)) # Dimenciones del icono
        add_button_PB.clicked.connect(self.decision) # Ejecución al hacer clic


        # Area de cola
        # Título de cola
        line_title_L = QLabel()
        line_title_L.setObjectName("line_title_L") # ID CSS
        line_title_L.setText("COLA") # Texto
        line_title_L.setAlignment(
            Qt.AlignmentFlag.AlignCenter # CentroH
            | Qt.AlignmentFlag.AlignTop # ArribaV
        )

        self.line_table_TW = QTableWidget()
        self.line_table_TW.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.line_table_TW.setColumnCount(5) # Columnas totales que se agregaran
        self.line_table_TW.setHorizontalHeaderLabels(["Estado", "URL", "Genero", "Formato", "Guardar en"]) # Nombre de las columnas totales
        self.line_table_TW.setColumnWidth(0, 150) # Estado
        self.line_table_TW.setColumnWidth(1, 250) # URL
        self.line_table_TW.setColumnWidth(2, 150) # Genero
        self.line_table_TW.setColumnWidth(3, 150) # Formato
        self.line_table_TW.setColumnWidth(4, 250) # Destino


        # Area de información
        # Titulo de información
        info_title_L = QLabel()
        info_title_L.setObjectName("info_title_L") # ID CSS
        info_title_L.setText("INFORMACIÓN") # Texto
        info_title_L.setAlignment(
            Qt.AlignmentFlag.AlignCenter # CentroH
            | Qt.AlignmentFlag.AlignTop # ArribaV
        )

        # Texto de información
        self.info_text_L = QLabel()
        self.info_text_L.setObjectName("info_text_L") # ID CSS
        self.info_text_L.setSizePolicy(
            QSizePolicy.Policy.Ignored, # Ignora el eje X
            QSizePolicy.Policy.Expanding # Expande el eje Y
        )
        self.info_text_L.setAlignment(
            Qt.AlignmentFlag.AlignTop # ArribaH
            | Qt.AlignmentFlag.AlignLeft # IzquierdaV
        )
        self.info_text_L.setTextInteractionFlags(
            # Activa la opción de sombrear el texto del laber
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.info_text_L.setWordWrap(True) # Salto de linea cuando llege a su maximo en el eje X

        # Scroll del texto de información
        info_scroll_SA = QScrollArea()
        info_scroll_SA.setWidgetResizable(True)
        info_scroll_SA.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)


        # AGREGAR LOS WIDGET A LA VENTANA
        # Area de inputs
        input_area_LyG.addWidget(title_ICON, 1, 1, 1, 4) # Agrega el icono de la ventana al area de inputs como titulo (abarca 2 columnas)
        input_area_LyG.addWidget(url_title_L, 2, 1, 1, 4)
        input_area_LyG.addWidget(self.url_input_LE, 3, 1, 1, 4) # Agrega el input de la url al area de inputs
        input_area_LyG.addWidget(format_title_L, 4, 1, 1, 2)
        input_area_LyG.addWidget(self.format_CB, 5, 1, 1, 2)
        input_area_LyG.addWidget(genre_title_L, 4, 3, 1, 2)
        input_area_LyG.addWidget(self.genre_CB, 5, 3, 1, 2)
        input_area_LyG.addWidget(directory_title_L, 6, 1, 1, 4)
        input_area_LyG.addWidget(self.directory_input_LE, 7, 1, 1, 4)
        input_area_LyG.addItem(space_item_SI, 99, 1, 1, 4)
        input_area_LyG.addWidget(add_button_PB, 100, 2, 1, 2) # Agrega el boton "agregar a la cola" al area de inputs


        # Area de cola
        line_area_LyVB.addWidget(line_title_L) # Agrega el titulo de cola al area de cola
        line_area_LyVB.addLayout(line_list_LyVB) # Agrega el texto de cola al area de cola
        line_list_LyVB.addWidget(self.line_table_TW)


        # Area de información
        info_area_LyG.addWidget(info_title_L, 1, 1) # Agrega el titulo de información al area de información
        info_area_LyG.addWidget(info_scroll_SA, 2, 1) # Agrega el widget de scroll al area de información
        info_scroll_SA.setWidget(self.info_text_L) # Agrega el texto de información al widget de scroll
        
        input_area_Wg.setLayout(input_area_LyG) # Agrega el area de inputs al widget de area de inputs
        container_area_LyHB.addWidget(input_area_Wg) # Agrega el widget de area de inputs al area contenedor
        container_area_LyHB.addLayout(content_area_LyVB) # Agrega el layout de area de contenido al area contenedor
        content_area_LyVB.addWidget(line_area_Wg) # Agrega el widget de area de cola al area de contenido
        content_area_LyVB.addWidget(info_area_Wg) # Agrega el widget de area de cola al area de contenido
        line_area_Wg.setLayout(line_area_LyVB) # Agrega el layout de area de cola al widget de información
        info_area_Wg.setLayout(info_area_LyG) # Agrega el layout de area de información al widget de información
        main_Wg.setLayout(container_area_LyHB) # Agrega el layout area contenedor al widget principal
        self.setCentralWidget(main_Wg) # Agrega el widget principal a la ventana

    def add_item_table_TW(self):
        row_position = self.line_table_TW.rowCount() # Número de filas

        self.line_table_TW.insertRow(row_position) # Inserta una fila

        # Agrega un item en Estado
        self.add_item_status = QTableWidgetItem()
        self.add_item_status.setText("Pendiente") # Cuando se crea una fila se agrega por defecto el texto "Pendiente"
        self.add_item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Alinear al centroH

        # Agrega un item en URL
        add_item_url = QTableWidgetItem()
        add_item_url.setText(self.url_input_LE.text()) # Inserta la URL que se añadio en el input URL
        add_item_url.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Alinea al centroH

        # Agrega un item en Genero
        add_item_genre = QTableWidgetItem()
        add_item_genre.setText(self.genre_CB.currentText()) # Inserta el genero seleccionado en el input genero
        add_item_genre.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Alinea al centroH

        # Agrega un item en Formato
        add_item_format = QTableWidgetItem()
        add_item_format.setText(self.format_CB.currentText()) # Inserta el formato seleccionado en el input formato
        add_item_format.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Alinea al centroH

        # Agrega un item en Guardar en
        directory = self.directory_input_LE.text().strip()
        if len(directory) == 0:
            directory = Config["app_output"] 
        add_item_directory = QTableWidgetItem()
        add_item_directory.setText(directory.replace("\\", "/")) # Inserta la Guardar en seleccionada en el input ruta de destino
        add_item_directory.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Alinea al centroH

        # Agrega los items a la tabla
        self.line_table_TW.setItem(row_position, 0, self.add_item_status) # Estado
        self.line_table_TW.setItem(row_position, 1, add_item_url) # URL
        self.line_table_TW.setItem(row_position, 2, add_item_genre) # Genero
        self.line_table_TW.setItem(row_position, 3, add_item_format) # Formato
        self.line_table_TW.setItem(row_position, 4, add_item_directory) # Guardar en

        # 
        self.start_task()

    def decision(self):
        # URL
        url = self.url_input_LE.text().strip()

        # Si la URL es correcta
        if url:
            self.show_input()
            self.add_item_table_TW()

        else:
            self.url_input_LE.clear()
            self.url_input_LE.setStyleSheet("""
                border: 5px solid #311212;
                background-color: #311212;
                border-radius: 5px;
                height: 30px;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 16px;
                color: #ebe4e4;
            """)
            self.url_input_LE.setPlaceholderText("Ingresa una URL")

            self.directory_input_LE.setStyleSheet("""
                border-radius: 5px;
                height: 30px;
                border: 5px solid #052741;
                background-color: #052741;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 16px;
                color: #ebe4e4;
            """)
            QTimer.singleShot(3000, self.show_input)

    def show_input(self):
        self.url_input_LE.setStyleSheet("""
                border-radius: 5px;
                height: 30px;
                border: 5px solid #052741;
                background-color: #052741;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 16px;
                color: #ebe4e4;
            """)
        self.url_input_LE.setPlaceholderText("https://music.youtube.com/playlist?list=0000000000")
        self.directory_input_LE.setStyleSheet("""
            border-radius: 5px;
            height: 30px;
            border: 5px solid #052741;
            background-color: #052741;
            padding-left: 10px;
            padding-right: 10px;
            font-size: 16px;
            color: #ebe4e4;
        """)
        self.directory_input_LE.setPlaceholderText(Config["app_output"])

    def start_task(self):
        time.sleep(2)
        self.worker = self.Worker(
            self.line_table_TW,
            self.directory_input_LE.text(),
            self.format_CB.currentText(),
            self.genre_CB.currentText()
        )
        self.url_input_LE.clear()

        self.worker.emit_result.connect(self.show_info_text)

        self.worker.start()

    def show_info_text(self, message):
        if message == "end":
            space = "-"
            # Carga el JSON del álbum
            with open(fr"{Config["app_temp"]}/album_metadata.json", "r", encoding="utf-8") as load_album_metadata:
                _data = json.load(load_album_metadata)

            # Muestra en la sección de información los datos del álbum cuando termina la descarga
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Álbum: {_data["album"]}\n") # Álbum
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Artista: {_data["artist"]}\n") # Artista
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Género: {_data["genre"]}\n") # Genero
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Año de Lanzamiento: {_data["year"]}\n") # Año de lanzamiento
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Número de Pistas: {_data["n_tracks"]}\n") # Número de pistas
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Fecha de Publicación: {_data["date"]}\n") # Fecha de publicación
            self.info_text_L.setText(f"{self.info_text_L.text()}    - Guardado en: {_data["tag"]}/{_data["artist"]}/{_data["album"]}\n")
            self.info_text_L.setText(f"{self.info_text_L.text()}{space*100}")

        else:
            self.info_text_L.setText(self.info_text_L.text() + message)

    class Worker(QThread):
        emit_result = pyqtSignal(str)
        mutex = QMutex()

        def __init__(self, row_item, locate_album, format_album, genre):
            super().__init__()
            self.row_item = row_item
            self.locate_album = locate_album.replace("\\", "/")
            self.format = format_album
            self.genre = genre

        def run(self):
            time.sleep(2)
            self.mutex.lock()
            row_count = self.row_item.rowCount()
            
            for row in range(row_count):
                item = self.row_item.item(row, 0)
                # Extraer la URL de la tabla[URL]
                self.url = self.row_item.item(row, 1)

                if row == 0:
                    text_1 = "[1] Descargando los metadatos de la URL\n"
                else:
                    text_1 = "\n[1] Descargando los metadatos de la URL\n"


                # if item.text() == "Pendiente" and item is not None:
                if item.text() == "Pendiente":
                    download_item = QTableWidgetItem()
                    download_item.setText("Descargando")
                    download_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.row_item.setItem(row, 0, download_item)
                    self.emit_result.emit(text_1)
                    
                    # Verifica si la Guardar en es correcta
                    if not self.locate_album:
                        self.locate_album = Config["app_output"]

                    # opciones de yt_dlp
                    ydl_opts = {
                            "ffmpeg_location" : Config["ffmpeg_path"], # Ruta del archivo FFMPEG
                            "quiet" : True # Muestra solo advertencias importantes
                        }

                    try:
                        # Descarga los metadatos
                        with yt_dlp.YoutubeDL(ydl_opts) as yt:
                            data = yt.extract_info(self.url.text(), download=False) # No se decargara contenido multimedia, solo los metadatos

                        # Guarda los metadatos extraidos de la URL
                        with open(fr"{Config["app_temp"]}/url_metadata.json", "w", encoding="utf-8") as save_data:
                            json.dump(data, save_data, indent=4)
                        
                        time.sleep(2)

                    except Exception as e:
                        finnish_item = QTableWidgetItem()
                        finnish_item.setText("Error")
                        finnish_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.row_item.setItem(row, 0, finnish_item)
                        self.emit_result.emit(f"[1] Error al descargar los metadatos de la URL: {e}\n")

                    # Extrae la información necesaria de los metadatos de la url
                    # Y genera otro JSON para los datos del album
                    try:
                        self.emit_result.emit("[2] Generando los metadatos del álbum\n")

                        # Carga los metadatos de la URL
                        with open(fr"{Config["app_temp"]}/url_metadata.json", "r", encoding="utf-8") as load_metadata:
                            _data = json.load(load_metadata)

                        # Obtiene la URL, nombre, ruta del cover
                        cover_url_album = _data["thumbnails"][-2]["url"] # URL del cover

                        # Obtiene el nombre del álbum
                        album_name = _data["entries"][0]["album"]
                        _char_pattern = r"[://]| {2,}" # caracteres que se reemplazaran
                        album_name = re.sub(_char_pattern, "-", album_name)

                        # Descarga el cover
                        _response = requests.get(cover_url_album)
                        if _response.status_code == 200:
                            # Guarda el cover
                            with open(fr"{Config["app_temp"]}/{album_name}.jpg", 'wb') as save_cover:
                                save_cover.write(_response.content)

                        # Verifica si no existe el cover
                        if not os.path.exists(fr"{Config["app_temp"]}/{album_name}.jpg"):
                            album_cover = Config["noImage_icon"]
                        else: album_cover = fr"{Config["app_temp"]}/{album_name}.jpg"

                        # Obtiene el nombre del artista del álbum
                        artist_name = _data["entries"][0]["artists"][0]

                        # Obtiene el año de lanzamiento del álbum
                        year_album = _data["entries"][0]["release_year"] # Año

                        if year_album is None:
                            year_album = _data["entries"][0]["upload_date"][:4] # Año

                        # Obtiene el número de pistas del álbum
                        tracks_album = _data["entries"][0]["n_entries"]

                        # Obtiene la fecha de lanzamiento
                        dateDay_album = _data["entries"][0]["upload_date"][6:] # Dia
                        dateMount_album = _data["entries"][0]["upload_date"][4:6] # Mes
                        dateYear_album = _data["entries"][0]["upload_date"][:4] # Año
                        date_album = f"{dateYear_album}-{dateMount_album}-{dateDay_album}"

                        # Genera un archivo JSON que se utilizara para obtener la información del álbum
                        with open(fr"{Config["app_temp"]}/album_metadata.json", "w", encoding="utf-8") as _album_data:
                            _album_metadata = {
                                "cover_path" : album_cover, # Ruta del cover
                                "album" : album_name, # Nombre del album
                                "genre" : self.genre,
                                "artist" : artist_name, # Nombre del artista
                                "year" : year_album, # Año de lanzamiento del album
                                "date" : date_album, # Fecha de lanzamiento del album
                                "n_tracks" : tracks_album, # Número de pistas
                                "tag" : self.locate_album # Guardar en
                            }
                            json.dump(_album_metadata, _album_data, indent=4)

                        time.sleep(2)

                    except Exception as e:
                        finnish_item = QTableWidgetItem()
                        finnish_item.setText("Error")
                        finnish_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.row_item.setItem(row, 0, finnish_item)
                        self.emit_result.emit(f"[2] Error al descargar los metadatos de la URL: {e}\n")

                    try:
                        self.emit_result.emit("[3] Descargando el álbum\n")
                        time.sleep(2)

                        # Carga el JSON del álbum
                        with open(fr"{Config["app_temp"]}/album_metadata.json", "r", encoding="utf-8") as load_album_metadata:
                            album_metadata = json.load(load_album_metadata)

                            _artist = album_metadata["artist"]
                            _album = album_metadata["album"]

                        # Configuración de descarga (FLAC)
                        ydl_opts = {
                            'ffmpeg_location': Config["ffmpeg_path"],  # cambia esto a la ubicación correcta
                            'format' : "bestaudio/best",
                            "quit" : True,
                            'ignoreerrors': True,  # ignora los errores
                            'no_overwrites': True,  # no vuelve a descargar archivos que ya han sido descargados
                            'continue': True,  # continua descargando archivos que fueron descargados y cancelados por un error
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': self.format, # formato
                                'preferredquality': '0' # calidad maxima (0)
                            }],
                            'outtmpl': fr"{Config["app_temp"]}/{_artist}/{_album}/%(title)s.%(ext)s",  # ruta de destino por defecto
                        }

                        # Inicia la descarga
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([self.url.text()])

                        time.sleep(2)
                    
                    except Exception as e:
                        finnish_item = QTableWidgetItem()
                        finnish_item.setText("Error")
                        finnish_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.row_item.setItem(row, 0, finnish_item)
                        self.emit_result.emit(f"[3] Error al descargar el álbum: {e}\n")

                    # Agrega los metadatos del album a la musica
                    try:
                        self.emit_result.emit("[4] Agregando los metadatos al álbum\n")

                        with open(fr"{Config["app_temp"]}/album_metadata.json", "r", encoding="utf-8") as read_album_metadata:
                            _data = json.load(read_album_metadata)

                        _cover = _data["cover_path"]
                        _album = _data["album"]
                        _artist = _data["artist"]
                        _year = _data["year"]
                        _date = _data["date"]
                        _genre = _data["genre"]
                        _output_yt_dlp_path = fr"{Config["app_temp"]}/{_artist}/{_album}"
                        _output_path = fr"{self.locate_album}/{_artist}/{_album}"

                        # Crea el directorio donde se colocara lo descargado con los metadatos
                        if not os.path.exists(_output_path):
                            os.makedirs(_output_path)

                        # Obtiene la lista de archivos en la carpeta
                        files = [
                            os.path.join(_output_yt_dlp_path, f)
                            for f in os.listdir(_output_yt_dlp_path)
                            if os.path.isfile(os.path.join(_output_yt_dlp_path, f))
                        ]

                        # Ordena los archivos por fecha de creación
                        files.sort(key=lambda x: os.path.getctime(x))


                        # Número de pistas
                        _tracks = 1

                        # imprime los archivos ordenados
                        for item in files:
                            _file_name = os.path.basename(item)

                            # Título del album
                            _title = Path(_file_name).stem

                            subprocess.run([
                                Config["ffmpeg_path"],
                                "-i", item,
                                "-i", _cover,
                                "-map", "0:a", "-map", "1",
                                "-codec", "copy", # copia el flujo del archivo sin volver a decodificar
                                "-disposition:v", "attached_pic",
                                "-metadata", f"title={_title}", # Título
                                "-metadata", f"artist={_artist}", # Nombre del artista
                                "-metadata", f"album={_album}", # Nombre del álbum
                                "-metadata", f"year={_year}", # Año del álbum
                                "-metadata", f"date={_date}", # fecha de lanzamiento del álbum
                                "-metadata", f"genre={_genre}", # Genero del álbum
                                "-metadata", f"track={_tracks}", # Pistas del álbum
                                "-loglevel", "warning", # oculta la informacion de ffmpeg
                                "-y", # Acepta todos los avisos
                                fr"{_output_path}/{_file_name}"
                            ])

                            _tracks += 1 # Agrega 1 al número de pistas

                        finnish_item = QTableWidgetItem()
                        finnish_item.setText("Descarga Finalizada")
                        finnish_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.row_item.setItem(row, 0, finnish_item)
                        self.emit_result.emit("[5] Descarga Finalizada\n")
                        self.emit_result.emit("end")

                        time.sleep(2)

                    except Exception as e:
                        finnish_item = QTableWidgetItem()
                        finnish_item.setText("Error")
                        finnish_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.row_item.setItem(row, 0, finnish_item)
                        self.emit_result.emit(f"[4] Error al agregar los metadatos al álbum: {e}\n")

            time.sleep(2)
            self.mutex.unlock()

        def closeEvent(self, event):
            try:
                # No cerramos la ventana, pero sí podemos asegurarnos de que el hilo termine bien
                if self.worker.isRunning():
                    self.worker.quit()  # Detenemos el hilo
                    self.worker.wait()  # Esperamos a que termine sin cerrar la ventana
                event.accept()

            except Exception as e:
                print(f"worker: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()    
    window.show()
    sys.exit(app.exec())