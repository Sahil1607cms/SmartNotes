import React, { useState } from "react";
import ChatAssistant from "../components/ChatAssistant.jsx";

export default function SummaryPage({ summary, loading }) {
  const [activeTab, setActiveTab] = useState("summary");
  const [chatMessages, setChatMessages] = useState([
    { from: "bot", text: "Hi! 👋 Ask me anything about the summary." },
  ]);

  return (
    <div className="flex flex-col h-full min-h-0 bg-black text-white p-4 rounded-lg shadow-lg">
      {/* Tabs */}
      <div className="flex mb-4">
        <button
          onClick={() => setActiveTab("summary")}
          className={`px-4 py-2 rounded font-bold cursor-pointer ${
            activeTab === "summary"
              ? "bg-yellow-400 text-black"
              : "bg-gray-700 text-gray-300"
          }`}
        >
          Summary
        </button>
        <button
          onClick={() => setActiveTab("chat")}
          disabled={!summary}
          className={`px-4 py-2 rounded ml-2 font-bold cursor-pointer ${
            activeTab === "chat"
              ? "bg-yellow-400 text-black"
              : "bg-gray-700 text-gray-300"
          } ${!summary && "opacity-50 cursor-not-allowed"}`}
        >
          Ask AI
        </button>

        <button
          onClick={() => alert("Flashcards feature coming soon!")}
          disabled={!summary}
          className={`px-4 py-2 rounded ml-2 font-bold cursor-pointer ${
            activeTab === "flashcards"
              ? "bg-yellow-400 text-black"
              : "bg-gray-700 text-gray-300"
          } ${!summary && "opacity-50 cursor-not-allowed"}`}
        >
          Flashcards
        </button>
      </div>

      {/* Content area */}
      <div className="flex-1 min-h-0 flex flex-col">
        {activeTab === "summary" && (
          <div className="bg-gray-800 p-4 rounded-lg shadow-inner whitespace-pre-wrap flex-1 overflow-y-auto">
            {loading ? "⏳ Generating summary..." : summary || "No summary yet."}
          </div>
        )}

        {activeTab === "chat" && summary && (
          <ChatAssistant
            summary={summary}
            chatMessages={chatMessages}
            setChatMessages={setChatMessages}
          />
        )}
      </div>
    </div>
  );
}
