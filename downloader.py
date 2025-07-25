import yt_dlp
import os
import uuid
from typing import Callable

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class YTDLLogger:
    def __init__(self):
        self.last_progress = 0

    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(msg)

def download_track(url: str, progress_callback: Callable[[float], None] = None) -> str:
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    def hook(d):
        if d['status'] == 'downloading' and progress_callback:
            percent = d.get('_percent_str', '').strip().replace('%', '')
            if percent:
                try:
                    progress_callback(float(percent))
                except:
                    pass

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "logger": YTDLLogger(),
        "progress_hooks": [hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_template.replace("%(ext)s", "mp3")
