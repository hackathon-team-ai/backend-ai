import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.router import api_router

# ── Inject API keys into os.environ at startup ──────────────────────────────
# This ensures keys are available to all services even if pydantic-settings
# could not load the .env file (e.g. Windows .env folder quirk).
def _inject_keys_from_env_file():
    base = os.path.dirname(os.path.abspath(__file__))
    for path in [os.path.join(base, ".env"), os.path.join(base, ".env", ".env")]:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip().strip('"').strip("'")
                        if key and val and key not in os.environ:
                            os.environ[key] = val
            break  # use first file found

_inject_keys_from_env_file()

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("krishimitra.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing KrishiMitra AI Backend services...")
    logger.info("GROQ_API_KEY loaded: %s", bool(os.environ.get("GROQ_API_KEY")))
    logger.info("GEMINI_API_KEY loaded: %s", bool(os.environ.get("GEMINI_API_KEY")))
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    await connect_to_mongo()
    yield
    await close_mongo_connection()
    logger.info("KrishiMitra AI Backend shutdown complete.")

app = FastAPI(
    title="KrishiMitra AI - Backend API",
    description="Multimodal AI Agriculture Advisor REST API powered by FastAPI, Google Gemini, ChromaDB RAG, and Motor MongoDB.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (Uploaded Leaf Images, Audio MP3s)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Mount API v1 Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
