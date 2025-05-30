import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock, mock_open
import base64
import torch
from pytubefix import YouTube
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from ai.video_extraction import (
    collect_metadata,
    generate_transcript,
    analyze_video_with_structured_output,
    download_youtube_video,
    load_video,
    analyze_youtube_video
)

# Test data
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=JzLtDZL7Nak"
TEST_VIDEO_PATH = "Cat Falls Down The Stairs.mp4"
TEST_BASE64_VIDEO = base64.b64encode(b"test video content").decode('utf-8')

# Mock response data
MOCK_VIDEO_ANALYSIS = {
    "metadados": {
        "titulo": "Test Video",
        "descricao": "Test Description",
        "duracao_segundos": 19,
        "data_upload": "2022-10-28T05:08:30",
        "autor": "Test Author",
        "visualizacoes": 82263,
        "id_video": "JzLtDZL7Nak",
        "url_thumbnail": "https://i.ytimg.com/vi/JzLtDZL7Nak/sddefault.jpg",
        "resolucao": "360p",
        "tamanho_arquivo": 1239637
    },
    "transcricao": {
        "texto_completo": "Test transcript",
        "segmentos": [
            {
                "inicio": 0,
                "fim": None,
                "texto": "Test transcript"
            }
        ]
    },
    "scenes": [
        {
            "start_time": 0,
            "end_time": 10,
            "description": "Test scene description",
            "visual_elements": ["test element"],
            "audio_elements": [],
            "mood": "test",
            "key_actions": ["test action"]
        }
    ],
    "summary": "Test summary"
}

@pytest.fixture
def mock_youtube():
    with patch('ai.video_extraction.YouTube') as mock:
        youtube_instance = MagicMock()
        youtube_instance.title = "Test Video"
        youtube_instance.description = "Test Description"
        youtube_instance.length = 19
        youtube_instance.publish_date = "2022-10-28T05:08:30"
        youtube_instance.author = "Test Author"
        youtube_instance.views = 82263
        youtube_instance.video_id = "JzLtDZL7Nak"
        youtube_instance.thumbnail_url = "https://i.ytimg.com/vi/JzLtDZL7Nak/sddefault.jpg"
        
        video_stream = MagicMock()
        video_stream.resolution = "360p"
        video_stream.filesize = 1239637
        youtube_instance.streams.get_highest_resolution.return_value = video_stream
        
        mock.return_value = youtube_instance
        yield mock

def test_collect_metadata_success(mock_youtube):
    """Test successful metadata collection"""
    result = collect_metadata(TEST_VIDEO_URL)
    
    assert result["metadados"]["titulo"] == "Test Video"
    assert result["metadados"]["descricao"] == "Test Description"
    assert result["metadados"]["duracao_segundos"] == 19
    assert result["metadados"]["autor"] == "Test Author"
    assert result["metadados"]["id_video"] == "JzLtDZL7Nak"
    assert result["metadados"]["resolucao"] == "360p"
    assert result["metadados"]["tamanho_arquivo"] == 1239637

def test_collect_metadata_invalid_url():
    """Test metadata collection with invalid URL"""
    with pytest.raises(ValueError):
        collect_metadata("invalid-url")

@pytest.mark.asyncio
@patch('ai.video_extraction.AutoModelForSpeechSeq2Seq.from_pretrained')
@patch('ai.video_extraction.AutoProcessor.from_pretrained')
@patch('ai.video_extraction.pipeline')
def test_generate_transcript_success(mock_pipeline, mock_processor, mock_model):
    """Test successful transcript generation"""
    # Mock pipeline response
    mock_pipeline.return_value.return_value = {
        "text": "Test transcript",
        "chunks": [{"timestamp": [0, None], "text": "Test transcript"}]
    }
    
    # Mock model and processor
    mock_model.return_value = MagicMock()
    mock_processor.return_value = MagicMock()
    
    result = generate_transcript(TEST_VIDEO_PATH)
    
    assert result["transcricao"]["texto_completo"] == "Test transcript"
    assert len(result["transcricao"]["segmentos"]) == 1
    assert result["transcricao"]["segmentos"][0]["texto"] == "Test transcript"

@pytest.mark.asyncio
@patch('ai.video_extraction.ChatGoogleGenerativeAI')
def test_analyze_video_with_structured_output_success(mock_llm):
    """Test successful video analysis with structured output"""
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value.invoke.return_value.model_dump.return_value = MOCK_VIDEO_ANALYSIS
    mock_llm.return_value = mock_llm_instance
    
    result = analyze_video_with_structured_output(TEST_BASE64_VIDEO)
    
    assert result == MOCK_VIDEO_ANALYSIS
    mock_llm.assert_called_once()

def test_download_youtube_video_success(mock_youtube):
    """Test successful video download"""
    mock_youtube.return_value.streams.get_highest_resolution.return_value.download.return_value = TEST_VIDEO_PATH
    
    result = download_youtube_video(TEST_VIDEO_URL)
    
    assert result == TEST_VIDEO_PATH
    mock_youtube.return_value.streams.get_highest_resolution.assert_called_once()

def test_load_video_success():
    """Test successful video loading and base64 encoding"""
    mock_content = b"test video content"
    
    with patch('builtins.open', mock_open(read_data=mock_content)):
        result = load_video(TEST_VIDEO_PATH)
        
        assert result == TEST_BASE64_VIDEO

@pytest.mark.asyncio
@patch('ai.video_extraction.download_youtube_video')
@patch('ai.video_extraction.load_video')
@patch('ai.video_extraction.analyze_video_with_structured_output')
@patch('ai.video_extraction.collect_metadata')
@patch('ai.video_extraction.generate_transcript')
async def test_analyze_youtube_video_success(
    mock_generate_transcript,
    mock_collect_metadata,
    mock_analyze_video,
    mock_load_video,
    mock_download_video
):
    """Test successful end-to-end video analysis"""
    # Setup mocks
    mock_download_video.return_value = TEST_VIDEO_PATH
    mock_load_video.return_value = TEST_BASE64_VIDEO
    mock_analyze_video.return_value = MOCK_VIDEO_ANALYSIS
    mock_collect_metadata.return_value = {"metadados": MOCK_VIDEO_ANALYSIS["metadados"]}
    mock_generate_transcript.return_value = {"transcricao": MOCK_VIDEO_ANALYSIS["transcricao"]}
    
    result = await analyze_youtube_video(TEST_VIDEO_URL)
    
    assert result["metadados"] == MOCK_VIDEO_ANALYSIS["metadados"]
    assert result["transcricao"] == MOCK_VIDEO_ANALYSIS["transcricao"]
    assert result["scenes"] == MOCK_VIDEO_ANALYSIS["scenes"]
    assert result["summary"] == MOCK_VIDEO_ANALYSIS["summary"]
    
    # Verify all mocks were called
    mock_download_video.assert_called_once_with(TEST_VIDEO_URL)
    mock_load_video.assert_called_once_with(TEST_VIDEO_PATH)
    mock_analyze_video.assert_called_once()
    mock_collect_metadata.assert_called_once_with(TEST_VIDEO_URL)
    mock_generate_transcript.assert_called_once_with(TEST_VIDEO_PATH)

@pytest.mark.asyncio
@patch('ai.video_extraction.download_youtube_video')
async def test_analyze_youtube_video_download_error(mock_download_video):
    """Test video analysis with download error"""
    mock_download_video.side_effect = Exception("Download failed")
    
    with pytest.raises(Exception) as exc_info:
        await analyze_youtube_video(TEST_VIDEO_URL)
    
    assert "Download failed" in str(exc_info.value)
