from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from downloader import download_track_with_logs
from utils import delete_file_after_delay
import os
import asyncio
import uuid
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def download_via_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        url = data.get("url")
        if not url or not url.startswith("http"):
            await websocket.send_text("ERROR::Invalid URL")
            return

        file_id = str(uuid.uuid4())
        file_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3")

        async def log_callback(msg: str):
            await websocket.send_text(msg)

        await download_track_with_logs(url, file_id, log_callback)
        await websocket.send_text(f"DONE::{file_id}.mp3")
        asyncio.create_task(delete_file_after_delay(file_path, delay=120))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        await websocket.send_text(f"ERROR::{str(e)}")
        await websocket.close()

@app.get("/file/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type="audio/mpeg")
