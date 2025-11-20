# Standard / environment
import os
from dotenv import load_dotenv

# Typing helpers
from typing import List, Optional

# Groq SDK (used by the Groq LLM wrapper)
from groq import Groq

# LangChain core pieces
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import LLM
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Embeddings + Vectorstore (FAISS)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Pydantic helper
from pydantic import PrivateAttr

import logging

GROQ_RATE_LIMIT = 100
GEMINI_RATE_LIMIT = 60

load_dotenv()


# === Wrap Groq Chat API into LangChain-compatible class ===
class GroqLLM(LLM):
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.6
    _client: Groq = PrivateAttr()

    def __init__(self, api_key: str, model_name: Optional[str] = None, temperature: float = 0.6):
        super().__init__()
        self._client = Groq(api_key=api_key)
        self.model = model_name or self.model
        self.temperature = temperature

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:  # type: ignore
        completion = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=5000,
            top_p=1,
        )
        return completion.choices[0].message.content  # type: ignore

    @property
    def _llm_type(self) -> str:
        return "groq-llm"

    class Config:
        arbitrary_types_allowed = True


# === Load embedding model (reusable) ===
def get_embedding_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Get HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name=model_name)


# === Load FAISS Vector Store ===
def load_vectorstore(db_path: str, embedding_model=None):
    """
    Load a FAISS vectorstore from the given path.
    
    Args:
        db_path: Path to the FAISS vectorstore directory
        embedding_model: Optional embedding model (will create default if None)
    
    Returns:
        FAISS vectorstore object
    """
    if embedding_model is None:
        embedding_model = get_embedding_model()
    
    return FAISS.load_local(db_path, embedding_model, allow_dangerous_deserialization=True)


# === Custom Prompt Template ===
CUSTOM_PROMPT_TEMPLATE = """
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context> {context}

Questions:{query}
"""

custom_prompt = ChatPromptTemplate(
    [
        ("system", CUSTOM_PROMPT_TEMPLATE),
        ("human", ["context", "query"]),
    ]
)


# === Helper Functions ===
def format_docs(docs):
    """Convert retrieved docs into a single string context block."""
    try:
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception:
        return " ".join([getattr(d, "page_content", str(d)) for d in docs])


def build_rag_chain(retriever_obj, prompt_obj, llm_obj):
    """Build and return the RAG runnable chain."""
    rag_chain = (
        {"context": retriever_obj | format_docs, "query": RunnablePassthrough()}
        | prompt_obj
        | llm_obj
        | StrOutputParser()
    )
    return rag_chain


def generate_reply(
    message: str,
    vectorstore,  # NEW: Accept vectorstore as argument
    llm_obj=None,
    prompt_obj=None,
    summary: Optional[str] = None,
    top_k: int = 5
) -> str:
    """
    Generate a reply for the given message using the provided vectorstore.
    
    Args:
        message: User query string
        vectorstore: FAISS vectorstore object to use for retrieval
        llm_obj: Optional LLM object (will create default Groq LLM if None)
        prompt_obj: Optional prompt template (will use custom_prompt if None)
        summary: Optional summary context (not currently used)
        top_k: Number of documents to retrieve
    
    Returns:
        Generated reply string
    """
    if not isinstance(message, str) or not message.strip():
        return "Please provide a non-empty message."

    try:
        # Use default LLM if not provided
        if llm_obj is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return "❌ Error: GROQ_API_KEY not found in environment"
            llm_obj = GroqLLM(api_key=api_key)
        
        # Use default prompt if not provided
        if prompt_obj is None:
            prompt_obj = custom_prompt
        
        # Create retriever from vectorstore with top_k
        retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        
        # Build RAG chain
        rag_chain = build_rag_chain(retriever, prompt_obj, llm_obj)
        
        # Invoke chain with message
        result = rag_chain.invoke(message)
        
        if result is None:
            return "⚠️ No reply generated."
        return str(result)

    except Exception as e:
        logging.exception("generate_reply failed")
        return f"❌ Error generating reply: {str(e)}"


def main():
    """Test harness for the generate_reply wrapper."""
    print("=== RAG QUERY TEST ===")
    
    # Load vectorstore
    DB_FAISS_PATH = "../../database/vectorstore"
    embedding_model = get_embedding_model()
    
    try:
        print(f"Loading vectorstore from: {DB_FAISS_PATH}")
        vectorstore = load_vectorstore(DB_FAISS_PATH, embedding_model)
        print("✓ Vectorstore loaded successfully\n")
        
        # Initialize LLM
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ Error: GROQ_API_KEY not found")
            return
        
        llm = GroqLLM(api_key=api_key)
        
        # Get user query
        try:
            user_q = input("Enter your query (or press Enter to use default): ").strip()
        except Exception:
            user_q = ""

        if not user_q:
            user_q = "Give me a short summary of the key ideas from the context."

        print(f"\nQuery: {user_q}\n")

        # Generate reply with dynamic vectorstore
        reply = generate_reply(
            message=user_q,
            vectorstore=vectorstore,  # Pass vectorstore as argument
            llm_obj=llm,
            prompt_obj=custom_prompt,
            top_k=5
        )
        
        print("\n📘 FINAL RESPONSE:\n", reply)

    except KeyboardInterrupt:
        print("\nExiting test.")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()