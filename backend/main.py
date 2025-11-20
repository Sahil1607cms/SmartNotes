from fastapi import FastAPI, Query, HTTPException, Body, Response
from fastapi import UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from groq import Groq
from bson.objectid import ObjectId

from youtube_transcript_api._errors import IpBlocked, NoTranscriptFound
from utils.youtube_transcript import get_transcripts
from services.YT_summarizer import summarize_long_transcript
from services.PDF_summarizer import summarize_long_pdf
from services.Media_summarizer import summarize_long_transcript as summarize_media_transcript
from services.media_summariser.process_media import process_media_file
from services.media_summariser.ragvideo2 import generate_reply

from database.historySchema import NoteModel, NoteResponseModel
from database.crud import create_note, get_notes_by_user

from services.media_summariser.embed import create_embeddings

import tempfile

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

class FlashcardRequest(BaseModel):
    summary: str

class ChatRequest(BaseModel):
    message: str
    summary: Optional[str] = None
    videoId: str
    
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
        
        text_for_embedding = " ".join([item["text"] for item in transcripts])
        
        summary = await summarize_long_transcript(transcripts)
        
        embedding_reference = None
        embeddings = None
        try:
            embeddings = create_embeddings(text_for_embedding)
            if embeddings:
                import uuid
                embedding_reference = f"yt_{uuid.uuid4().hex[:8]}"
                print(f"✓ Embeddings created successfully with reference: {embedding_reference}")
            else:
                print("⚠ Embeddings returned None, proceeding without embedding storage")
        except Exception as embedding_error:
            print(f"⚠ Error creating embeddings: {str(embedding_error)}")

        note_data = NoteModel(
            user_id=req.user_id,
            title=req.title,
            type=req.type,
            summary=summary,
            transcript=transcripts,
            source=req.url or "uploaded transcript",
            embeddings=embeddings
        )

        saved_note = create_note(note_data)

        # Avoid returning potentially large embeddings payload to the frontend.
        response_note = dict(saved_note)
        response_note.pop("embeddings", None)

        return {
            "summary": summary,
            "note": response_note,
            "embeddings_status": "success" if embedding_reference else "skipped",
            "id": saved_note.get("id")
        }

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
    import tempfile
    temp_file_path = None
    try:
        if not file.filename:
            return {"error": "File name is required"}

        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = [
            ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac",
            ".mp4", ".avi", ".mov", ".mkv", ".webm"
        ]

        if file_ext not in allowed_extensions:
            return {"error": f"Unsupported file format: {file_ext}. Supported formats: {', '.join(allowed_extensions)}"}

        # Save uploaded file temporarily
        file_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        print(f"Processing media file: {file.filename}")

        transcripts = await process_media_file(temp_file_path, file.filename)

        if not transcripts or len(transcripts) == 0:
            return {"error": "Failed to transcribe the media file. Please ensure the file contains audio."}
        
        else :
            print("Transcript length is : ", len(transcripts))
            text_for_embedding = " ".join([item["text"] for item in transcripts])
    
        # Summarize transcript
        summary = await summarize_media_transcript(transcripts)
        
        embedding_reference = None
        embeddings = None
        try:
            embeddings = create_embeddings(text_for_embedding)
            if embeddings:
                import uuid
                embedding_reference = f"yt_{uuid.uuid4().hex[:8]}"
                print(f"✓ Embeddings created successfully with reference: {embedding_reference}")
            else:
                print("⚠ Embeddings returned None, proceeding without embedding storage")
        except Exception as embedding_error:
            print(f"⚠ Error creating embeddings: {str(embedding_error)}")

        note_data = NoteModel(
            user_id=user_id,
            title=file.filename,
            type=type,
            summary=summary,
            transcript=transcripts,
            source="Uploaded media",
            embeddings=embeddings
        )

        saved_note = create_note(note_data)
        response_note = dict(saved_note)
        response_note.pop("embeddings", None)

        return {
            "summary": summary,
            "note": response_note,
            "embeddings_status": "success" if embedding_reference else "skipped",
            "id": saved_note.get("id")
        }

    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        print(f"Error processing media file: {str(e)}")
        return {"error": f"Failed to process media file: {str(e)}"}

    finally:
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
        
        from langchain_community.document_loaders import PyPDFLoader
        temp_pdf_path = None
        try:
            if not file.filename:
                return {"error": "File name is required"}
            pdf_bytes = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(pdf_bytes)
                temp_pdf_path = temp_pdf.name
            print("path of pdf :" , temp_pdf_path)
            pdf_name = file.filename 
            loader = PyPDFLoader(temp_pdf_path)
            pdf_docs = loader.load()
            pdf_text_only = [doc.page_content for doc in pdf_docs]
            print(pdf_text_only)
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


# --------------------------
# Generate Flashcard Bullet Points from Summary
# --------------------------
@app.post("/summarize-flashcard")
async def summarize_for_flashcard(req: FlashcardRequest):
    try:
        if not req.summary or req.summary.strip() == "":
            return {"error": "Summary is required"}
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"error": "Groq API key not configured"}
        
        client = Groq(api_key=groq_api_key)
        
        prompt = f"""
Extract exactly 6 key bullet points from the following summary. 
Each bullet point should be concise (max 15 words) and capture the main idea.
Format as a numbered list (1., 2., 3., etc).

Summary:
{req.summary}

Bullet Points:
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        bullet_points_text = response.choices[0].message.content
        if not bullet_points_text:
            return {"status": "error", "error": "No response from Groq"}
        
        bullet_points_text = bullet_points_text.strip()
        
        # Parse bullet points into a list
        lines = bullet_points_text.split("\n")
        bullet_points = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                # Remove numbering or bullet markers
                cleaned = line.lstrip("0123456789.-•) ").strip()
                if cleaned:
                    bullet_points.append(cleaned)
        
        # Ensure we have exactly 6 (or as many as extracted)
        bullet_points = bullet_points[:6]
        
        return {
            "status": "success",
            "bullet_points": bullet_points,
            "count": len(bullet_points)
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


# --------------------------
# Generate Suggested Prompts from Summary
# --------------------------
@app.post("/prompts")
async def generate_prompts(request: dict = Body(...)):
    try:
        summary = request.get("summary", "")
        if not summary or not summary.strip():
            return {"prompts": []}
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"prompts": []}
        
        client = Groq(api_key=groq_api_key)
        
        prompt = f"""Based on this summary, generate 3 good questions a user might ask about the content.
Return only the questions, one per line, very short, without numbering or bullet points.

Summary:
{summary}

Questions:
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        questions_text = response.choices[0].message.content
        if not questions_text:
            return {"prompts": []}
        
        questions_text = questions_text.strip()
        
        # Split by newlines and clean
        questions = [q.strip() for q in questions_text.split("\n") if q.strip()]
        
        # Convert to prompt objects
        prompts = [{"text": q} for q in questions[:4]]
        
        return {"prompts": prompts}
    
    except Exception as e:
        print(f"Error generating prompts: {str(e)}")
        return {"prompts": []}


# --------------------------
# Chat QnA with Embeddings & RAG
# --------------------------
@app.post("/chat")
async def chat_with_rag(request: dict = Body(...)):
    try:
        from database.crud import notes_collection
        from langchain_huggingface import HuggingFaceEmbeddings
        import numpy as np
        
        message = request.get("message", "").strip()
        summary = request.get("summary", "").strip()
        note_id = request.get("note_id", "").strip()
        
        if not message:
            return {"reply": "Please ask a question."}
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"reply": "⚠️ API key not configured."}
        
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        question_embedding = embedding_model.embed_query(message)
        
        # i am retrieving embeddings from mongo db here 
        context_text = ""
        if note_id:
            try:
                note = notes_collection.find_one({"_id": ObjectId(note_id)})
                if note and note.get("embeddings"):
                    embeddings_list = note["embeddings"]
                    
                    # Compute similarity scores
                    scores = []
                    for emb_item in embeddings_list:
                        if isinstance(emb_item, dict) and "embedding" in emb_item:
                            stored_embedding = np.array(emb_item["embedding"])
                            question_vec = np.array(question_embedding)
                            
                            # Cosine similarity
                            similarity = np.dot(stored_embedding, question_vec) / (
                                np.linalg.norm(stored_embedding) * np.linalg.norm(question_vec) + 1e-8
                            )
                            scores.append((similarity, emb_item.get("text", "")))
                    
                    # Sort by similarity and get top-3 chunks
                    scores.sort(reverse=True, key=lambda x: x[0])
                    top_chunks = [text for _, text in scores[:3]]
                    context_text = "\n\n".join(top_chunks)
            except Exception as e:
                print(f"⚠️ Error retrieving embeddings from note_id: {str(e)}")
        
        # falling back to summary in csae summary generation has failed
        if not context_text and summary:
            context_text = summary
        
        if not context_text:
            return {"reply": "No context available to answer from."}
        
        rag_prompt = f"""Answer the following question based ONLY on the provided context in english only strictly.
If the answer is not in the context, say "I don't have that information in the provided context."

Context:
{context_text}

Question: {message}

Answer:
"""
        
        client = Groq(api_key=groq_api_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": rag_prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        if not reply:
            reply = "⚠️ No response generated."
        
        return {"reply": reply.strip()}
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"reply": f"❌ Error: {str(e)}"}