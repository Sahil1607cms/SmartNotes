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

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://sahil16072004_db_user:MawDWGwbH7gcb3hF@cluster0.cvrmksw.mongodb.net/?appName=Cluster0"
)
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "notesDB")
