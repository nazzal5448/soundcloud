from fastapi import FastAPI, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import requests
from downloader import build_download_command
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/fetch")
async def fetch(url: str = Form(...)):
    try:
        r = requests.get(f"https://soundcloud.com/oembed?url={url}&format=json")
        if r.status_code != 200:
            return JSONResponse({"error": "Failed to fetch metadata."}, status_code=500)

        data = r.json()
        title = data.get("title")
        return JSONResponse({
            "type": "track",
            "title": title,
            "url": url
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
