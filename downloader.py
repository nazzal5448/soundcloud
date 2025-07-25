import yt_dlp
import os
import uuid
import asyncio

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class WebSocketLogger:
    def __init__(self, send_func):
        self.send_func = send_func

    def debug(self, msg): self._send(f"[DEBUG] {msg}")
    def info(self, msg): self._send(f"[INFO] {msg}")
    def warning(self, msg): self._send(f"[WARN] {msg}")
    def error(self, msg): self._send(f"[ERROR] {msg}")

    def _send(self, msg):
        asyncio.create_task(self.send_func(msg))

async def download_track_with_logs(url: str, file_id: str, send_func):
    output_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "logger": WebSocketLogger(send_func),
        "progress_hooks": [lambda d: asyncio.create_task(send_func(str(d)))],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
