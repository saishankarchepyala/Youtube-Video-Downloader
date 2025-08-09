# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import yt_dlp

app = FastAPI()

# Enable CORS for local frontend origins (adjust as needed)
origins = [
    "http://localhost:3000",  # adjust if your frontend runs on another port
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "*",  # Allow all origins - good for dev, avoid in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow POST, OPTIONS, GET etc
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    quality: str
    type: str  # "video" or "audio"

# Create downloads folder if not exists
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.post("/download")
def download_video(req: DownloadRequest):
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    # Extract numeric height from quality string (e.g. "720p" -> 720)
    try:
        height = int(req.quality.lower().replace("p", ""))
    except Exception:
        height = 720  # default fallback

    if req.type == "video":
        ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
    elif req.type == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    else:
        raise HTTPException(status_code=400, detail="Invalid download type")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=True)
            filename = ydl.prepare_filename(info)
            if req.type == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"

        return {"status": "success", "title": os.path.basename(filename)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
