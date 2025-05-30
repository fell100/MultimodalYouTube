import sys
import json
from typing import Dict, Any, Union
from pathlib import Path
from loguru import logger

# Configure loguru
LOG_LEVEL = "INFO"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Add file logger with rotation
log_file = Path("logs/app.log")
log_file.parent.mkdir(exist_ok=True)
logger.add(
    str(log_file),
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    rotation="10 MB",  # Rotate when file reaches 10MB
    compression="zip",  # Compress rotated logs
    retention="1 week",  # Keep logs for 1 week
    filter=lambda record: "langfuse" not in record["name"].lower() or record["level"].no >= logger.warning.level
)


class StructuredLogger:
    """
    Wrapper around loguru logger to provide structured logging capabilities
    """
    @staticmethod
    def info(message: Union[str, Dict[str, Any]], **kwargs):
        if isinstance(message, dict):
            logger.info(json.dumps(message))
        else:
            logger.info(message, **kwargs)
    
    @staticmethod
    def error(message: Union[str, Dict[str, Any]], **kwargs):
        if isinstance(message, dict):
            logger.error(json.dumps(message))
        else:
            logger.error(message, **kwargs)
    
    @staticmethod
    def warning(message: Union[str, Dict[str, Any]], **kwargs):
        if isinstance(message, dict):
            logger.warning(json.dumps(message))
        else:
            logger.warning(message, **kwargs)
    
    @staticmethod
    def debug(message: Union[str, Dict[str, Any]], **kwargs):
        if isinstance(message, dict):
            logger.debug(json.dumps(message))
        else:
            logger.debug(message, **kwargs)
    
    @staticmethod
    def critical(message: Union[str, Dict[str, Any]], **kwargs):
        if isinstance(message, dict):
            logger.critical(json.dumps(message))
        else:
            logger.critical(message, **kwargs)


l = StructuredLogger()



