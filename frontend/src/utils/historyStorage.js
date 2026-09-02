import { auth } from "../firebase.js";

const HISTORY_CACHE_KEY = "smartnotes_history_cache";
export const HISTORY_UPDATED_EVENT = "smartnotes_history_updated";

/**
 * Returns cached notes array from localStorage immediately (0ms latency).
 */
export function getStoredNotes() {
  try {
    const raw = localStorage.getItem(HISTORY_CACHE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    console.error("Error reading stored notes from localStorage:", e);
    return [];
  }
}

/**
 * Saves notes array to localStorage and notifies all listening components.
 */
export function setStoredNotes(notes) {
  try {
    const formatted = notes.map((note) => ({
      ...note,
      id: note.id || note._id,
      date: note.created_at
        ? new Date(note.created_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })
        : note.date || "Unknown date",
    }));

    localStorage.setItem(HISTORY_CACHE_KEY, JSON.stringify(formatted));
    window.dispatchEvent(new Event(HISTORY_UPDATED_EVENT));
    return formatted;
  } catch (e) {
    console.error("Error saving notes to localStorage:", e);
    return notes;
  }
}

/**
 * Adds a single newly created note to local history cache and notifies components.
 */
export function addNoteToHistory(newNote) {
  if (!newNote) return;
  try {
    const current = getStoredNotes();
    const formattedNote = {
      ...newNote,
      id: newNote.id || newNote._id,
      date: newNote.created_at
        ? new Date(newNote.created_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
          })
        : "Just now",
    };

    const filtered = current.filter((n) => (n.id || n._id) !== formattedNote.id);
    const updated = [formattedNote, ...filtered];
    setStoredNotes(updated);
  } catch (e) {
    console.error("Error adding note to history:", e);
  }
}

/**
 * Removes a note from local history cache by ID and notifies components.
 */
export function removeNoteFromHistory(noteId) {
  try {
    const current = getStoredNotes();
    const updated = current.filter((n) => (n.id || n._id) !== noteId);
    setStoredNotes(updated);
  } catch (e) {
    console.error("Error removing note from history:", e);
  }
}

/**
 * Asynchronously fetches fresh notes from backend DB and updates localStorage cache.
 */
export async function syncNotesFromDB(userId) {
  if (!userId) {
    const currentUser = auth.currentUser;
    if (currentUser) userId = currentUser.uid;
  }

  if (!userId) return getStoredNotes();

  try {
    const res = await fetch(`http://localhost:8000/notes/?user_id=${userId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);

    const data = await res.json();
    if (Array.isArray(data)) {
      return setStoredNotes(data);
    }
  } catch (e) {
    console.warn("Could not sync notes from DB (using cached local notes):", e);
  }

  return getStoredNotes();
}
