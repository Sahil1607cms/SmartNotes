import React, { useState, useEffect } from "react";
import SummaryPage from "./SummaryPage";
import { auth } from "../firebase.js";
import { Paperclip, File } from "lucide-react";
export default function PdfTextSummarizer() {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [userID, setUserID] = useState(null);
  const [title, setTitle] = useState("PDF");
const [noteId, setNoteId] = useState("");
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
    const savedSummary = localStorage.getItem("summary_pdf");
    if (savedSummary) setSummary(savedSummary);
  }, []);

  useEffect(() => {
    if (summary) {
      localStorage.setItem("summary_pdf", summary);
    }
  }, [summary]);

  const clearStorage = () => {
    localStorage.removeItem("summary_pdf");
    setSummary("");
  };

  const handleSummarize = async () => {
    if (!file) return;

    if (!userID) return alert("User not logged in!");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("user_id", userID);
      formData.append("type", "pdf");

      const res = await fetch("http://localhost:8000/summarize-pdf", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }
      const data = await res.json();

      setSummary(data.summary || "Failed to generate summary Try again");
    } catch (error) {
      console.error("❌ PDF summarization failed:", error);
      setSummary("An error occurred while summarizing the PDF.");
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
          onClick={() => clearStorage()}
          className="bg-amber-300   mt-10 text-black p-1 font-bold rounded-md cursor-pointer hover:bg-amber-200"
        >
          Clear Page
        </button>
      </div>
      {/* Input */}
      <div className="mb-4 mt-2 flex gap-2 max-h-[50px]">
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
          className="flex items-center  gap-2 px-4 py-2 bg-gray-800 text-white rounded cursor-pointer hover:bg-gray-700 "
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
