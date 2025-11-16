import React from "react";
import { useState, useEffect } from "react";
import { UploadCloud, AudioLines, Video } from "lucide-react";
import SummaryPage from "./SummaryPage";
import { useAuth } from "../context/AuthContext";

export default function AudioVideoSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null); // store uploaded file
  const [error, setError] = useState("");
  const { user } = useAuth();

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
    if (!file) {
      setError("Please select a file first");
      return;
    }

    if (!user) {
      setError("Please log in to summarize media files");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", user.uid);
      formData.append("type", "media");

      const res = await fetch("http://localhost:8000/summarize-media", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (data.error) {
        setError(data.error);
        setSummary("");
      } else if (data.summary) {
        setSummary(data.summary);
        setError("");
      } else {
        setError("Failed to generate summary. Please try again.");
        setSummary("");
      }
    } catch (err) {
      console.error("Error summarizing media:", err);
      setError("Network error. Please check your connection and try again.");
      setSummary("");
    } finally {
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
            accept="audio/*,video/*,.mp3,.wav,.m4a,.ogg,.flac,.aac,.mp4,.avi,.mov,.mkv,.webm"
            onChange={(e) => {
              setFile(e.target.files[0]);
              setError("");
            }}
            className="hidden"
          />
          {/* Custom styled label as button */}
          <label
            htmlFor="file-upload"
            className="flex flex-col text-center justify-center items-center gap-2 px-4 py-2 h-[150px] sm:h-[200px] w-full bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700 border-dotted border-blue-400 border-2"
          >
            <UploadCloud className="w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-gray-700 p-1"/>
            <span className="text-sm sm:text-base px-2">{file ? file.name : "Drag and drop or Browse your files"}</span>
            <span className="text-[.7rem] sm:text-[.8rem] text-gray-400 px-2">{file ? "" : "Supported formats - MP3, WAV, M4A, MP4, AVI, MOV, etc."}</span>
          </label>
          {error && (
            <div className="text-red-500 text-sm px-2 py-1 bg-red-50 rounded w-full">
              {error}
            </div>
          )}
          <button
            onClick={handleSummarize}
            disabled={loading || !file || !user}
            className="px-4 py-2 bg-blue-600 max-h-[40px] rounded cursor-pointer text-sm sm:text-base w-full sm:w-auto disabled:bg-gray-400 disabled:cursor-not-allowed"
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
