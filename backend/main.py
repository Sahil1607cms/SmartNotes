from fastapi import FastAPI, Query, HTTPException
from fastapi import UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

from youtube_transcript_api._errors import IpBlocked, NoTranscriptFound
from utils.youtube_transcript import get_transcripts
from services.YT_summarizer import summarize_long_transcript
from services.PDF_summarizer import summarize_long_pdf
from services.Media_summarizer import summarize_long_transcript as summarize_media_transcript
from services.media_summariser.process_media import process_media_file

from database.historySchema import NoteModel, NoteResponseModel
from database.crud import create_note, get_notes_by_user

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Schemas
class YouTubeRequest(BaseModel):
    url: str

class TranscriptItem(BaseModel):
    time: str
    text: str

class SummarizeRequest(BaseModel):
    user_id: str
    title: str
    type: str = "youtube"  
    url: Optional[str] = None
    transcript: Optional[List[TranscriptItem]] = None

# --------------------------
# YouTube Transcript API route for viewPage component transcript displaying
# --------------------------
@app.get("/transcript/")
def transcript_api(url: str):
    try:
        transcripts = get_transcripts(url)
        return {"transcript": transcripts}
    except IpBlocked:
        return {"error": "Your IP is blocked by YouTube. Try again later or from a different network."}
    except NoTranscriptFound:
        return {"error": "Transcript not found for this video."}
    except Exception as e:
        return {"error": str(e)}

# --------------------------
# Summarize & Save Note YOUTUBE
# --------------------------
@app.post("/summarize-yt")
async def summarize_youtube_and_save(req: SummarizeRequest):
    try:
        if req.transcript:
            transcripts = [item.dict() for item in req.transcript]
        elif req.url:
            transcripts = get_transcripts(req.url)
        else:
            return {"error": "Provide either a transcript or a URL"}

        summary = await summarize_long_transcript(transcripts)

        note_data = NoteModel(
            user_id=req.user_id,
            title=req.title,
            type=req.type,
            summary=summary,
            transcript=transcripts,
            source=req.url or "uploaded transcript"
        )

        saved_note = create_note(note_data)

        return {"summary": summary, "note": saved_note}

    except Exception as e:
        return {"error": str(e)}

# --------------------------
# Summarize & Save Note MEDIA (Audio/Video)
# --------------------------
@app.post("/summarize-media")
async def summarize_media_and_save(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    type: str = Form("media")
):
    """
    Process uploaded audio/video file: transcribe and summarize.
    """
    import tempfile
    
    temp_file_path = None
    try:
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        if file_ext not in allowed_extensions:
            return {"error": f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}"}
        
        # Save uploaded file temporarily
        file_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name
        
        print(f"Processing media file: {file.filename}")
        
        # Process media file (transcribe)
        transcripts = await process_media_file(temp_file_path, file.filename)
        
        if not transcripts or len(transcripts) == 0:
            return {"error": "Failed to transcribe the media file. Please ensure the file contains audio."}
        
        # Summarize transcript
        summary = await summarize_media_transcript(transcripts)
        
        # Save to database
        note_data = NoteModel(
            user_id=user_id,
            title=file.filename,
            type=type,
            summary=summary,
            transcript=transcripts,
            source="Uploaded media"
        )
        
        saved_note = create_note(note_data)
        
        return {"summary": summary, "note": saved_note}
    
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        print(f"Error processing media file: {str(e)}")
        return {"error": f"Failed to process media file: {str(e)}"}
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass


# --------------------------
# Summarize & Save Note PDF
# --------------------------
@app.post("/summarize-pdf")
async def summarize_PDF_and_save(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    type: str = Form("PDF")
):
    try:
        import tempfile
        from langchain_community.document_loaders import PyPDFLoader
        temp_pdf_path = None
        try:
            pdf_bytes = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(pdf_bytes)
                temp_pdf_path = temp_pdf.name
            print("path of pdf :" , temp_pdf_path)
            pdf_name = file.filename 
            loader = PyPDFLoader(temp_pdf_path)
            pdf_docs = loader.load()
            pdf_text_only = [doc.page_content for doc in pdf_docs]
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except OSError:
                    pass

        summary = await summarize_long_pdf(pdf_docs)

        note_data = NoteModel(
            user_id=user_id,
            title=pdf_name,
            type=type,
            summary=summary,
            pdf_content=pdf_text_only,
            source="Uploaded PDF"
        )

        saved_note = create_note(note_data)

        return {"summary": summary, "note": saved_note}

    except Exception as e:
        return {"error": str(e)}
    
# --------------------------
# Get Notes by User
# --------------------------
@app.get("/notes/", response_model=List[NoteResponseModel])
def get_user_notes(user_id: str = Query(..., description="ID of the logged-in user")):
    """
    Fetch all saved notes for a specific user
    """
    try:
        notes = get_notes_by_user(user_id)  # returns list of dicts
        # Return as list of NoteResponseModel for FastAPI serialization
        response_notes = [
            NoteResponseModel(**note) for note in notes
        ]
        return response_notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


