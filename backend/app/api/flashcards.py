import re
from fastapi import APIRouter, Body
from app.models.schemas import FlashcardRequest
from app.core.llm import get_groq_llm
from langchain_core.output_parsers import StrOutputParser

router = APIRouter()


@router.post("/summarize-flashcard")
async def summarize_for_flashcard(req: FlashcardRequest):
    """
    Extracts 6 concise bullet points for flashcards.
    First attempts zero-cost local parsing from summary; falls back to Groq if needed.
    """
    try:
        if not req.summary or not req.summary.strip():
            return {"error": "Summary is required"}

        # --- OPTIMIZATION: Zero-API Call Local Bullet Extraction ---
        lines = req.summary.strip().split("\n")
        extracted_bullets = []

        for line in lines:
            line = line.strip()
            # Check for markdown bullets or numbered items
            if line.startswith(("- ", "* ", "• ")) or (len(line) > 2 and line[0].isdigit() and line[1] in ".):"):
                cleaned = line.lstrip("0123456789.-*•) ").strip()
                # Ensure meaningful length (between 10 and 150 chars)
                if 10 <= len(cleaned) <= 150 and cleaned not in extracted_bullets:
                    extracted_bullets.append(cleaned)

        if len(extracted_bullets) >= 4:
            bullets = extracted_bullets[:6]
            return {
                "status": "success",
                "bullet_points": bullets,
                "count": len(bullets),
                "source": "local_parser"
            }

        # --- Fallback: Groq LLM API call if summary lacks formatted bullets ---
        llm = get_groq_llm(temperature=0.7)

        prompt = f"""
Extract exactly 6 key bullet points from the following summary. 
Each bullet point should be concise (max 15 words) and capture the main idea.
Format as a numbered list (1., 2., 3., etc).

Summary:
{req.summary}

Bullet Points:
"""

        chain = llm | StrOutputParser()
        response_text = await chain.ainvoke(prompt)

        if not response_text or not response_text.strip():
            return {"status": "error", "error": "No response from Groq"}

        bullet_points = []
        for line in response_text.strip().split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                cleaned = line.lstrip("0123456789.-•) ").strip()
                if cleaned:
                    bullet_points.append(cleaned)

        bullet_points = bullet_points[:6]

        return {
            "status": "success",
            "bullet_points": bullet_points,
            "count": len(bullet_points),
            "source": "groq_api"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.post("/prompts")
async def generate_prompts(request: dict = Body(...)):
    """
    Generates suggested questions based strictly on the summary.
    First attempts zero-cost local section/header parsing; falls back to Groq if needed.
    """
    try:
        summary = request.get("summary", "")
        if not summary or not summary.strip():
            return {"prompts": []}

        # --- OPTIMIZATION: Zero-API Call Local Question Generator ---
        headers = []
        for line in summary.strip().split("\n"):
            line = line.strip()
            if line.startswith("#"):
                clean_header = line.lstrip("#").strip()
                if clean_header and len(clean_header) > 3 and not any(k in clean_header.lower() for k in ["summary", "overview", "introduction", "conclusion"]):
                    headers.append(clean_header)

        if headers:
            questions = []
            for h in headers[:3]:
                questions.append({"text": f"What is {h}?"})
                questions.append({"text": f"Can you explain {h} in detail?"})
            return {"prompts": questions[:3], "source": "local_parser"}

        # --- Fallback: Groq LLM API Call ---
        llm = get_groq_llm(temperature=0.7)

        prompt = f"""Based on this summary strictly, generate 3 good questions a user might ask about the content. Do not include anything outside the summary.
Return only the questions, one per line, very short, without numbering or bullet points.

Summary:
{summary}

Questions:
"""

        chain = llm | StrOutputParser()
        questions_text = await chain.ainvoke(prompt)

        if not questions_text or not questions_text.strip():
            return {"prompts": []}

        questions = [q.strip() for q in questions_text.strip().split("\n") if q.strip()]
        prompts = [{"text": q} for q in questions[:3]]

        return {"prompts": prompts, "source": "groq_api"}
    except Exception as e:
        return {"prompts": []}
