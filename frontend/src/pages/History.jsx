import React, { useState, useEffect } from "react";
import { Search, X, Copy } from "lucide-react";
import { auth } from "../firebase.js";

export default function History() {
  const [search, setSearch] = useState("");
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedNote, setSelectedNote] = useState(null);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const user = auth.currentUser;
        if (!user) throw new Error("User not logged in");

        const userId = user.uid;
        const response = await fetch(`http://localhost:8000/notes/?user_id=${userId}`);
        if (!response.ok) throw new Error("Failed to fetch notes");

        const data = await response.json();
        if (data.error) throw new Error(data.error);
        if (!Array.isArray(data)) {
          setNotes([]);
          return;
        }

        const formattedNotes = data.map(note => ({
          ...note,
          date: note.created_at 
            ? new Date(note.created_at).toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
              })
            : 'Unknown date'
        }));

        setNotes(formattedNotes);
      } catch (err) {
        setError(err.message);
        setNotes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNotes();
  }, []);

  const filteredNotes = notes.filter(
    note =>
      note.title.toLowerCase().includes(search.toLowerCase()) ||
      note.summary.toLowerCase().includes(search.toLowerCase())
  );

  // Format summary function
  const formatSummary = (text) => {
    if (!text) return "";

    let formatted = text;

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<span class="font-bold">$1</span>');

    // Headings
    formatted = formatted.replace(/^###\s+(.*)$/gm, '<span class="text-lg font-semibold">$1</span><br>');
    formatted = formatted.replace(/^##\s+(.*)$/gm, '<span class="text-lg font-semibold">$1</span><br>');
    formatted = formatted.replace(/^#\s+(.*)$/gm, '<span class="text-lg font-semibold">$1</span><br>');

    // Bullets
    formatted = formatted.replace(/^\s*[\*\-]\s+(.*)$/gm, '<li>$1</li>');
    if (/<li>/.test(formatted)) {
      formatted = formatted.replace(/(<li>.*<\/li>)/gs, '<ul class="list-disc list-inside mb-2">$1</ul>');
    }

    // Remaining line breaks
    formatted = formatted.replace(/\n/g, "<br>");

    return formatted;
  };

  const copySummary = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert("Summary copied to clipboard!");
    });
  };

  return (
    <div className="mx-auto p-3 sm:p-6 flex flex-col h-[100vh]">
      <h1 className="text-xl sm:text-2xl font-bold mb-4">Notes History</h1>

      <div className="relative mb-4">
        <Search className="absolute left-3 top-3 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search notes..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-xl focus:ring focus:ring-blue-300 outline-none text-sm sm:text-base"
        />
      </div>

      {loading && <p className="text-gray-400 text-center py-8">Loading notes...</p>}
      {error && <p className="text-red-400 text-center py-8">Error: {error}</p>}

      {!loading && !error && (
        <div className="flex-1 overflow-y-auto space-y-4 border-t border-gray-600 pt-2">
          {filteredNotes.length > 0 ? (
            filteredNotes.map(note => (
              <div
                key={note.id}
                onClick={() => setSelectedNote(note)}
                className="p-3 sm:p-4 border-0 rounded-xl hover:bg-gray-700 cursor-pointer transition"
              >
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-2 gap-2">
                  <h2 className="text-base sm:text-lg text-yellow-300 font-semibold break-words">{note.title}</h2>
                  <span className="text-xs sm:text-sm text-gray-300 whitespace-nowrap">{note.date}</span>
                </div>
                <p className="text-sm sm:text-base text-gray-300 line-clamp-2">{note.summary}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8 text-sm sm:text-base">No notes found.</p>
          )}
        </div>
      )}

      {/* Modal */}
      {selectedNote && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 p-2 sm:p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-2xl p-4 sm:p-6 relative flex flex-col max-h-[90vh]">
            {/* Close button */}
            <button
              onClick={() => setSelectedNote(null)}
              className="absolute top-2 right-2 sm:top-3 sm:right-3 text-gray-400 hover:text-white p-1"
            >
              <X size={20} className="sm:w-6 sm:h-6" />
            </button>

            {/* Copy button */}
            <button
              onClick={() => copySummary(selectedNote.summary)}
              className="absolute top-2 right-10 sm:top-3 sm:right-12 text-black bg-white rounded-md hover:bg-gray-200 flex items-center gap-1 px-2 py-1 text-xs sm:text-sm"
            >
              <Copy size={16} className="sm:w-[18px] sm:h-[18px] text-black"/> <span className="hidden sm:inline">Copy</span>
            </button>

            <h2 className="text-lg sm:text-2xl mt-2 font-bold text-yellow-300 mb-4 pr-16 break-words">{selectedNote.title}</h2>
            <p className="text-xs sm:text-sm text-gray-400 mb-2">Type: {selectedNote.type}</p>
            <p className="text-xs sm:text-sm text-gray-400 mb-4 break-all">Source: {selectedNote.source}</p>

            {/* Scrollable summary */}
            <div
              className="overflow-y-auto text-gray-300 text-sm sm:text-base"
              style={{ maxHeight: "60vh" }}
              dangerouslySetInnerHTML={{ __html: formatSummary(selectedNote.summary) }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
