from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import time
from app.settings import get_settings
from app.logging import l
from typing import List, Dict, Optional
from datetime import datetime

from ai.video_extraction import analyze_youtube_video

router = APIRouter()

class YouTubeURL(BaseModel):
    url: HttpUrl

class VideoAnalysis(BaseModel):
    metadados: Dict
    transcricao: Dict
    elementos_visuais: List[Dict]

@router.post("/api/youtube/analyze/")
async def analyze_youtube_video_endpoint(
    youtube_url: str,
):

    try:
        l.info(f"Received YouTube URL: {youtube_url}")
        analysis = await analyze_youtube_video(youtube_url)
        l.info(f"Analysis: {analysis}")
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing video: {str(e)}"
        )

@router.get("/info")
async def info():
    settings = get_settings()
    l.info(f"Getting {settings.app_name} info")
    return {
        "app_name": settings.app_name,
        "model": settings.model,
        "temperature": settings.temperature
    }
