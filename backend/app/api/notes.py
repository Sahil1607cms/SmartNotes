from typing import List
from fastapi import APIRouter, Query, HTTPException
from app.models.schemas import NoteResponseModel
from app.core.database import get_notes_by_user, delete_note_by_id

router = APIRouter()


@router.get("/notes/", response_model=List[NoteResponseModel])
def fetch_user_notes(user_id: str = Query(..., description="Firebase User ID")):
    """Fetch all saved notes for a specific user."""
    try:
        notes = get_notes_by_user(user_id)
        return [NoteResponseModel(**note) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
def delete_note(note_id: str):
    """Delete a specific note by ID."""
    try:
        success = delete_note_by_id(note_id)
        if success:
            return {"status": "success", "message": "Note deleted successfully"}
        raise HTTPException(status_code=404, detail="Note not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
