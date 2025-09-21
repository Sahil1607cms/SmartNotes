import React, { useState } from "react";
import SummaryPage from "./SummaryPage";
import VideoPreview from "../components/VideoPreview";

export default function YoutubeSummarizer() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSummarize = async () => {
    if (!url.trim()) return;
    setLoading(true);

    try {
      // Example mock call — replace with backend
      setTimeout(() => {
      setSummary("Elon Musk is a visionary entrepreneur, engineer, and innovator whose work has had a profound impact on multiple industries, ranging from space exploration to electric vehicles and renewable energy. As the founder of SpaceX, he has revolutionized the aerospace industry by developing reusable rockets, drastically reducing the cost of space travel, and laying the groundwork for potential human colonization of Mars. Through Tesla, Musk has accelerated the global transition to sustainable energy, popularizing electric cars and pushing the boundaries of battery technology and autonomous driving. Beyond these ventures, he has been involved in ambitious projects such as Neuralink, which aims to create brain-computer interfaces, and The Boring Company, which focuses on tunnel infrastructure to reduce urban traffic congestion. Musk’s approach is characterized by first-principles thinking, a willingness to take massive risks, and an insistence on solving fundamental problems rather than incremental improvements. His influence extends beyond technology; he has become a cultural figure whose ideas about innovation, the future of humanity, and the ethical use of technology spark discussion and debate worldwide. Despite criticism for his unconventional management style and controversial statements, Musk remains one of the most impactful and polarizing figures of the 21st century, driving conversations about what is possible when audacious vision is combined with relentless execution.");
      setLoading(false);
    }, 1200);
    } catch (err) {
      setSummary("❌ Failed to generate summary.");
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen"> {/* 🔹 full height container */}
      <h1 className="text-3xl py-2 px-2 font-bold min-h-[50px]">
        Youtube Video Summarizer
      </h1>

      {/* Input */}
      <div className="mb-4 mt-2 flex gap-2 px-2">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste YouTube link..."
          className="flex-1 p-2 rounded bg-gray-800 text-white"
        />
        <button
          onClick={handleSummarize}
          className="px-4 py-2 bg-blue-600 rounded"
        >
          <div>{loading ? "⏳ Summarizing..." : "Summarize"}</div>
        </button>
      </div>

      {/* Grid takes remaining space */}
      <div className="grid grid-cols-[400px_1fr] flex-1 min-h-0">
        <VideoPreview url={url} />
        <SummaryPage summary={summary} loading={loading} />
      </div>
    </div>
  );
}

