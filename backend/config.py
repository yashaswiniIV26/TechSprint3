from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Velionx API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CREDENTIALS_PATH: Optional[str] = "firebase-credentials.json"
    
    # Google AI
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - will be parsed from comma-separated string
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
