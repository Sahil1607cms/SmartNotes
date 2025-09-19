import React, { useState } from "react";
import SummaryPage from "./SummaryPage";
import { Paperclip } from "lucide-react";
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
      setSummary("❌ Failed to generate summary.");
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
          <Paperclip className="w-5 h-5" />
          {file ? file.name : "Choose a file"}
        </label>
        <button
          onClick={handleSummarize}
          className="px-4 py-2 bg-blue-600 rounded cursor-pointer"
        >
          Summarize
        </button>
      </div>

      {/* Summary + Chat */}
      <SummaryPage summary={summary} loading={loading} />
    </div>
  );
}
