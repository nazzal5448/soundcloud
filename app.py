from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import asyncio

from downloader import fetch_metadata, build_download_command

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/fetch")
async def fetch(url: str = Form(...)):
    try:
        metadata = await fetch_metadata(url)
        if isinstance(metadata, list):  # Playlist
            title = "Playlist"
            tracks = [{"title": m.get("title"), "url": m.get("webpage_url")} for m in metadata]
            return JSONResponse({"type": "playlist", "tracks": tracks, "title": title})
        else:  # Single track
            return JSONResponse({
                "type": "track",
                "title": metadata.get("title"),
                "url": metadata.get("webpage_url")
            })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/stream")
async def stream(url: str):
    try:
        cmd = build_download_command(url)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        return StreamingResponse(
            process.stdout,
            media_type="audio/mpeg",
            headers={"Content-Disposition": 'attachment; filename="soundcloud.mp3"'}
        )
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)
