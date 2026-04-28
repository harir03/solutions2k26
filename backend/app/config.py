"""
IntelliCredit Alternate (ICA) - Core Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "IntelliCredit Alternate"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/intellicredit"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Settings
    MODEL_PATH: str = "backend/models"
    DATA_PATH: str = "backend/data"
    
    # Fairness
    DISPARATE_IMPACT_THRESHOLD: float = 0.8  # Four-fifths rule
    
    class Config:
        env_file = ".env"


settings = Settings()
