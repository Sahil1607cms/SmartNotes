import React, { useState, useEffect } from "react";
import SummaryPage from "./SummaryPage";
import VideoPreview from "../components/VideoPreview";
import LiveLogConsole from "../components/LiveLogConsole";
import { auth } from "../firebase.js";
import { addNoteToHistory } from "../utils/historyStorage.js";

export default function YoutubeSummarizer() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [userID, setUserID] = useState(null);
  const [title, setTitle] = useState("YouTube Video");
  const [noteId, setNoteId] = useState("");
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
      const savedState = localStorage.getItem("summary_yt_state");
      if (savedState) {
        const parsed = JSON.parse(savedState);
        if (parsed.summary) setSummary(parsed.summary);
        if (parsed.url) setUrl(parsed.url);
        if (parsed.transcript) setTranscript(parsed.transcript);
        if (parsed.title) setTitle(parsed.title);
        if (parsed.noteId) setNoteId(parsed.noteId);
        if (parsed.logs) setLogs(parsed.logs);
      }
    } catch (e) {
      console.error("Error restoring YouTube state:", e);
    }
  }, []);

  // Save full state to localStorage whenever state changes
  useEffect(() => {
    const stateToSave = { summary, url, transcript, title, noteId, logs };
    localStorage.setItem("summary_yt_state", JSON.stringify(stateToSave));
  }, [summary, url, transcript, title, noteId, logs]);

  const clearStorage = () => {
    localStorage.removeItem("summary_yt_state");
    setUrl("");
    setSummary("");
    setTranscript([]);
    setLogs([]);
    setNoteId("");
    setError("");
  };

  const handleSummarize = async () => {
    if (!url.trim()) return;
    if (!userID) return alert("User not logged in!");

    setLoading(true);
    setError("");
    setSummary("");
    setLogs(["📥 Starting YouTube processing..."]);

    try {
      const res = await fetch("http://localhost:8000/summarize-yt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userID,
          title,
          type: "youtube",
          url,
          transcript: (transcript && transcript.length > 0) ? transcript : null,
        }),
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
        setError("Failed to summarize YouTube video.");
      }
    } catch (err) {
      console.error(err);
      setError("Failed to summarize YouTube video.");
      setLogs((prev) => [...prev, "❌ Error processing YouTube video."]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="flex items-center justify-between">
        <div className="text-3xl py-2 px-2 font-bold min-h-[50px]">
          Youtube Video Summarizer
        </div>
        <button
          onClick={clearStorage}
          className="bg-amber-300 text-black p-1 font-bold rounded-md cursor-pointer hover:bg-amber-200"
        >
          Clear Page
        </button>
      </div>

      {/* Input */}
      <div className="mb-4 mt-2 flex flex-col gap-2 px-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube link..."
            className="flex-1 p-2 rounded bg-gray-800 text-white"
          />
          <button
            onClick={handleSummarize}
            className={`px-4 py-2 rounded ${
              url.trim()
                ? "bg-blue-600 cursor-pointer"
                : "bg-gray-600 cursor-not-allowed"
            }`}
            disabled={!url.trim() || loading}
          >
            <div>{loading ? "⏳ Processing..." : "Summarize"}</div>
          </button>
        </div>
      </div>

      {/* Preview, Console & Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] flex-1 gap-2 min-h-0">
        <div className="flex flex-col gap-2 min-h-0 overflow-hidden">
          <VideoPreview
            url={url}
            transcript={transcript}
            setTranscript={setTranscript}
            setTitle={setTitle}
            onTranscriptFetched={(t) => setTranscript(t)}
            onTitleFetched={(t) => setTitle(t)}
          />
          {logs.length > 0 && <LiveLogConsole logs={logs} />}
        </div>
        <SummaryPage summary={summary} loading={loading} noteId={noteId} />
      </div>
    </div>
  );
}
