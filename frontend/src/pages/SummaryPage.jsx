import React, { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import ChatAssistant from "../components/ChatAssistant.jsx";
import { Copy, Download } from "lucide-react";
import Flashcards from "../components/Flashcards.jsx";
import { jsPDF } from "jspdf";

export default function SummaryPage({ summary, loading }) {
  const [activeTab, setActiveTab] = useState("summary");
  const [copied, setCopied] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { from: "bot", text: "Hi! 👋 Ask me anything about the summary." },
  ]);
  const summaryRef = useRef();

  const handleCopyAll = () => {
    const textToCopy = summary;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const downloadPDF = () => {
  if (!summary) return;

  const doc = new jsPDF({
    unit: "pt",
    format: "a4",
  });

  const margin = 40;
  const maxWidth = 515; // A4 width minus margins

  doc.setFont("Helvetica", "normal");
  doc.setFontSize(12);

  const lines = doc.splitTextToSize(summary, maxWidth);
  doc.text(lines, margin, margin);

  doc.save("summary.pdf");
};


  return (
    <div className="flex flex-col w-full h-full min-h-0 bg-black text-white p-2 sm:p-4 rounded-lg shadow-lg">
      {/* Tabs */}
      <div className="flex flex-wrap justify-between gap-2 mb-4">
        <div className="flex items-center gap-2">
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
        onClick={() => setActiveTab("flashcards")}
          disabled={!summary}
          className={`px-3 sm:px-4 py-2 rounded font-bold cursor-pointer text-sm sm:text-base ${
            activeTab === "flashcards"
              ? "bg-yellow-400 text-black"
              : "bg-gray-700 text-gray-300"
          } ${!summary && "opacity-50 cursor-not-allowed"}`}
        >
          Flashcards
        </button>
        </div>
        <div className="flex items-center gap-2">
          <button
          onClick={()=>downloadPDF()}
          className=" flex items-center gap-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 cursor-pointer ml-auto rounded text-xs sm:text-sm"
        >
          <>
            <Download className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="">Save to PDF</span>
          </>
        </button>
        <button
          onClick={handleCopyAll}
          className=" flex items-center gap-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 cursor-pointer ml-auto rounded text-xs sm:text-sm"
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
      </div>

      <div className="flex-1 min-h-0 min-w-full flex flex-col">
        {activeTab === "summary" && (
          <div ref={summaryRef} className="bg-black p-2 sm:p-4 rounded-lg shadow-inner  flex-1 overflow-y-auto  text-sm sm:text-base">
            {loading ? (
              "⏳ Generating summary..."
            ) : summary ? (
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => (
                    <h1
                      className="text-blue-400 font-bold text-4xl mt-2 mb-2"
                      {...props}
                    />
                  ),
                  h2: ({ node, ...props }) => (
                    <h2
                      className="text-blue-400 font-bold text-3xl mt-2 mb-2"
                      {...props}
                    />
                  ),
                  h3: ({ node, ...props }) => (
                    <h3
                      className="text-blue-400 font-bold text-2xl mt-2 mb-2"
                      {...props}
                    />
                  ),

                  strong: ({ node, ...props }) => (
                    <strong
                      className="text-yellow-300 font-bold text-xl mb-10 mt-10"
                      {...props}
                    />
                  ),

                  p: ({ node, ...props }) => (
                    <p className="text-white text-lg mb-3 mt-3" {...props} />
                  ),

                  ul: ({ node, ...props }) => (
                    <ul className="list-disc ml-4 mb-2 mt-2" {...props} />
                  ),

                  ol: ({ node, ...props }) => (
                    <ol className="list-decimal ml-4 " {...props} />
                  ),

                  li: ({ node, ...props }) => (
                    <li className="text-white text-lg " {...props} />
                  ),
                }}
              >
                {summary}
              </ReactMarkdown>
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
        {activeTab === "flashcards" && summary && (
          <Flashcards
            summary={summary}
          />
        )}
      </div>
      <style>{`
        .section-title {
          font-weight: 700;
          font-size: 1.15rem; /* bigger */
          color: #facc15;     /* yellow/orange */
         
        }
      `}</style>
    </div>
  );
}
