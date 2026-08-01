import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


def _find_env_file() -> str | None:
    """
    Return the path to the .env file regardless of whether the user accidentally
    created a '.env' *folder* (Windows quirk) or a proper '.env' *file*.

    Search order:
      1. backend-ai/.env          (correct — plain file)
      2. backend-ai/.env/.env     (wrong but common — file inside folder)
      3. backend-ai/.env.example  (last resort fallback)
    """
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(base, ".env"),
        os.path.join(base, ".env", ".env"),
        os.path.join(base, ".env.example"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


_ENV_FILE = _find_env_file()


class Settings(BaseSettings):
    PROJECT_NAME: str = "KrishiMitra AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "krishimitra-super-secret-jwt-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "krishimitra_db"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GROQ_API_KEY: str = ""

    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    UPLOAD_DIR: str = "./uploads"
    STATIC_DIR: str = "./static"

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
    ]

    model_config = ConfigDict(
        env_file=_ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

# Log which env file was loaded so it's visible in backend logs
import logging
_logger = logging.getLogger("krishimitra.config")
_logger.info("Loaded env file: %s", _ENV_FILE)
_logger.info("GEMINI_API_KEY present: %s", bool(settings.GEMINI_API_KEY))
_logger.info("GROQ_API_KEY present: %s", bool(settings.GROQ_API_KEY))

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)