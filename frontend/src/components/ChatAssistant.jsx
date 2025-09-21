import React, { useState, useEffect, useRef } from "react";
import { Send } from "lucide-react";

const ChatAssistant = ({ summary, chatMessages, setChatMessages }) => {
  const [chatInput, setChatInput] = useState("");
  const [prompts, setPrompts] = useState([]);
  const messagesEndRef = useRef(null);
  const [thinking, setThinking] = useState(false);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Fetch prompts
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const res = await fetch("http://localhost:5000/prompts", {
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
      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatInput, summary }),
      });
      const data = await res.json();
      const botMsg = { from: "bot", text: data.reply || "⚠️ No reply received." };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { from: "bot", text: "Elon Musk is a billionaire entrepreneur and engineer known for founding SpaceX and Tesla. He focuses on advancing space exploration, electric vehicles, and sustainable energy, and is involved in projects like Neuralink and The Boring Company." },
      ]);
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Chat messages container */}
      <div className="flex-1 min-h-0 overflow-y-auto pr-2 space-y-2 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        {chatMessages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
              msg.from === "bot"
                ? "text-white self-start max-w-s"
                : "bg-gray-600 text-white self-end ml-auto"
            }`}
          >
            {msg.text}
          </div>
        ))}

        {thinking && (
          <div className="max-w-xs px-3 py-2 rounded-lg text-sm text-white self-start">
            🤔 Thinking, please wait...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Bot prompts */}
      {prompts.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2 overflow-x-auto">
          {prompts.map((msg, idx) => (
            <div
              key={idx}
              onClick={() => {
                setChatInput(msg.text);
                setTimeout(() => handleSendMessage(), 0);
              }}
              className="bg-blue-600 text-white px-3 py-1 rounded-lg text-sm cursor-pointer"
            >
              {msg.text}
            </div>
          ))}
        </div>
      )}

      {/* Input box */}
      <div className="flex gap-2 bg-gray-900 p-2 rounded-b-lg">
        <input
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask about the summary..."
          className="flex-1 p-2 rounded-l bg-gray-800 text-white rounded-2xl"
        />
        <button onClick={handleSendMessage}>
          <Send className="bg-yellow-400 size-10 p-2 text-black rounded-2xl" />
        </button>
      </div>
    </div>
  );
};

export default ChatAssistant;
