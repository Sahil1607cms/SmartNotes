from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class TranscriptItem(BaseModel):
    time: str
    text: str


class NoteModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    title: str
    type: str  # "media", "PDF", "youtube"
    summary: str
    transcript: Optional[List[Dict[str, Any]]] = None
    pdf_content: Optional[List[str]] = None
    embeddings: Optional[List[Dict[str, Any]]] = None
    source: Optional[str] = None
    task_id: Optional[str] = None
    status: str = "Completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class NoteResponseModel(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    title: str
    type: str
    summary: str
    transcript: Optional[List[Dict[str, Any]]] = None
    pdf_content: Optional[List[str]] = None
    source: Optional[str] = None
    task_id: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        populate_by_name = True


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
    note_id: Optional[str] = None
