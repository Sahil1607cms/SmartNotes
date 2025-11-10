import React, { useState, useEffect } from "react";
import SummaryPage from "./SummaryPage";
import VideoPreview from "../components/VideoPreview";
import { auth } from "../firebase.js";

export default function YoutubeSummarizer() {
  const [url, setUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [userID, setUserID] = useState(null);
  const [title, setTitle] = useState("YouTube Video");

  // Track Firebase auth user
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      if (user) setUserID(user.uid);
      else setUserID(null);
    });
    return () => unsubscribe();
  }, []);

  // Persist summary locally so it survives navigation
  useEffect(() => {
    const savedSummary = localStorage.getItem("summary_youtube");
    const savedUrl = localStorage.getItem("summary_url");
    const savedTranscript = localStorage.getItem("summary_transcript");
    if (savedUrl && savedSummary) {
      setSummary(savedSummary);
      setUrl(savedUrl);
      setTranscript(savedTranscript);
    }
  }, []);

  useEffect(() => {
    if (summary) {
      localStorage.setItem("summary_youtube", summary );
      localStorage.setItem("summary_url", url );
      localStorage.setItem("summary_transcript",transcript);
    }
  }, [summary]);

  

  const handleSummarize = async () => {
    if (!url.trim()) return;
    if (!transcript || transcript.length === 0) {
      alert("Transcript not available yet!");
      return;
    }
    if (!userID) return alert("User not logged in!");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userID,
          title,
          type: "youtube",
          url,
          transcript,
        }),
      });

      const data = await res.json();
      console.log("Backend response:", data);
      if (data.summary) setSummary(data.summary);
      else setSummary("❌ Failed to generate summary.");
    } catch (err) {
      console.error(err);
      setSummary("❌ Failed to generate summary.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
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
          className={`px-4 py-2 rounded ${
            transcript.length > 0 && url
              ? "bg-blue-600"
              : "bg-gray-600 cursor-not-allowed"
          }`}
          disabled={transcript.length === 0 || !url || loading}
        >
          <div>{loading ? "⏳ Summarizing..." : "Summarize"}</div>
        </button>
      </div>

      <div className="grid grid-cols-[400px_1fr] flex-1 min-h-0">
        <VideoPreview
          url={url}
          setTranscript={setTranscript}
          setTitle={setTitle}
        />
        <SummaryPage summary={summary} loading={loading} />
      </div>
    </div>
  );
}
