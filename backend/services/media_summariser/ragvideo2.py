# Standard / environment
import os
from dotenv import load_dotenv

# Typing helpers
from typing import List, Optional

# Groq SDK (used by the Groq LLM wrapper)
from groq import Groq

# LangChain core pieces
from langchain_core.prompts import ChatPromptTemplate                # prompt templates
from langchain_core.language_models import LLM  # base class for custom LLM wrapper
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
#from langchain.schema import Document                       # Document type returned by retriever

# Embeddings + Vectorstore (FAISS)
from langchain_huggingface import HuggingFaceEmbeddings     # embedding provider used to build / load index
from langchain_community.vectorstores import FAISS           # load_local / as_retriever

# Pydantic helper used if you create a custom LLM wrapper with a private client
from pydantic import PrivateAttr

# Optional — useful for debugging / basic HTTP calls if you need to fall back
import logging
import requests
import json



GROQ_RATE_LIMIT = 100  # Maximum Groq API calls per minute
GEMINI_RATE_LIMIT = 60  # Maximum Gemini API calls per minute

load_dotenv()

# === Load FAISS Vector Store ===
from langchain_huggingface import HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DB_FAISS_PATH = "../../database/vectorstore"
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)


# === Wrap Groq Chat API into LangChain-compatible class ===


class GroqLLM(LLM):
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.6
    _client: Groq = PrivateAttr()  # This is how we define a private client field

    def __init__(self, api_key: str, model_name: Optional[str] = None, temperature: float = 0.6):
        super().__init__()
        self._client = Groq(api_key=api_key) 
        self.model = model_name or self.model
        self.temperature = temperature

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        completion = self._client.chat.completions.create(  #  Use _client here
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=5000,
            top_p=1,
        )
        return completion.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "groq-llm"

    class Config:
        arbitrary_types_allowed = True

# === Instantiate Groq Model ===
llm = GroqLLM(api_key=os.getenv("GROQ_API_KEY"))
#from langchain.prompts import PromptTemplate

# Externalized custom prompt definition
CUSTOM_PROMPT_TEMPLATE = """

Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context> {context}

Questions:{query}

"""

custom_prompt = ChatPromptTemplate(
    [
    ("system",CUSTOM_PROMPT_TEMPLATE),
    ("human",["context", "query"]),]
)


# === QA Chain ===
# qa_chain = create_retrieval_chain(
#     llm=llm,
#     chain_type="stuff",
#     retriever=db.as_retriever(),
#     return_source_documents=False
    
# )


retriever=db.as_retriever()
user_input=input("Enter your query   ")

# === Final Call ===
try:
    # Create a RAG chain using modern LangChain runables
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])
    
    # Build RAG chain: retriever -> format docs -> prompt -> llm -> output
    rag_chain = (
        {"context": retriever | format_docs, "query": RunnablePassthrough()}
        | custom_prompt
        | llm
        | StrOutputParser()
    )
    
    response = rag_chain.invoke(user_input)
    print("\n📘 FINAL RESPONSE:\n", response)
    
except Exception as e:
    print(f"❌ Error during query processing: {str(e)}")
    import traceback
    traceback.print_exc()



# === Wrapper + Test ===

def format_docs(docs):
    """Helper to convert retrieved docs (list) into a single string context block."""
    # docs are expected to have .page_content
    try:
        return "\n\n".join([doc.page_content for doc in docs])
    except Exception:
        # defensive fallback
        return " ".join([getattr(d, "page_content", str(d)) for d in docs])

def build_rag_chain(retriever_obj, prompt_obj, llm_obj):
    """
    Build and return the RAG runnable chain used to answer queries.
    This mirrors the chain in your snippet.
    """
    # We use RunnablePassthrough via the prompt and LLM objects already configured
    # The retriever is used as retriever_obj | format_docs in the same style as your snippet.
    rag_chain = (
        {"context": retriever_obj | format_docs, "query": RunnablePassthrough()}
        | prompt_obj
        | llm_obj
        | StrOutputParser()
    )
    return rag_chain


def generate_reply(message: str, summary: Optional[str] = None, collection: str = "default", top_k: int = 5) -> str:
    """
    Final wrapper to generate a reply string for `message`.
    - Uses the global `retriever`, `custom_prompt`, and `llm` defined earlier.
    - Returns the LLM text output (or an error string).
    - Replace or extend with collection-specific loading logic if you persist multiple vectorstores.
    """
    if not isinstance(message, str) or not message.strip():
        return "Please provide a non-empty message."

    try:
        # Optional: if your retriever supports setting k, do so here (depends on implementation).
        # Many retrievers accept search parameters at call-time; if not, you can use as-is.
        # Example (pseudo): retriever_obj.search_kwargs = {"k": top_k}
        # For the FAISS retriever from your snippet, you can pass top_k via retriever.get_relevant_documents(...) if available.
        # We'll just build the chain and invoke with message (the retriever is bound to the chain).
        rag_chain = build_rag_chain(retriever, custom_prompt, llm)

        # If you want to include `summary` in the prompt, you could modify the ChatPromptTemplate or
        # pass a combined query like f"{summary}\n\nUser: {message}". For now we pass `message` directly.
        # If your prompt expects both 'context' and 'query' keys, the chain will handle the retrieval -> formatting -> prompt.
        result = rag_chain.invoke(message)

        # Ensure result is a string
        if result is None:
            return "⚠️ No reply generated."
        return str(result)

    except Exception as e:
        logging.exception("generate_reply failed")
        return f"❌ Error generating reply: {str(e)}"


def main():
    """
    Test harness for the generate_reply wrapper.
    - Uses a sample query or interactive input.
    - Prints the result to stdout.
    - Also shows the example uploaded file path (from session) used as a sample source_url.
    """
    # Example: path to the file uploaded earlier in this session (keeps developer-provided path)
    uploaded_file_path = "/mnt/data/444d529c-83c4-4eb0-9a9c-c7a0167029a1.png"

    print("=== RAG QUERY TEST ===")
    try:
        # Try interactive input first; fall back to a default query
        try:
            user_q = input("Enter your query (or press Enter to use default): ").strip()
        except Exception:
            user_q = ""

        if not user_q:
            user_q = "Give me a short summary of the key ideas from the context."

        print(f"\nUsing sample uploaded file (as sample source_url): {uploaded_file_path}")
        print(f"Query: {user_q}\n")

        reply = generate_reply(user_q, summary=None, collection="default", top_k=5)
        print("\n📘 FINAL RESPONSE:\n", reply)

    except KeyboardInterrupt:
        print("\nExiting test.")
    except Exception as e:
        print("Test failed:", str(e))


if __name__ == "__main__":
    main()


