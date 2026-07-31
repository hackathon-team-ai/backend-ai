import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KrishiMitra AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "krishimitra-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "krishimitra_db"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3-flash-preview"
    GROQ_API_KEY: str = ""

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    UPLOAD_DIR: str = "./uploads"
    STATIC_DIR: str = "./static"

    CORS_ORIGINS: List[str] = ["http://localhost:5173","http://localhost:3000","*"]

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)