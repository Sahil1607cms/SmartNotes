import React from "react";
import { useState, useEffect } from "react";
import { UploadCloud, AudioLines, Video } from "lucide-react";
import SummaryPage from "./SummaryPage";
export default function AudioVideoSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null); // store uploaded file

  // Persist summary locally so it survives navigation
  useEffect(() => {
    const saved = localStorage.getItem("summary_audio_video");
    if (saved) setSummary(saved);
  }, []);

  useEffect(() => {
    if (summary !== undefined) {
      localStorage.setItem("summary_audio_video", summary || "");
    }
  }, [summary]);

  const handleSummarize = async () => {
    if (!file) return;
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/summary", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setSummary(data.summary || "Failed to generate summary Try again");
    } catch (err) {
      setSummary("Elon Musk is a visionary entrepreneur, engineer, and innovator whose work has had a profound impact on multiple industries, ranging from space exploration to electric vehicles and renewable energy. As the founder of SpaceX, he has revolutionized the aerospace industry by developing reusable rockets, drastically reducing the cost of space travel, and laying the groundwork for potential human colonization of Mars. Through Tesla, Musk has accelerated the global transition to sustainable energy, popularizing electric cars and pushing the boundaries of battery technology and autonomous driving. Beyond these ventures, he has been involved in ambitious projects such as Neuralink, which aims to create brain-computer interfaces, and The Boring Company, which focuses on tunnel infrastructure to reduce urban traffic congestion. Musk’s approach is characterized by first-principles thinking, a willingness to take massive risks, and an insistence on solving fundamental problems rather than incremental improvements. His influence extends beyond technology; he has become a cultural figure whose ideas about innovation, the future of humanity, and the ethical use of technology spark discussion and debate worldwide. Despite criticism for his unconventional management style and controversial statements, Musk remains one of the most impactful and polarizing figures of the 21st century, driving conversations about what is possible when audacious vision is combined with relentless execution.");
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-xl sm:text-2xl md:text-3xl py-2 px-2 font-bold min-h-[50px]">
        Select an Audio or Video to get the summary
      </h1>
      <div className="grid grid-cols-1 lg:grid-cols-[400px_1fr] flex-1 gap-2">
        {/* Input */}
        <div className="mb-4 mt-2 flex flex-col items-center justify-center gap-2 px-2">
          <input
            type="file"
            id="file-upload"
            accept="audio/mp3, audio/mpeg, video/mp4"
            onChange={(e) => setFile(e.target.files[0])} // store file object
            className="hidden"
          />
          {/* Custom styled label as button */}
          <label
            htmlFor="file-upload"
            className="flex flex-col text-center justify-center items-center gap-2 px-4 py-2 h-[150px] sm:h-[200px] w-full bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700 border-dotted border-blue-400 border-2"
          >
            <UploadCloud className="w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-gray-700 p-1"/>
            <span className="text-sm sm:text-base px-2">{file ? file.name : "Drag and drop or Browse your files"}</span>
            <span className="text-[.7rem] sm:text-[.8rem] text-gray-400 px-2">{file ? "" : "Supported formats - MP3, MP4, MPEG"}</span>
          </label>
          <button
            onClick={handleSummarize}
            className="px-4 py-2 bg-blue-600 max-h-[40px] rounded cursor-pointer text-sm sm:text-base w-full sm:w-auto"
          >
            <div>{loading ? "⏳ Summarizing..." : "Summarize"}</div>
          </button>
        </div>

        {/* Summary + Chat */}
        <SummaryPage summary={summary} loading={loading} />
      </div>
    </div>
  );
}
