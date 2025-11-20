import React, { useState, useEffect, useRef } from "react";
import { Send } from "lucide-react";
import ReactMarkdown from "react-markdown";
const ChatAssistant = ({ summary, chatMessages, setChatMessages, noteId }) => {
  const [chatInput, setChatInput] = useState("");
  const [prompts, setPrompts] = useState([]);
  const messagesEndRef = useRef(null);
  const [thinking, setThinking] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const res = await fetch("http://localhost:8000/prompts", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ summary }),
        });
        const data = await res.json();
        setPrompts(data.prompts || []);
      } catch {
        setPrompts([]);
      }
    };
    if (summary) fetchPrompts();
  }, [summary]);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { from: "user", text: chatInput };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setThinking(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatInput, summary, note_id: noteId }),
      });
      const data = await res.json();
      const botMsg = {
        from: "bot",
        text: data.reply || "⚠️ No reply received.",
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { from: "bot", text: "Having trouble generating a response." },
      ]);
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      <div className="flex-1 min-h-0 overflow-y-auto pr-2 space-y-2 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {chatMessages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-[65%] px-3 py-2 rounded-lg text-lg font-semibold ${
              msg.from === "bot"
                ? "text-white self-start"
                : "bg-gray-600 text-white self-end ml-auto" 
            }`}
          >
            <ReactMarkdown>{msg.text}</ReactMarkdown>
          </div>
        ))}

        {thinking && (
          <div className="max-w-[85%] sm:max-w-xs px-3 py-2 rounded-lg text-md  text-white self-start">
            🤔 Thinking, please wait...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {prompts.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2 overflow-x-auto pb-2">
          {prompts.map((msg, idx) => (
            <div
              key={idx}
              onClick={() => {
                setChatInput(msg.text);
                setTimeout(() => handleSendMessage(), 0);
              }}
              className="bg-blue-600 text-white px-2 sm:px-3 py-1 rounded-lg text-xs  cursor-pointer whitespace-nowrap"
            >
              <ReactMarkdown>{msg.text}</ReactMarkdown>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2 bg-gray-900 p-2 rounded-b-lg">
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask about the summary..."
          className="flex-1 p-2 rounded-l bg-gray-800 text-white rounded-2xl text-sm sm:text-base"
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <button onClick={handleSendMessage} className="flex-shrink-0">
          <Send className="bg-yellow-400 w-8 h-8 sm:w-10 sm:h-10 p-1.5 sm:p-2 text-black rounded-2xl" />
        </button>
      </div>
    </div>
  );
};

export default ChatAssistant;
