import os
from langchain_groq import ChatGroq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

def get_groq_llm(temperature: float = 0.4, max_tokens: int = 2048) -> ChatGroq:
    """Central factory for Groq ChatGroq instances using openai/gpt-oss-20b."""
    api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")
    
    model_name = GROQ_MODEL or "openai/gpt-oss-20b"

    return ChatGroq(
        model=model_name,
        groq_api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        max_retries=1
    )
