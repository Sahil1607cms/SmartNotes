import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, Optional, Dict, Any
from app.core.config import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)

client = MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client[MONGODB_DB_NAME]
notes_collection = db["notes"]


def init_db_connection() -> bool:
    """Verifies active MongoDB connection at startup with ping command."""
    try:
        client.admin.command('ping')
        logger.info(f"🍃 [MongoDB] Successfully connected to database: '{MONGODB_DB_NAME}'")
        return True
    except Exception as e:
        logger.error(f"❌ [MongoDB Connection Error] Failed to connect to MongoDB: {e}")
        return False


def create_note(note_data: Any) -> Dict[str, Any]:
    """Saves a note document to MongoDB and returns document with string ID."""
    doc = note_data.dict(by_alias=True)
    if "_id" in doc and doc["_id"] is None:
        doc.pop("_id")
        
    res = notes_collection.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc["_id"] = str(res.inserted_id)
    return doc


def get_notes_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all notes for a specific user ordered by created_at descending."""
    cursor = notes_collection.find({"user_id": user_id}).sort("created_at", -1)
    notes = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["_id"] = str(doc["_id"])
        notes.append(doc)
    return notes


def get_note_by_id(note_id: str) -> Optional[Dict[str, Any]]:
    """Fetches a single note by string ObjectId."""
    try:
        doc = notes_collection.find_one({"_id": ObjectId(note_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
            return doc
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}")
    return None


def delete_note_by_id(note_id: str) -> bool:
    """Deletes a note document by string ObjectId."""
    try:
        res = notes_collection.delete_one({"_id": ObjectId(note_id)})
        return res.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        return False
