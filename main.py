from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import yt_dlp
import os
import logging

app = FastAPI()

# Define paths
DOWNLOADS_FOLDER = os.path.join(os.getcwd(), "downloads")
TEMPLATES_FOLDER = os.path.join(os.getcwd(), "templates")
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

# Mount static files and downloaded files routing
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# Initialize Jinja2Templates
templates = Jinja2Templates(directory=TEMPLATES_FOLDER)

# Model to handle video download requests
class VideoRequest(BaseModel):
    url: str
    quality: str
    download_type: str

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    # Serve the HTML template
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download")
async def download_video(video_request: VideoRequest):
    # Quality and format mapping for yt-dlp
    quality_map = {
        "144p": "18", "240p": "133", "360p": "134", "480p": "135",
        "720p": "136", "1080p": "137", "1440p": "271", "2160p": "313",
        "best": "bestvideo"
    }
    format_code = quality_map.get(video_request.quality, "bestvideo")
    format_option = "bestaudio" if video_request.download_type == "audio" else f"{format_code}+bestaudio/best"

    ydl_opts = {
        'format': format_option,
        'outtmpl': os.path.join(DOWNLOADS_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_request.url, download=True)
            file_path = ydl.prepare_filename(info)

        return {"message": f"{video_request.download_type.capitalize()} downloaded successfully in {video_request.quality} quality.", "file_path": os.path.basename(file_path)}
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")
