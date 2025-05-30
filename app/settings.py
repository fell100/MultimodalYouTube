import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Youtube Video Analysis"
    google_api_key: str
    model: str
    temperature: float
    speech_model: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()