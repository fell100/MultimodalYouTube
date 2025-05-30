import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


from main import get_app

app = get_app(test_mode=True)
client = TestClient(app)

# Mock data for testing
MOCK_VIDEO_ANALYSIS = {
    "metadados": {
        "titulo": "Cat Falls Down The Stairs",
        "descricao": "Cat Dramatically Tumbles Down The Stairs Amidst Silly Play Fight With Cat Sibling",
        "duracao_segundos": 19,
        "data_upload": "2022-10-28T05:08:30",
        "autor": "Tom and Mimi",
        "visualizacoes": 82263,
        "id_video": "JzLtDZL7Nak",
        "url_thumbnail": "https://i.ytimg.com/vi/JzLtDZL7Nak/sddefault.jpg",
        "resolucao": "360p",
        "tamanho_arquivo": 1239637
    },
    "transcricao": {
        "texto_completo": "Thank you so much for joining us today",
        "segmentos": [
            {
                "inicio": 0,
                "fim": None,
                "texto": "Thank you so much for joining us today"
            }
        ]
    },
    "scenes": [
        {
            "start_time": 0,
            "end_time": 10,
            "description": "Two cats, one black and white and one grey, are in a hallway with grey carpet.",
            "visual_elements": [
                "black and white cat",
                "grey cat",
                "hallway",
                "grey carpet",
                "door"
            ],
            "audio_elements": [],
            "mood": "playful",
            "key_actions": [
                "cats interacting",
                "cat sitting",
                "cat standing"
            ]
        },
        {
            "start_time": 10,
            "end_time": 19,
            "description": "The grey cat chases the black and white cat down a flight of carpeted stairs.",
            "visual_elements": [
                "grey cat",
                "black and white cat",
                "stairs",
                "carpet"
            ],
            "audio_elements": [],
            "mood": "playful",
            "key_actions": [
                "cat chasing",
                "cats running down stairs"
            ]
        }
    ],
    "summary": "Two cats, one black and white and one grey, are playing in a house. They start in a hallway and then chase each other down a flight of stairs covered with grey carpet."
}

def test_info_endpoint():
    """Test the /info endpoint returns correct application information"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "model" in data
    assert "temperature" in data

@pytest.mark.asyncio
@patch('app.routes.analyze_youtube_video')
async def test_analyze_youtube_video_success(mock_analyze):
    """Test successful video analysis"""
    mock_analyze.return_value = MOCK_VIDEO_ANALYSIS
    
    response = client.post(
        "/api/youtube/analyze/",
        params={"youtube_url": "https://www.youtube.com/watch?v=test123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data == MOCK_VIDEO_ANALYSIS
    mock_analyze.assert_called_once_with("https://www.youtube.com/watch?v=test123")

@pytest.mark.asyncio
@patch('app.routes.analyze_youtube_video')
async def test_analyze_youtube_video_error(mock_analyze):
    """Test error handling in video analysis"""
    mock_analyze.side_effect = Exception("Test error")
    
    response = client.post(
        "/api/youtube/analyze/",
        params={"youtube_url": "https://www.youtube.com/watch?v=test123"}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Error analyzing video" in data["detail"]

def test_analyze_youtube_video_invalid_url():
    """Test video analysis with invalid URL"""
    response = client.post(
        "/api/youtube/analyze/",
        params={"youtube_url": "invalid-url"}
    )
    
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Error analyzing video" in data["detail"]
