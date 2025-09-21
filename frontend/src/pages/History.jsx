import React, { useState } from "react";
import { Search } from "lucide-react";

export default function History({ onOpenNote }) {
  const [search, setSearch] = useState("");

  // Dummy notes history
  const [notes] = useState([
    { id: 1, title: "Meeting with Client", date: "2025-09-20", summary: "Discussed project roadmap and deliverables." },
    { id: 2, title: "AI Research Paper", date: "2025-09-19", summary: "Summarized key points on LLM advancements." },
    { id: 3, title: "Daily Journal", date: "2025-09-18", summary: "Reflections on productivity and learning." },
    { id: 4, title: "YouTube Video Notes", date: "2025-09-17", summary: "Main takeaways from a podcast on innovation." },
  ]);

  // Filtered notes by search
  const filteredNotes = notes.filter(
    (note) =>
      note.title.toLowerCase().includes(search.toLowerCase()) ||
      note.summary.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* Header */}
      <h1 className="text-2xl font-bold mb-4">Notes History</h1>

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-3 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search notes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-xl focus:ring focus:ring-blue-300 outline-none"
        />
      </div>

      {/* Notes List */}
      <div className="space-y-4">
        {filteredNotes.length > 0 ? (
          filteredNotes.map((note) => (
            <div
              key={note.id}
              onClick={() => onOpenNote && onOpenNote(note)}
              className="p-4 border-0 rounded-xl hover:bg-gray-700 cursor-pointer transition"
            >
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-lg text-yellow-300 font-semibold">{note.title}</h2>
                <span className="text-sm text-gray-300">{note.date}</span>
              </div>
              <p className="text-gray-300 line-clamp-2">{note.summary}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-500">No notes found.</p>
        )}
      </div>
    </div>
  );
}
