import json
import yt_dlp
import hashlib

from PyQt6.QtCore import (
    QThread,
    pyqtSignal
)

class WorkerMetadata(QThread):
    emit_result = pyqtSignal(str)

    def __init__(self, url, destination_path):
        super().__init__()
        self._url = url
        self._hash = self.url_hash(self._url)
        self.destination_path = destination_path

    def url_hash(self, text):
        hash_obj = hashlib.md5()
        hash_obj.update(text.encode("utf-8"))
        hash_hex = hash_obj.hexdigest()
        return hash_hex

    def run(self):
        if not self._url:
            self.emit_result.emit("Empty URL")
            self.quit()
        else:
            try:
                self.url_metadata()
            finally:
                self.emit_result.emit("Thread WorkerMetadata finished")
                self.quit()

    def url_metadata(self):
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
                "ffmpeg_location" : "Resources/Scripts/ffmpeg.exe",
            }

            with yt_dlp.YoutubeDL(_ydl_opts) as yt:
                _url_metadata = yt.extract_info(self._url, download=False)

        except:
            self.emit_result.emit("Error downloading metadata")
        try: 
            with open(fr"{self.destination_path}/{self._hash}.json", "w", encoding="utf-8") as _save_metadata:
                json.dump(_url_metadata, _save_metadata, indent=4)

        except:
            self.emit_result.emit("Error saving metadata")