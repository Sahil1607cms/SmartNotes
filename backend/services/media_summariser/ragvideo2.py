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





