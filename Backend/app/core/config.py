"""
Configuration settings for AgriBot AI
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AgriBot AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/agribot"
    DATABASE_ECHO: bool = False
    
    # AI/ML Settings
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = None
    IMD_API_BASE: str = "https://mausam.imd.gov.in/imd_latest/contents/api"
    AGMARKNET_API: str = "https://agmarknet.gov.in/SearchCmmMkt.aspx"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # File storage
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Language support
    SUPPORTED_LANGUAGES: List[str] = [
        "hi",  # Hindi
        "en",  # English
        "ta",  # Tamil
        "te",  # Telugu
        "bn",  # Bengali
        "mr",  # Marathi
        "gu",  # Gujarati
        "kn",  # Kannada
        "ml",  # Malayalam
        "pa",  # Punjabi
        "ur",  # Urdu
    ]
    
    # Data sources
    DATA_DIRECTORY: str = "./data"
    DATASETS_DIRECTORY: str = "./data/datasets"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure directories exist
for directory in [
    settings.DATA_DIRECTORY,
    settings.DATASETS_DIRECTORY,
    settings.UPLOAD_DIRECTORY,
    settings.CHROMA_PERSIST_DIRECTORY,
]:
    Path(directory).mkdir(parents=True, exist_ok=True)