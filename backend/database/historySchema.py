from pydantic import BaseModel
from typing import Optional,List,Any,Dict
from datetime import datetime

class NoteModel(BaseModel):
    user_id: str
    title: str | None
    type: str | None
    summary: str
    transcript: Optional[list[Dict[str, Any]] ] = None
    media_content: Optional[list[Dict[str, Any]] ] = None
    pdf_content: Optional[list[str]] = None
    source: str
    chat_content: Optional[str] = None
    embeddings: Optional[list[Dict[str, Any]]] = None

class NoteResponseModel(NoteModel):
    id: str
    created_at: datetime
