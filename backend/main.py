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
from database.crud import create_note, get_notes_by_user, delete_note_by_id

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
            "id": saved_note.get("_id")
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

        else:
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
            "id": saved_note.get("_id")
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
            print("path of pdf :", temp_pdf_path)
            pdf_name = file.filename
            loader = PyPDFLoader(temp_pdf_path)
            pdf_docs = loader.load()
            pdf_text_only = [doc.page_content for doc in pdf_docs]

            clean_text = "".join(pdf_text_only)
            clean_text = clean_text.replace("\n", " ")
        finally:
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.remove(temp_pdf_path)
                except OSError:
                    pass

        summary = await summarize_long_pdf(pdf_docs)

        embedding_reference = None
        embeddings = None
        try:
            embeddings = create_embeddings(clean_text)
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
            title=pdf_name,
            type=type,
            summary=summary,
            pdf_content=pdf_text_only,
            source="Uploaded PDF",
            embeddings=embeddings
        )

        saved_note = create_note(note_data)
        response_note = dict(saved_note)
        response_note.pop("embeddings", None)

        return {
            "summary": summary,
            "note": response_note,
            "embeddings_status": "success" if embedding_reference else "skipped",
            "id": saved_note.get("_id")
        }

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
# Delete Note by ID
# --------------------------
@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    """
    Delete a specific note by its ID
    """
    try:
        success = delete_note_by_id(note_id)
        if success:
            return {"status": "success", "message": "Note deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Note not found")
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

        prompt = f"""Based on this summary strictly, generate 3 good questions a user might ask about the content, dont include anything outside the summary.
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

        print(f"Note ID: {note_id}")
        print(f"Summary: {summary}")
        print(f"Message: {message}")

        if not message:
            return {"reply": "Please ask a question."}

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"reply": "⚠️ API key not configured."}

        # Initialize embedding model
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("Model loaded")

        question_embedding = embedding_model.embed_query(message)
        print("Question embeddings generated")

        # Retrieve embeddings from MongoDB
        context_text = ""
        retrieval_method = None

        if note_id:
            try:
                note = notes_collection.find_one({"_id": ObjectId(note_id)})
                print(f"Note found: {note is not None}")

                if note and note.get("embeddings"):
                    embeddings_list = note["embeddings"]
                    print(f"Found {len(embeddings_list)} embedding chunks")

                    # Compute similarity scores
                    scores = []
                    for emb_item in embeddings_list:
                        if isinstance(emb_item, dict) and "embedding" in emb_item:
                            # Extract the embedding from MongoDB's extended JSON format
                            raw_embedding = emb_item["embedding"]

                            # Handle MongoDB's $numberDouble format
                            if isinstance(raw_embedding, list):
                                # Extract numeric values from $numberDouble wrappers
                                stored_embedding = np.array([
                                    float(val["$numberDouble"]) if isinstance(val, dict) and "$numberDouble" in val
                                    else float(val) #type: ignore
                                    for val in raw_embedding
                                ], dtype=np.float32)

                                print(f"Converted embedding shape: {stored_embedding.shape}")
                            else:
                                stored_embedding = np.array(raw_embedding)

                            question_vec = np.array(question_embedding)

                            # Ensure both vectors have the same dimension
                            if len(stored_embedding) != len(question_vec):
                                print(
                                    f"⚠️ Dimension mismatch: stored={len(stored_embedding)}, question={len(question_vec)}")
                                continue

                            # Cosine similarity
                            similarity = np.dot(stored_embedding, question_vec) / (
                                    np.linalg.norm(stored_embedding) * np.linalg.norm(question_vec) + 1e-8
                            )

                            text_chunk = emb_item.get("text", "").strip()
                            if text_chunk:  # Only add non-empty chunks
                                scores.append((similarity, text_chunk))
                                print(f"Similarity: {similarity:.4f}")

                    if scores:
                        # Sort by similarity and get top-3 chunks
                        scores.sort(reverse=True, key=lambda x: x[0])
                        top_chunks = [text for _, text in scores[:3]]
                        context_text = "\n\n".join(top_chunks)
                        retrieval_method = "embeddings"
                        print(f"Retrieved {len(top_chunks)} chunks via embeddings")
                        print(f"Top similarity score: {scores[0][0]:.4f}")
                    else:
                        print("No valid embeddings found after processing")

                # Fallback to summary if embeddings didn't work
                if not context_text and summary:
                    context_text = summary
                    retrieval_method = "summary"
                    print("Falling back to summary")

                # Last resort: use full note content if available
                if not context_text and note and note.get("content"):
                    context_text = note["content"]
                    retrieval_method = "full_content"
                    print("Falling back to full note content")

            except Exception as e:
                print(f"⚠️ Error retrieving from note_id: {str(e)}")
                import traceback
                traceback.print_exc()

        # Final check for context
        if not context_text:
            return {
                "reply": "I don't have any context to answer your question. Please make sure:\n"
                         "1. A valid note_id is provided, or\n"
                         "2. The note has been processed with embeddings, or\n"
                         "3. A summary is available."
            }

        # Build RAG prompt
        rag_prompt = f"""Use the following context to answer the question. If the information needed to answer is not present in the context, respond that the context does not include the answer"

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

        print(f"Response generated using {retrieval_method}")

        return {
            "reply": reply.strip(),
            "context_source": retrieval_method  # Optional: helps with debugging
        }

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"reply": f"❌ Error: {str(e)}"}