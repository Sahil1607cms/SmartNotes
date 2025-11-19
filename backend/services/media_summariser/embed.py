from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import time
import threading
import json

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
    db = FAISS.from_documents(chunks, embedding_model)
    db.save_local(save_path)
    print(f"FAISS vector store saved at: {save_path}")


# Step 6: Main function
def main():
    """
    Main function to orchestrate the FAISS vector store creation
    from transcription.txt file
    """
    try:
        # Define file paths
        transcription_file = "transcription.txt"
        vectorstore_save_path = "../../database/vectorstore"
        
        print("Starting FAISS vector store creation...")
        
        # Step 1: Load text file
        print(f"Loading text from: {transcription_file}")
        text = load_text_file(transcription_file)
        
        # Step 2: Wrap into Document
        print("Wrapping text into Document format...")
        documents = wrap_into_document(text)
        
        # Step 3: Create chunks
        print("Creating text chunks...")
        chunks = create_chunks(documents)
        print(f"Created {len(chunks)} chunks")
        
        # Step 4: Get embedding model
        print("Loading embedding model...")
        embedding_model = get_embedding_model()
        
        # Step 5: Build and save FAISS
        print("Building and saving FAISS vector store...")
        build_and_save_faiss(chunks, embedding_model, vectorstore_save_path)
        
        print("✓ FAISS vector store created successfully!")
        
    except FileNotFoundError:
        print(f"Error: {transcription_file} not found. Please ensure it exists in the current directory.")
    except Exception as e:
        print(f"Error creating FAISS vector store: {str(e)}")


if __name__ == "__main__":
    main()
