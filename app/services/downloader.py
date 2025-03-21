import json
import yt_dlp
import hashlib
import os
import subprocess
from pathlib import Path
from app.core.config import defaultConfig
from PyQt6.QtCore import (
    QThread,
    pyqtSignal,
    QMutex
)

# Carga la configuración de la ventana
with open(defaultConfig(), "r", encoding="utf-8") as load_config:
    global Config
    Config = json.load(load_config)

class WorkerDownload(QThread):
    emit_item_result = pyqtSignal(str)
    mutex = QMutex()

    def __init__(self, url, genre, audio_format, destination, default_destination, temp_destination):
        super().__init__()

        self._url = url
        self._genre = genre
        self._audio_format = audio_format
        self._destination = destination.replace("\\", "/")
        self._default_destination = default_destination.replace("\\", "/")
        self._temp_destination = temp_destination.replace("\\", "/")

    def url_hash(self, text):
        hash_obj = hashlib.md5()
        hash_obj.update(text.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()
        return hash_hex

    def run(self):
        if not self._url:
            self.emit_item_result.emit("Empty URL")
            self.quit()
        else:
            try:
                self.mutex.lock()
                self.emit_item_result.emit("Descargando")
                _metadata = self.download_metadata(self._url, self._temp_destination)
                self.download_music(
                    self._url,
                    self._genre,
                    self._audio_format,
                    self._destination,
                    self._default_destination,
                    self._temp_destination,
                    _metadata
                )
                self.add_metadata(
                    _metadata,
                    self._genre,
                    self._destination,
                    self._default_destination,
                    self._temp_destination
                )
            finally:
                self.quit()
                self.emit_item_result.emit("Finalizado")
                self.mutex.unlock()

    def download_metadata(self, url, temp_destination):
        try:
            class MyLogger(object):
                def debug(self, msg):
                    pass
                def warning(self, msg):
                    pass
                def error(self, msg):
                    pass

            _ydl_opts = {
                "logger" : MyLogger(),
                "ffmpeg_location" : Config["ffmpeg_path"],
            }

            with yt_dlp.YoutubeDL(_ydl_opts) as yt:
                _url_metadata = yt.extract_info(url, download=False)
        except:
            pass

        try:
            _json_name = self.url_hash(url)
            _json_config = os.path.join(temp_destination, f"{_json_name}.json")
            with open(_json_config, "w", encoding="utf-8") as _save_metadata:
                json.dump(_url_metadata, _save_metadata, indent=4)
            return _json_config
        except:
            pass

    def download_music(
        self,
        url,
        genre,
        audio_format,
        destination,
        default_destination,
        temp_destination,
        json_metadata = None
    ):
        try:
            if json_metadata is None:
                _output_download = os.path.join(temp_destination, "Artista Desconocido", "Álbum Desconocido")
            else:
                with open(json_metadata, "r", encoding="utf-8") as _read_metadata:
                    _config = json.load(_read_metadata)
                _output_download = os.path.join(
                    temp_destination,
                    _config["entries"][0]["artists"][0],
                    _config["entries"][0]["album"]
                )
            
            _ydl_opts = {
                'ffmpeg_location': Config["ffmpeg_path"],
                'format' : "bestaudio/best",
                "quiet" : True,
                "no_warnings" : True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': '0'
                }],
                'outtmpl': fr"{_output_download}/%(title)s.%(ext)s"
            }

            with yt_dlp.YoutubeDL(_ydl_opts) as ydl:
                ydl.download([self._url])
        except Exception as e:
            pass

    def add_metadata(
        self,
        album_json,
        genre,
        destination,
        default_destination,
        output_destination
    ):
        try:
            with open(album_json, "r", encoding="utf-8") as _read_metadata:
                _config = json.load(_read_metadata)
                _config_cover = _config["thumbnails"][-2]["url"]
                _config_album = _config["entries"][0]["album"]
                _config_artist = _config["entries"][0]["artists"][0]
                _config_artists = _config["entries"][0]["artists"]
                _config_year = _config["entries"][0]["release_year"]
                if _config_year is None:
                    _config_year = ["entries"][0]["upload_date"][:4]
                _date_year = _config["entries"][0]["upload_date"][:4]
                _date_mouth = _config["entries"][0]["upload_date"][4:6]
                _date_day = _config["entries"][0]["upload_date"][6:]
                _config_date = f"{_date_year}-{_date_mouth}-{_date_day}"
                if destination == "":
                    _config_destination =  os.path.join(default_destination, _config_artist, _config_album)
                else:
                    _config_destination = os.path.join(destination, _config_artist, _config_album)
        except Exception as e:
            pass

        try:
            temp_destination = os.path.join(output_destination, _config_artist, _config_album)
            files = [
                os.path.join(temp_destination, f)
                for f in os.listdir(temp_destination)
                if os.path.isfile(os.path.join(temp_destination, f))
            ]
            files.sort(key=lambda x: os.path.getctime(x))

            if not os.path.exists(_config_destination):
                os.makedirs(_config_destination)

            _tracks = 1

            for item in files:
                _file_name = os.path.basename(item)
                _title = Path(_file_name).stem 

                subprocess.run([
                    Config["ffmpeg_path"],
                    "-i", item,
                    "-i", _config_cover,
                    "-map", "0:a", "-map", "1",
                    "-codec", "copy",
                    "-disposition:v", "attached_pic",
                    "-metadata", f"title={_title}",
                    "-metadata", f"artist={_config_artists}",
                    "-metadata", f"album={_config_album}",
                    "-metadata", f"year={_config_year}",
                    "-metadata", f"date={_config_date}",
                    "-metadata", f"genre={genre}",
                    "-metadata", f"track={_tracks}",
                    "-loglevel", "warning",
                    "-y",
                    fr"{_config_destination}/{_file_name}"
                ])

                _tracks += 1
        except Exception as e:
            pass