import logging
import numpy as np
from typing import List, Dict, Any, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.database import notes_collection, get_note_by_id
from app.core.llm import get_groq_llm

logger = logging.getLogger(__name__)

# Global reusable embedding model instance
_EMBEDDING_MODEL = None


def get_embedding_model():
    """
    Returns cached HuggingFace Embedding Model instance.
    Loads model once into RAM and reuses across requests.
    """
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        logger.info("⚡ Pre-loading HuggingFace Embedding Model (sentence-transformers/all-MiniLM-L6-v2)...")
        _EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _EMBEDDING_MODEL


def generate_embeddings(text: str) -> Optional[List[Dict[str, Any]]]:
    """
    Chunks input text and computes 384-dimensional dense vectors using all-MiniLM-L6-v2.
    Returns list of dicts: [{'text': chunk_text, 'embedding': [floats]}]
    """
    try:
        if not text or not text.strip():
            return None

        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
        docs = splitter.create_documents([text])
        if not docs:
            return None

        model = get_embedding_model()
        chunks = [doc.page_content for doc in docs]
        vectors = model.embed_documents(chunks)

        serializable = []
        for chunk_text, vec in zip(chunks, vectors):
            if vec is not None:
                serializable.append({
                    "text": chunk_text,
                    "embedding": [float(x) for x in vec]
                })

        return serializable
    except Exception as e:
        logger.error(f"Error generating vector embeddings: {e}")
        return None


def async_generate_and_save_embeddings(note_id: str, text: str):
    """
    Asynchronous background task that computes dense vector embeddings for a saved note
    and updates the MongoDB document without blocking the HTTP summary response.
    """
    try:
        if not text or not text.strip() or not note_id:
            return

        logger.info(f"🧠 [Background] Generating vector embeddings for Note ID: {note_id}...")
        embeddings = generate_embeddings(text)

        if embeddings:
            from bson.objectid import ObjectId
            notes_collection.update_one(
                {"_id": ObjectId(note_id)},
                {"$set": {"embeddings": embeddings}}
            )
            logger.info(f"✅ [Background] Successfully stored {len(embeddings)} vector embeddings for Note ID: {note_id}")
    except Exception as e:
        logger.error(f"❌ [Background Error] Failed to generate/store embeddings for Note ID {note_id}: {e}")


def search_vector_context(message: str, note_id: Optional[str] = None, summary: Optional[str] = None) -> tuple[str, str]:
    """
    Enhanced Dual-Retrieval Vector Engine:
    1. Attempts MongoDB Atlas native $vectorSearch.
    2. Falls back to in-memory NumPy cosine similarity matching with top-k scoring.
    3. Falls back to Note Summary or Note Content.
    Returns: (context_text, retrieval_method)
    """
    if not message or not message.strip():
        return "", "empty_query"

    model = get_embedding_model()
    query_vector = model.embed_query(message)

    context_text = ""
    retrieval_method = None

    if note_id:
        note = get_note_by_id(note_id)

        # 1. Attempt MongoDB Atlas $vectorSearch Aggregation
        try:
            from bson.objectid import ObjectId
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embeddings.embedding",
                        "queryVector": query_vector,
                        "numCandidates": 100,
                        "limit": 4,
                        "filter": {"_id": ObjectId(note_id)}
                    }
                },
                {
                    "$project": {
                        "embeddings": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            cursor = notes_collection.aggregate(pipeline)
            results = list(cursor)

            if results:
                chunks_list = []
                for doc in results:
                    for item in doc.get("embeddings", []):
                        if isinstance(item, dict) and "text" in item and item["text"].strip():
                            chunks_list.append(item["text"].strip())
                if chunks_list:
                    context_text = "\n\n".join(chunks_list[:4])
                    retrieval_method = "mongo_vectorSearch"
                    logger.info("✅ Vector context retrieved via MongoDB Atlas $vectorSearch")
        except Exception as vs_err:
            logger.info(f"MongoDB $vectorSearch unavailable ({vs_err}). Using local NumPy vector search...")

        # 2. Local In-Memory NumPy Cosine Similarity Search
        if not context_text and note and note.get("embeddings"):
            try:
                embeddings_list = note["embeddings"]
                query_arr = np.array(query_vector, dtype=np.float32)
                query_norm = np.linalg.norm(query_arr) + 1e-8

                scored_chunks = []
                for item in embeddings_list:
                    if isinstance(item, dict) and "embedding" in item:
                        raw_vec = item["embedding"]
                        stored_arr = np.array(raw_vec, dtype=np.float32)

                        if len(stored_arr) == len(query_arr):
                            similarity = np.dot(stored_arr, query_arr) / (
                                np.linalg.norm(stored_arr) * query_norm
                            )
                            chunk_text = item.get("text", "").strip()
                            if chunk_text:
                                scored_chunks.append((float(similarity), chunk_text))

                if scored_chunks:
                    scored_chunks.sort(key=lambda x: x[0], reverse=True)
                    top_chunks = [text for _, text in scored_chunks[:4]]
                    context_text = "\n\n".join(top_chunks)
                    retrieval_method = "numpy_cosine_similarity"
                    logger.info(f"✅ Vector context retrieved via NumPy Cosine Similarity (Top score: {scored_chunks[0][0]:.4f})")
            except Exception as numpy_err:
                logger.error(f"NumPy vector search error: {numpy_err}")

        # 3. Fallback to Note Summary
        if not context_text and summary:
            context_text = summary
            retrieval_method = "summary_fallback"

        # 4. Fallback to Note Raw Content
        if not context_text and note and note.get("summary"):
            context_text = note["summary"]
            retrieval_method = "note_summary_fallback"

    return context_text, (retrieval_method or "none")


def format_chat_history(
    history: List[Dict[str, Any]],
    max_messages: int = 4
) -> str:
    """Formats the last max_messages (4) chat items into a conversational memory context block."""
    if not isinstance(history, list) or not history:
        return "None"

    recent = history[-max_messages:]
    formatted = []

    for msg in recent:
        if not isinstance(msg, dict):
            continue
        role = "User" if msg.get("from") == "user" else "Assistant"
        text = str(msg.get("text", "")).strip()

        if text:
            formatted.append(f"{role}: {text}")

    return "\n".join(formatted) if formatted else "None"


RAG_PROMPT_TEMPLATE = """Use the retrieved context and recent conversation history to answer the user's current question accurately.

Retrieved Context:
{context}

Recent Conversation:
{chat_history}

Current User Question:
{question}

Answer:"""


async def generate_rag_reply(
    message: str,
    note_id: Optional[str] = None,
    summary: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Generates a grounded answer for user question using vector context, recent chat history, & Groq Compound."""
    context_text, retrieval_method = search_vector_context(message, note_id=note_id, summary=summary)

    if not context_text:
        return {
            "reply": "I don't have enough context to answer your question. Please ensure the note has been processed and saved.",
            "context_source": "none"
        }

    formatted_history = format_chat_history(history or [], max_messages=4)

    if history and isinstance(history, list):
        valid_msgs = [m for m in history if isinstance(m, dict) and m.get("text")]
        recent_count = min(len(valid_msgs), 4)
        if recent_count > 0:
            logger.info(f"💬 Using {recent_count} recent chat message(s) for conversational memory context.")

    llm = get_groq_llm(temperature=0.3, max_tokens=2048)
    prompt = PromptTemplate(
        template=RAG_PROMPT_TEMPLATE,
        input_variables=["context", "chat_history", "question"]
    )
    chain = prompt | llm | StrOutputParser()

    try:
        reply = await chain.ainvoke({
            "context": context_text,
            "chat_history": formatted_history,
            "question": message
        })
        return {
            "reply": reply.strip(),
            "context_source": retrieval_method
        }
    except Exception as e:
        logger.error(f"Error generating RAG reply: {e}")
        return {"reply": f"❌ Error generating reply: {str(e)}", "context_source": retrieval_method}
