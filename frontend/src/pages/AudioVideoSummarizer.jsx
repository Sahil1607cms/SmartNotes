import React, { useState, useEffect } from "react";
import { UploadCloud } from "lucide-react";
import SummaryPage from "./SummaryPage";
import LiveLogConsole from "../components/LiveLogConsole";
import { useAuth } from "../context/AuthContext";
import { addNoteToHistory } from "../utils/historyStorage.js";

export default function AudioVideoSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const { user } = useAuth();
  const [noteId, setNoteId] = useState("");
  const [logs, setLogs] = useState([]);

  // Restore full state on mount
  useEffect(() => {
    try {
      const savedState = localStorage.getItem("summary_media_state");
      if (savedState) {
        const parsed = JSON.parse(savedState);
        if (parsed.summary) setSummary(parsed.summary);
        if (parsed.noteId) setNoteId(parsed.noteId);
        if (parsed.logs) setLogs(parsed.logs);
      }
    } catch (e) {
      console.error("Error restoring media state:", e);
    }
  }, []);

  // Save full state to localStorage whenever state changes
  useEffect(() => {
    const stateToSave = { summary, noteId, logs };
    localStorage.setItem("summary_media_state", JSON.stringify(stateToSave));
  }, [summary, noteId, logs]);

  const clearStorage = () => {
    localStorage.removeItem("summary_media_state");
    setSummary("");
    setLogs([]);
    setNoteId("");
    setError("");
    setFile(null);
  };

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
    setSummary("");
    setLogs(["📥 Starting media processing..."]);

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

      if (data.summary) {
        setSummary(data.summary);
        if (data.note) {
          addNoteToHistory(data.note);
          if (data.note.id || data.note._id) setNoteId(data.note.id || data.note._id);
        }
        if (data.logs) setLogs(data.logs);
      } else if (data.error) {
        setError(data.error);
        if (data.logs) setLogs(data.logs);
      } else {
        setError("Failed to summarize media file.");
      }
    } catch (err) {
      console.error("Error summarizing media:", err);
      setError("Network error. Please try again.");
      setLogs((prev) => [...prev, "❌ Error processing media file."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between">
        <h1 className="text-xl sm:text-2xl md:text-3xl py-2 px-2 font-bold min-h-[50px]">
          Select an Audio or Video to get the summary
        </h1>
        <button
          onClick={clearStorage}
          className="bg-amber-300 mt-2 text-black p-1 font-bold rounded-md cursor-pointer hover:bg-amber-200"
        >
          Clear Page
        </button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] flex-1 gap-2 min-h-0">
        {/* Input & Logs */}
        <div className="mb-4 mt-2 flex flex-col items-center justify-start gap-2 px-2">
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
          <label
            htmlFor="file-upload"
            className="flex flex-col text-center justify-center items-center gap-2 px-4 py-2 h-[150px] sm:h-[180px] w-full bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700 border-dotted border-blue-400 border-2"
          >
            <UploadCloud className="w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-gray-700 p-1" />
            <span className="text-sm sm:text-base px-2">
              {file ? file.name : "Drag and drop or Browse your files"}
            </span>
            <span className="text-[.7rem] sm:text-[.8rem] text-gray-400 px-2">
              {file ? "" : "Supported formats - MP3, WAV, M4A, MP4, AVI, MOV, etc."}
            </span>
          </label>
          {error && (
            <div className="text-red-500 text-sm px-2 py-1 bg-red-950/60 border border-red-800 rounded w-full">
              {error}
            </div>
          )}
          <button
            onClick={handleSummarize}
            disabled={loading || !file || !user}
            className="px-4 py-2 bg-blue-600 max-h-[40px] rounded cursor-pointer text-sm sm:text-base w-full disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
          >
            <div>{loading ? "⏳ Processing..." : "Summarize"}</div>
          </button>

          {logs.length > 0 && <LiveLogConsole logs={logs} />}
        </div>

        {/* Summary + Chat */}
        <SummaryPage summary={summary} loading={loading} noteId={noteId} />
      </div>
    </div>
  );
}
