from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Set
from pathlib import Path
from enum import Enum

class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class Settings(BaseSettings):
    APP_NAME: str = "Contract Analyzer API"
    GROQ_API_KEY: str
    MODEL_NAME: str = "mixtral-8x7b-32768"
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".doc", ".txt"}
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    class Config:
        env_file = ".env"
        use_enum_values = True

@lru_cache()
def get_settings():
    return Settings()