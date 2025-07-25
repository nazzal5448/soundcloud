from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from downloader import download_track
from utils import delete_file_after_delay
import asyncio
import os
import logging

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/download")
async def download(url: str = Query(..., description="SoundCloud track URL")):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, lambda: download_track(url))
    except Exception as e:
        logging.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download track")

    asyncio.create_task(delete_file_after_delay(file_path))

    return FileResponse(file_path, filename="track.mp3", media_type="audio/mpeg")
