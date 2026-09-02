import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.summarizer import router as summarizer_router
from app.api.notes import router as notes_router
from app.api.flashcards import router as flashcards_router
from app.api.chat import router as chat_router
from app.api.transcript import router as transcript_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager:
    1. Verifies active MongoDB connection.
    2. Pre-loads heavy HuggingFace Embedding Model into RAM.
    """
    logger.info("🍃 [Startup] Initializing MongoDB database connection...")
    try:
        from app.core.database import init_db_connection
        init_db_connection()
    except Exception as e:
        logger.error(f"❌ [Startup Error] MongoDB initialization failed: {e}")

    logger.info("⚡ [Startup] Pre-loading HuggingFace Embedding Model (sentence-transformers/all-MiniLM-L6-v2)...")
    try:
        from app.services.vector_search import get_embedding_model
        get_embedding_model()
        logger.info("✅ [Startup] Embedding Model pre-loaded successfully into RAM.")
    except Exception as e:
        logger.error(f"❌ [Startup Error] Failed to pre-load embedding model: {e}")
    
    yield
    logger.info("🛑 [Shutdown] SmartNotes Backend API shutting down...")


app = FastAPI(
    title="SmartNotes API",
    description="Clean, Local-Only AI Knowledge & Vector Processing Engine",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(summarizer_router)
app.include_router(notes_router)
app.include_router(flashcards_router)
app.include_router(chat_router)
app.include_router(transcript_router)


@app.get("/")
def read_root():
    return {"message": "SmartNotes Backend API is running."}