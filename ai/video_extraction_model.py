from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Scene(BaseModel):
    start_time: float = Field(description="Start time of the scene in seconds")
    end_time: float = Field(description="End time of the scene in seconds")
    description: str = Field(description="Detailed description of the scene content")
    visual_elements: List[str] = Field(
        default_factory=list, 
        description="List of key visual elements present in the scene"
    )
    audio_elements: List[str] = Field(
        default_factory=list, 
        description="List of key audio elements present in the scene"
    )
    mood: str = Field(
        default="", 
        description="The overall mood or atmosphere of the scene"
    )
    key_actions: List[str] = Field(
        default_factory=list,
        description="List of main actions or events happening in the scene"
    )

class VideoAnalysis(BaseModel):
    scenes: List[Scene] = Field(description="List of analyzed scenes")
    summary: str = Field(description="Brief summary of the entire video content")