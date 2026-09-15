import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MAX_CONCURRENT_SUMMARIES = int(os.getenv("MAX_CONCURRENT_SUMMARIES", "1"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "5000"))  # ~1,250 tokens (tailored for Groq's 8,000 TPM limit)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "400"))

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set. Add it to backend/.env")

MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "notesDB")
