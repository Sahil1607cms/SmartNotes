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

  let formatted = text;

  // 1️⃣ Handle asterisks **Bold**
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<span class="section-title">$1</span>');

  // 2️⃣ Handle hash-style headings (###, ##, #)
  formatted = formatted.replace(/^###\s+(.*)$/gm, '<span class="section-title">$1</span>');
  formatted = formatted.replace(/^##\s+(.*)$/gm, '<span class="section-title">$1</span>');
  formatted = formatted.replace(/^#\s+(.*)$/gm, '<span class="section-title">$1</span>');

  // 3️⃣ Handle bullets * or -
  formatted = formatted.replace(/^\s*[\*\-]\s+(.*)$/gm, '<li>$1</li>');

  // 4️⃣ Wrap list items in <ul> if any exist
  if (/<li>/.test(formatted)) {
    formatted = formatted.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
  }

  // 5️⃣ Replace remaining line breaks with <br>
  formatted = formatted.replace(/\n/g, "<br>");

  return formatted;
};


  return (
    <div className="flex flex-col w-full h-full min-h-0 bg-black text-white p-2 sm:p-4 rounded-lg shadow-lg">
      {/* Tabs */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={() => setActiveTab("summary")}
          className={`px-3 sm:px-4 py-2 rounded font-bold cursor-pointer text-sm sm:text-base ${
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
          className={`px-3 sm:px-4 py-2 rounded font-bold cursor-pointer text-sm sm:text-base ${
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
          className={`px-3 sm:px-4 py-2 rounded font-bold cursor-pointer text-sm sm:text-base ${
            activeTab === "flashcards"
              ? "bg-yellow-400 text-black"
              : "bg-gray-700 text-gray-300"
          } ${!summary && "opacity-50 cursor-not-allowed"}`}
        >
          Flashcards
        </button>
        <button
            onClick={handleCopyAll}
            className="flex items-center gap-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 cursor-pointer ml-auto rounded text-xs sm:text-sm"
          >
            {copied ? (
              <span className="text-green-400">Copied!</span>
            ) : (
              <>
                <Copy className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden sm:inline">Copy Summary</span>
                <span className="sm:hidden">Copy</span>
              </>
            )}
          </button>
      </div>

      <div className="flex-1 min-h-0 min-w-full flex flex-col">
        {activeTab === "summary" && (
          <div className="bg-gray-800 p-2 sm:p-4 rounded-lg shadow-inner whitespace-pre-wrap flex-1 overflow-y-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden text-sm sm:text-base">
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
