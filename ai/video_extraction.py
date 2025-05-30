import logging
import os
import base64
import torch
from typing import Dict, Any, Optional, List
from datetime import datetime
from pytubefix import YouTube
import pytubefix as pytube
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.logging import l
from ai.video_extraction_model import VideoAnalysis
from ai.prompts import video_extraction_prompt
from app.settings import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)

def collect_metadata(url: str) -> Dict[str, Any]:
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        yt = YouTube(url)
        video_stream = yt.streams.get_highest_resolution()
        
        metadata = {
            "metadados": {
                "titulo": yt.title,
                "descricao": yt.description,
                "duracao_segundos": yt.length,
                "data_upload": yt.publish_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "autor": yt.author,
                "visualizacoes": yt.views,
                "id_video": yt.video_id,
                "url_thumbnail": yt.thumbnail_url,
                "resolucao": video_stream.resolution if video_stream else None,
                "tamanho_arquivo": video_stream.filesize if video_stream else None
            }
        }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise Exception(f"Video processing error: {str(e)}")
    

def generate_transcript(video_path: str) -> Dict[str, Any]:
    try:
        
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        model_id = settings.speech_model
        
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, 
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        model.to(device)
        
        processor = AutoProcessor.from_pretrained(model_id)
        
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )
        
        result = pipe(
            video_path,
            return_timestamps=True,
            generate_kwargs={
                "task": "transcribe",
                "language": "english"
            }
        )
        
        os.remove(video_path)
        
        formatted_transcript = {
            "transcricao": {
                "texto_completo": result["text"],
                "segmentos": []
            }
        }
        
        for chunk in result["chunks"]:
            segment = {
                "inicio": chunk["timestamp"][0],
                "fim": chunk["timestamp"][1],
                "texto": chunk["text"]
            }
            formatted_transcript["transcricao"]["segmentos"].append(segment)
        
        return formatted_transcript
        
    except Exception as e:
        logger.error(f"Error generating transcript: {str(e)}")
        raise Exception(f"Transcript generation error: {str(e)}")
    

def analyze_video_with_structured_output(video_base64: str, 
                                         prompt: str = video_extraction_prompt, 
                                         model: str = settings.model, 
                                         temperature: float = settings.temperature,
                                         ) -> Dict[str, Any]:

    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key=settings.google_api_key
    )

    structured_llm = llm.with_structured_output(VideoAnalysis)
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "media",
                "mime_type": "video/mp4",
                "data": video_base64
            }
        ]
    )
    
    response = structured_llm.invoke([message])
    return response.model_dump()

def download_youtube_video(url: str) -> str:
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()
    return video.download()

def load_video(file_path: str) -> str:
    with open(file_path, "rb") as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    return video_base64



async def analyze_youtube_video(url: str) -> Dict[str, Any]:

    try:

        video_path = download_youtube_video(url)
        l.info(f"Video {url[:10]} downloaded to: {video_path}")

        video_base64 = load_video(video_path)
        
        multimodal_analysis = analyze_video_with_structured_output(video_base64)
        l.info("Multimodal analysis completed")

        metadata = collect_metadata(url)
        l.info("Metadata collection completed")

        transcript = generate_transcript(video_path)
        l.info("Transcript generation completed")

        l.info("Analysis completed successfully")
        return {
            **metadata,
            **transcript,
            **multimodal_analysis,
        }
    
    except Exception as e:
        l.error(f"Error during video analysis: {str(e)}")
        raise
    
    finally:
        if os.path.exists(video_path):
            l.info(f"Cleaning up temporary video file: {video_path}")
            os.remove(video_path)
