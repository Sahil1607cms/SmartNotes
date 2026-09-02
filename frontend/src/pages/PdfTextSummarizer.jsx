import React, { useState, useEffect } from "react";
import SummaryPage from "./SummaryPage";
import LiveLogConsole from "../components/LiveLogConsole";
import { auth } from "../firebase.js";
import { addNoteToHistory } from "../utils/historyStorage.js";
import { File } from "lucide-react";

export default function PdfTextSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [userID, setUserID] = useState(null);
  const [noteId, setNoteId] = useState(null);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState("");

  // Track Firebase auth user
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      if (user) setUserID(user.uid);
      else setUserID(null);
    });
    return () => unsubscribe();
  }, []);

  // Restore full state on mount
  useEffect(() => {
    try {
      const savedState = localStorage.getItem("summary_pdf_state");
      if (savedState) {
        const parsed = JSON.parse(savedState);
        if (parsed.summary) setSummary(parsed.summary);
        if (parsed.noteId) setNoteId(parsed.noteId);
        if (parsed.logs) setLogs(parsed.logs);
      }
    } catch (e) {
      console.error("Error restoring PDF state:", e);
    }
  }, []);

  // Save full state to localStorage whenever state changes
  useEffect(() => {
    const stateToSave = { summary, noteId, logs };
    localStorage.setItem("summary_pdf_state", JSON.stringify(stateToSave));
  }, [summary, noteId, logs]);

  const clearStorage = () => {
    localStorage.removeItem("summary_pdf_state");
    setSummary("");
    setLogs([]);
    setNoteId(null);
    setError("");
    setFile(null);
  };

  const handleSummarize = async () => {
    if (!file) return;
    if (!userID) return alert("User not logged in!");

    setLoading(true);
    setError("");
    setSummary("");
    setLogs(["📥 Starting PDF text processing..."]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", userID);
      formData.append("type", "PDF");

      const res = await fetch("http://localhost:8000/summarize-pdf", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

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
        setError("Failed to summarize PDF document.");
      }
    } catch (err) {
      console.error("❌ PDF summarization failed:", err);
      setError("An error occurred while summarizing the PDF.");
      setLogs((prev) => [...prev, "❌ Error processing PDF file."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between">
        <div className="text-3xl py-2 px-2 font-bold min-h-[50px]">
          PDF Summarizer
        </div>
        <button
          onClick={clearStorage}
          className="bg-amber-300 mt-2 text-black p-1 font-bold rounded-md cursor-pointer hover:bg-amber-200"
        >
          Clear Page
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] flex-1 gap-2 min-h-0">
        {/* Input & Logs */}
        <div className="mb-4 mt-2 flex flex-col gap-2">
          <input
            type="file"
            id="file-upload"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
          />
          <label
            htmlFor="file-upload"
            className="flex items-center gap-2 px-4 py-3 bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700 border border-gray-700"
          >
            <File className="w-5 h-5 text-blue-400" />
            <span className="truncate">{file ? file.name : "Choose a PDF file"}</span>
          </label>
          {error && (
            <div className="text-red-500 text-xs px-2 py-1 bg-red-950/50 rounded border border-red-800">
              {error}
            </div>
          )}
          <button
            onClick={handleSummarize}
            disabled={loading || !file}
            className="px-4 py-2 bg-blue-600 rounded cursor-pointer disabled:bg-gray-500 font-semibold"
          >
            <div>{loading ? "⏳ Processing..." : "Summarize PDF"}</div>
          </button>

          {logs.length > 0 && <LiveLogConsole logs={logs} />}
        </div>

        {/* Summary + Chat */}
        <SummaryPage summary={summary} loading={loading} noteId={noteId} />
      </div>
    </div>
  );
}