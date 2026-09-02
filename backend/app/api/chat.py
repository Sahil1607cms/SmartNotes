from fastapi import APIRouter, Body
from app.services.vector_search import generate_rag_reply

router = APIRouter()


@router.post("/chat")
async def chat_with_rag(request: dict = Body(...)):
    """
    RAG Chat endpoint powered by dense local HuggingFace embeddings
    and Groq Compound LLM with conversational memory.
    """
    try:
        message = request.get("message", "").strip()
        summary = request.get("summary", "").strip()
        note_id = request.get("note_id", "") or request.get("videoId", "")
        history = request.get("history", [])

        if not isinstance(history, list):
            history = []

        if not message:
            return {"reply": "Please ask a valid question."}

        res = await generate_rag_reply(
            message=message,
            note_id=note_id,
            summary=summary,
            history=history
        )
        return res
    except Exception as e:
        return {"reply": f"❌ Error: {str(e)}", "context_source": "none"}
