from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv
import time
import threading
import json
from typing import List,Dict,Any

# ...existing code...


# Optional: Rate limiting class (only if you need it)
class RateLimiter:
    """Production rate limiting"""
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.calls = []
        self.lock = threading.Lock()
    
    def acquire(self):
        with self.lock:
            now = time.time()
            self.calls = [call for call in self.calls if now - call < 60]
            
            if len(self.calls) >= self.calls_per_minute:
                sleep_time = 60 - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    self.calls = self.calls[1:]
            
            self.calls.append(now)


load_dotenv()


# Step 1: Load text file
def load_text_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Handle JSON array format from transcription
    try:
        data = json.loads(content.replace("Transcript generated :  ", ""))
        text = " ".join([item.get('text', '') for item in data if isinstance(item, dict)])
        return text
    except:
        return content

# ...existing code...


# Step 2: Wrap into Document
def wrap_into_document(text):
    return [Document(page_content=text)]


# Step 3: Create chunks
def create_chunks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_documents(documents)


# Step 4: Embedding model
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# Step 5: Build & Save FAISS DB
def build_and_save_faiss(chunks, embedding_model, save_path="vectorstore/txt_faiss"):
    # Keep helper for backwards-compatibility if needed, but do not require saving
    db = FAISS.from_documents(chunks, embedding_model)
    print(f"FAISS vector store saved at: {save_path}")
    return db


# Step 6: Main function
def create_embeddings(text: str):
    """
    Create embeddings from text (string) and return a serializable list of
    {'text': chunk_text, 'embedding': [floats]} dictionaries suitable for
    storing in MongoDB.
    Returns None on failure.
    """
    try:
        if not text or not text.strip():
            print("⚠ Empty text provided for embedding")
            return None

        # Step 2: Wrap into Document
        print("Wrapping text into Document format...")
        documents = wrap_into_document(text)

        # Step 3: Create chunks
        print("Creating text chunks...")
        chunks = create_chunks(documents)
        print(f"Created {len(chunks)} chunks")

        if len(chunks) == 0:
            print("⚠ No chunks created for embedding")
            return None

        # Step 4: Get embedding model
        print("Loading embedding model...")
        embedding_model = get_embedding_model()

        # Step 5: Compute embeddings for each chunk
        texts = [c.page_content for c in chunks]
        vectors = None
        try:
            # Preferred API: embed_documents
            vectors = embedding_model.embed_documents(texts)
        except Exception:
            # Fallback: call embed_query per item
            vectors = []
            for t in texts:
                try:
                    v = embedding_model.embed_query(t)
                except Exception:
                    v = None
                vectors.append(v)

        # Build serializable list
        serializable = []
        for t, v in zip(texts, vectors):
            if v is None:
                continue
            # Ensure floats (e.g., numpy types) are converted
            vec_list = [float(x) for x in v]
            serializable.append({
                "text": t,
                "embedding": vec_list
            })

        if len(serializable) == 0:
            print("⚠ Embedding computation produced no vectors")
            return None

        print(f"✓ Created {len(serializable)} embeddings")
        return serializable

    except Exception as e:
        print(f"Error creating embeddings: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


