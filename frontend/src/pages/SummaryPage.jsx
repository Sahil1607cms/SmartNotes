import React, { useState } from "react";
import ChatAssistant from "../components/ChatAssistant.jsx";
import { Copy } from "lucide-react";

export default function SummaryPage({ summary, loading }) {
  const [activeTab, setActiveTab] = useState("summary");
    const [copied, setCopied] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { from: "bot", text: "Hi! 👋 Ask me anything about the summary." },
  ]);

  const handleCopyAll = () => {
    const textToCopy = summary
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatSummary = (text) => {
    if (!text) return "";
    return text
      .replace(/\*\*(.*?)\*\*/g, '<span class="section-title">$1</span>')
      .replace(/\n/g, "<br>");
  };

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
        <button
            onClick={handleCopyAll}
            className="flex items-center gap-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 cursor-pointer ml-auto rounded text-sm"
          >
            {copied ? (
              <span className="text-green-400">Copied!</span>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy Summary
              </>
            )}
          </button>
      </div>

      <div className="flex-1 min-h-0 flex flex-col">
        {activeTab === "summary" && (
          <div className="bg-gray-800 p-4 rounded-lg shadow-inner whitespace-pre-wrap flex-1 overflow-y-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
            {loading ? (
              "⏳ Generating summary..."
            ) : summary ? (
              <div
                dangerouslySetInnerHTML={{ __html: formatSummary(summary) }}
              />
            ) : (
              "No summary yet."
            )}
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
      <style >{`
        .section-title {
          font-weight: 700;
          font-size: 1.15rem; /* bigger */
          color: #facc15;     /* yellow/orange */
         
        }
      `}</style>
    </div>
  );
}
