import React, { useState } from "react";
import SummaryPage from "./SummaryPage";
import { Paperclip, File } from "lucide-react";
export default function PdfTextSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null); // store uploaded file

  const handleSummarize = async () => {
    if (!file) return;
    setLoading(true);

    try {
      const formData = new formData();
      formData.append("file", file);

      const res = await fetch("backendurl/summary", {
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
      <h1 className="text-3xl py-2 px-2 font-bold">
        Select a PDF to get the summary
      </h1>
      {/* Input */}
      <div className="mb-4 mt-2 flex gap-2">
        <input
          type="file"
          id="file-upload"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])} // store file object
          className="hidden"
        />
        {/* Custom styled label as button */}
        <label
          htmlFor="file-upload"
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700"
        >
          <File className="w-5 h-5" />
          {file ? file.name : "Choose a file"}
        </label>
        <button
          onClick={handleSummarize}
          className="px-4 py-2 bg-blue-600 rounded cursor-pointer"
        >
          <div>{loading ? "⏳ Summarizing..." : "Summarize"}</div>
        </button>
      </div>

      {/* Summary + Chat */}
      <SummaryPage summary={summary} loading={loading} />
    </div>
  );
}
