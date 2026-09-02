import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Search, X, Copy, Trash2, RefreshCw } from "lucide-react";
import { auth } from "../firebase.js";
import { useAuth } from "../context/AuthContext.jsx";
import {
  getStoredNotes,
  removeNoteFromHistory,
  syncNotesFromDB,
  HISTORY_UPDATED_EVENT,
} from "../utils/historyStorage.js";

export default function History() {
  const [search, setSearch] = useState("");
  const { user: authUser } = useAuth();
  
  // Instant load from localStorage cache (0ms latency!)
  const [notes, setNotes] = useState(() => getStoredNotes());
  const [loading, setLoading] = useState(() => getStoredNotes().length === 0);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState("");
  const [selectedNote, setSelectedNote] = useState(null);

  useEffect(() => {
    let isMounted = true;

    // Direct MongoDB sync on routing to History tab
    const fetchFromDB = async (targetUser) => {
      const uid = targetUser?.uid || authUser?.uid || auth.currentUser?.uid || localStorage.getItem("smartnotes_uid");
      if (!uid) {
        if (isMounted) setLoading(false);
        return;
      }

      localStorage.setItem("smartnotes_uid", uid);
      if (isMounted) setSyncing(true);

      try {
        const freshNotes = await syncNotesFromDB(uid);
        if (isMounted) {
          setNotes(freshNotes);
          setError("");
        }
      } catch (err) {
        console.error("MongoDB fetch error in History:", err);
        if (isMounted) setError("Failed to load notes from database.");
      } finally {
        if (isMounted) {
          setLoading(false);
          setSyncing(false);
        }
      }
    };

    // 1. Fetch from MongoDB immediately on tab click / mount
    fetchFromDB(authUser || auth.currentUser);

    // 2. Refresh UI state whenever local storage cache updates
    const updateFromCache = () => {
      if (isMounted) {
        setNotes(getStoredNotes());
        setLoading(false);
      }
    };
    window.addEventListener(HISTORY_UPDATED_EVENT, updateFromCache);

    // 3. Auth listener backup
    const unsubscribe = auth.onAuthStateChanged((u) => {
      if (u) fetchFromDB(u);
    });

    return () => {
      isMounted = false;
      window.removeEventListener(HISTORY_UPDATED_EVENT, updateFromCache);
      unsubscribe();
    };
  }, [authUser]);

  const handleManualRefresh = async () => {
    const uid = authUser?.uid || auth.currentUser?.uid || localStorage.getItem("smartnotes_uid");
    if (!uid) return;
    setSyncing(true);
    const freshNotes = await syncNotesFromDB(uid);
    setNotes(freshNotes);
    setSyncing(false);
  };

  const filteredNotes = notes.filter(
    (note) =>
      (note.title && note.title.toLowerCase().includes(search.toLowerCase())) ||
      (note.summary && note.summary.toLowerCase().includes(search.toLowerCase()))
  );

  const copySummary = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Summary copied to clipboard!");
    });
  };

  const deleteNote = async (noteId) => {
    try {
      // Instantly remove from local storage & UI state
      removeNoteFromHistory(noteId);
      setNotes((prev) => prev.filter((n) => (n.id || n._id) !== noteId));
      setSelectedNote(null);

      // Async delete from MongoDB
      await fetch(`http://localhost:8000/notes/${noteId}`, {
        method: "DELETE",
      });
    } catch (error) {
      console.error("Error deleting note from backend:", error);
    }
  };

  return (
    <div className="mx-auto p-3 sm:p-6 flex flex-col h-[100vh]">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl sm:text-2xl font-bold">Notes History</h1>
        <button
          onClick={handleManualRefresh}
          disabled={syncing}
          className="flex items-center gap-1.5 text-xs sm:text-sm bg-gray-800 hover:bg-gray-700 text-gray-200 px-3 py-1.5 rounded-lg border border-gray-700 transition cursor-pointer"
          title="Sync with MongoDB"
        >
          <RefreshCw size={14} className={syncing ? "animate-spin text-blue-400" : ""} />
          <span>{syncing ? "Syncing..." : "Refresh"}</span>
        </button>
      </div>

      <div className="relative mb-4">
        <Search className="absolute left-3 top-3 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search notes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-700 rounded-xl focus:ring focus:ring-blue-300 outline-none text-sm sm:text-base bg-gray-900 text-white"
        />
      </div>

      {loading && notes.length === 0 && (
        <p className="text-gray-400 text-center py-8">Loading notes from database...</p>
      )}

      {error && notes.length === 0 && (
        <p className="text-red-400 text-center py-8">Error: {error}</p>
      )}

      {!loading && (
        <div className="flex-1 overflow-y-auto space-y-4 border-t border-gray-700 pt-2">
          {filteredNotes.length > 0 ? (
            filteredNotes.map((note) => (
              <div
                key={note.id || note._id || Math.random()}
                onClick={() => setSelectedNote(note)}
                className="p-3 sm:p-4 border border-gray-800 rounded-xl hover:bg-gray-800 bg-gray-900/60 cursor-pointer transition"
              >
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2 gap-2">
                  <h2 className="text-base sm:text-lg text-yellow-300 font-semibold break-words">
                    {note.title || "Untitled Note"}
                  </h2>
                  <span className="text-xs sm:text-sm text-gray-400 whitespace-nowrap">
                    {note.date || "Unknown date"}
                  </span>
                </div>
                <p className="text-sm sm:text-base text-gray-300 line-clamp-2">
                  {note.summary}
                </p>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8 text-sm sm:text-base">
              No notes found.
            </p>
          )}
        </div>
      )}

      {/* Modal View for Note Details */}
      {selectedNote && (
        <div className="fixed inset-0 bg-black/70 bg-opacity-50 flex justify-center items-center z-50 p-2 sm:p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-4xl p-4 sm:p-6 relative flex flex-col max-h-[90vh]">
            <button
              onClick={() => setSelectedNote(null)}
              className="absolute top-2 right-2 sm:top-3 sm:right-3 text-gray-400 hover:text-white p-1"
            >
              <X size={20} className="sm:w-6 sm:h-6" />
            </button>

            <button
              onClick={() => deleteNote(selectedNote.id || selectedNote._id)}
              className="absolute top-2 right-12 sm:top-3 sm:right-14 text-white bg-red-600 rounded-md hover:bg-red-700 flex items-center gap-1 px-2 py-1 text-xs sm:text-sm"
            >
              <Trash2 size={16} className="sm:w-[18px] sm:h-[18px]" />
              <span className="hidden sm:inline">Delete</span>
            </button>

            <button
              onClick={() => copySummary(selectedNote.summary)}
              className="absolute top-2 right-24 sm:top-3 sm:right-28 text-black bg-white rounded-md hover:bg-gray-200 flex items-center gap-1 px-2 py-1 text-xs sm:text-sm"
            >
              <Copy size={16} className="sm:w-[18px] sm:h-[18px] text-black" />
              <span className="hidden sm:inline">Copy</span>
            </button>

            <h2 className="text-lg sm:text-2xl mt-2 font-bold text-yellow-300 mb-4 pr-16 break-words">
              {selectedNote.title || "Untitled Note"}
            </h2>
            <p className="text-xs sm:text-sm font-bold mb-2 text-gray-300">
              Type: {selectedNote.type || "Document"}
            </p>
            {selectedNote.source && (
              <p className="text-xs sm:text-sm font-bold mb-4 break-all text-gray-400">
                Source: {selectedNote.source}
              </p>
            )}

            <div className="overflow-y-auto text-gray-300 text-sm sm:text-base border-t border-gray-700 pt-4 flex-1">
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => (
                    <h1 className="text-yellow-400 font-bold text-2xl mt-2 mb-2" {...props} />
                  ),
                  h2: ({ node, ...props }) => (
                    <h2 className="text-yellow-400 font-bold text-xl mt-2 mb-2" {...props} />
                  ),
                  h3: ({ node, ...props }) => (
                    <h3 className="text-yellow-400 font-bold text-lg mt-2 mb-2" {...props} />
                  ),
                  strong: ({ node, ...props }) => (
                    <strong className="text-yellow-300 font-bold" {...props} />
                  ),
                  p: ({ node, ...props }) => (
                    <p className="text-gray-200 text-sm sm:text-base mb-3" {...props} />
                  ),
                  ul: ({ node, ...props }) => (
                    <ul className="list-disc ml-4 mb-2 mt-2" {...props} />
                  ),
                  ol: ({ node, ...props }) => (
                    <ol className="list-decimal ml-4 mb-2 mt-2" {...props} />
                  ),
                  li: ({ node, ...props }) => (
                    <li className="text-gray-200 text-sm sm:text-base mb-1" {...props} />
                  ),
                }}
              >
                {selectedNote.summary}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
