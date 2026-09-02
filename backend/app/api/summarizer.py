import os
import shutil
import logging
from uuid import uuid4
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from app.core.config import UPLOAD_DIR
from app.models.schemas import SummarizeRequest, NoteModel
from app.core.database import create_note
from app.services.youtube import get_transcripts
from app.services.media_processor import process_media_file, extract_pdf_text
from app.services.summarizer import summarize_long_content
from app.services.vector_search import async_generate_and_save_embeddings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/summarize-yt")
async def summarize_youtube(req: SummarizeRequest, background_tasks: BackgroundTasks):
    """Direct local processing for YouTube summarization."""
    logs = ["📥 Fetching YouTube transcript..."]
    try:
        if req.transcript:
            transcripts = [item.dict() for item in req.transcript]
        elif req.url:
            transcripts = get_transcripts(req.url)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Provide either a transcript or a URL", "logs": logs}
            )

        logs.append(f"📄 Retrieved {len(transcripts)} transcript segments.")
        logs.append("🤖 Generating summary using Groq Compound...")

        summary = await summarize_long_content(transcripts)

        note_data = NoteModel(
            user_id=req.user_id,
            title=req.title or "YouTube Video",
            type="youtube",
            summary=summary,
            transcript=transcripts,
            source=req.url or "YouTube",
            embeddings=None,
            status="Completed"
        )

        logs.append("💾 Saving note to database...")
        saved_note = create_note(note_data)
        note_id = saved_note.get("id") or saved_note.get("_id")

        if note_id:
            text_for_embedding = " ".join([item.get("text", "") for item in transcripts if isinstance(item, dict)])
            if text_for_embedding.strip():
                logs.append("🧠 Scheduled local vector embedding computation in background.")
                background_tasks.add_task(async_generate_and_save_embeddings, str(note_id), text_for_embedding)

        logs.append("🚀 Done! Summary is ready.")

        return {
            "status": "success",
            "summary": summary,
            "note": saved_note,
            "logs": logs
        }
    except Exception as e:
        err_str = str(e)
        logger.error(f"Error in YouTube summarization: {err_str}")
        status_code = 413 if "413" in err_str else 500
        return JSONResponse(
            status_code=status_code,
            content={"error": f"Failed to summarize YouTube video: {err_str}", "logs": logs}
        )


@router.post("/summarize-media")
async def summarize_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    type: str = Form("media")
):
    """Direct local processing for Audio/Video media summarization."""
    logs = ["📥 Ingesting media file locally..."]
    try:
        if not file.filename:
            return JSONResponse(status_code=400, content={"error": "File name is required", "logs": logs})

        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".mp4", ".avi", ".mov", ".mkv", ".webm"]
        if file_ext not in allowed_extensions:
            return JSONResponse(status_code=400, content={"error": f"Unsupported file format: {file_ext}", "logs": logs})

        task_id = str(uuid4())
        user_dir = UPLOAD_DIR / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        filename = Path(file.filename).name
        local_file_path = str(user_dir / f"{task_id}_{filename}")

        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logs.append("🎧 Transcribing audio/video content with Faster-Whisper...")
        transcripts = process_media_file(local_file_path, filename)

        logs.append("🤖 Generating summary using Groq Compound...")
        summary = await summarize_long_content(transcripts)

        note_data = NoteModel(
            user_id=user_id,
            title=filename,
            type="media",
            summary=summary,
            transcript=transcripts,
            source=local_file_path,
            embeddings=None,
            task_id=task_id,
            status="Completed"
        )

        logs.append("💾 Saving note to database...")
        saved_note = create_note(note_data)
        note_id = saved_note.get("id") or saved_note.get("_id")

        if note_id:
            text_for_embedding = " ".join([item.get("text", "") for item in transcripts if isinstance(item, dict)])
            if text_for_embedding.strip():
                logs.append("🧠 Scheduled local vector embedding computation in background.")
                background_tasks.add_task(async_generate_and_save_embeddings, str(note_id), text_for_embedding)

        logs.append("🚀 Done! Summary is ready.")

        return {
            "status": "success",
            "summary": summary,
            "note": saved_note,
            "logs": logs
        }
    except Exception as e:
        err_str = str(e)
        logger.error(f"Error processing media: {err_str}")
        status_code = 413 if "413" in err_str else 500
        return JSONResponse(
            status_code=status_code,
            content={"error": f"Failed to process media file: {err_str}", "logs": logs}
        )


@router.post("/summarize-pdf")
async def summarize_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    type: str = Form("PDF")
):
    """Direct local processing for PDF document text summarization."""
    logs = ["📥 Uploading PDF file locally..."]
    try:
        if not file.filename:
            return JSONResponse(status_code=400, content={"error": "File name is required", "logs": logs})

        if Path(file.filename).suffix.lower() != ".pdf":
            return JSONResponse(status_code=400, content={"error": "Only PDF files are supported.", "logs": logs})

        task_id = str(uuid4())
        user_dir = UPLOAD_DIR / user_id
        user_dir.mkdir(parents=True, exist_ok=True)

        filename = Path(file.filename).name
        local_file_path = str(user_dir / f"{task_id}_{filename}")

        with open(local_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logs.append("📄 Extracting text using PyMuPDF...")
        extracted_text = extract_pdf_text(local_file_path)

        logs.append("🤖 Generating summary using Groq Compound...")
        summary = await summarize_long_content(extracted_text)

        note_data = NoteModel(
            user_id=user_id,
            title=filename,
            type="PDF",
            summary=summary,
            pdf_content=[extracted_text],
            source=local_file_path,
            embeddings=None,
            task_id=task_id,
            status="Completed"
        )

        logs.append("💾 Saving note to database...")
        saved_note = create_note(note_data)
        note_id = saved_note.get("id") or saved_note.get("_id")

        if note_id and extracted_text.strip():
            logs.append("🧠 Scheduled local vector embedding computation in background.")
            background_tasks.add_task(async_generate_and_save_embeddings, str(note_id), extracted_text)

        logs.append("🚀 Done! Summary is ready.")

        return {
            "status": "success",
            "summary": summary,
            "note": saved_note,
            "logs": logs
        }
    except Exception as e:
        err_str = str(e)
        logger.error(f"Error processing PDF: {err_str}")
        status_code = 413 if "413" in err_str else 500
        return JSONResponse(
            status_code=status_code,
            content={"error": f"Failed to process PDF: {err_str}", "logs": logs}
        )
