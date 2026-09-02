import React, { useState, useEffect } from "react";
import { Copy } from "lucide-react";

export default function VideoPreview({
  url,
  transcript: externalTranscript,
  setTranscript,
  onTranscriptFetched,
  setTitle,
  onTitleFetched,
}) {
  const [copied, setCopied] = useState(false);
  const [localTranscript, setLocalTranscript] = useState([]);
  const [fetching, setFetching] = useState(false);

  const activeTranscript =
    Array.isArray(externalTranscript) && externalTranscript.length > 0
      ? externalTranscript
      : localTranscript;

  const getYouTubeId = (ytUrl) => {
    if (!ytUrl) return null;
    try {
      if (ytUrl.includes("youtu.be/"))
        return ytUrl.split("youtu.be/")[1].split(/[?&]/)[0];
      if (ytUrl.includes("youtube.com/watch"))
        return new URL(ytUrl).searchParams.get("v");
      if (ytUrl.includes("youtube.com/embed/"))
        return ytUrl.split("embed/")[1].split(/[?&]/)[0];
      if (ytUrl.includes("youtube.com/shorts/"))
        return ytUrl.split("shorts/")[1].split(/[?&]/)[0];
      return null;
    } catch {
      return null;
    }
  };

  const videoId = getYouTubeId(url);

  const safeUpdateTranscript = (data) => {
    setLocalTranscript(data);
    if (typeof setTranscript === "function") setTranscript(data);
    if (typeof onTranscriptFetched === "function") onTranscriptFetched(data);
  };

  const safeUpdateTitle = (titleStr) => {
    if (typeof setTitle === "function") setTitle(titleStr);
    if (typeof onTitleFetched === "function") onTitleFetched(titleStr);
  };

  useEffect(() => {
    if (!url) {
      setLocalTranscript([]);
      return;
    }

    const fetchTranscriptAndTitle = async () => {
      setFetching(true);
      try {
        const response = await fetch(
          `http://localhost:8000/transcript/?url=${encodeURIComponent(url)}`
        );
        const data = await response.json();

        if (data.transcript && Array.isArray(data.transcript)) {
          safeUpdateTranscript(data.transcript);
        } else {
          safeUpdateTranscript([{ time: "00:00", text: data.error || "Transcript not available" }]);
        }

        // Fetch video title via oEmbed
        const resTitle = await fetch(
          `https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`
        );

        if (resTitle.ok) {
          const titleData = await resTitle.json();
          safeUpdateTitle(titleData.title || "YouTube Video");
        } else {
          safeUpdateTitle("YouTube Video");
        }
      } catch (error) {
        console.error("Error fetching transcript or title:", error);
        safeUpdateTranscript([{ time: "00:00", text: "Error fetching transcript" }]);
        safeUpdateTitle("YouTube Video");
      } finally {
        setFetching(false);
      }
    };

    fetchTranscriptAndTitle();
  }, [url]);

  const handleCopyAll = () => {
    const textToCopy =
      activeTranscript
        ?.map((line) => `${line.time} - ${line.text}`)
        .join("\n") || "";

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);

    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col p-2 border-r md:w-full w-[250px] border-gray-700">
      {/* Video Player */}
      <div className="aspect-video min-h-[200px] w-full bg-black rounded-lg overflow-hidden border border-gray-800">
        {videoId ? (
          <iframe
            src={`https://www.youtube.com/embed/${videoId}`}
            title="YouTube video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            className="w-full h-full"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            Paste a valid YouTube link to preview
          </div>
        )}
      </div>

      {/* Transcript Section */}
      <div className="mt-4 flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">Transcript</h2>

          {activeTranscript.length > 0 && (
            <button
              onClick={handleCopyAll}
              className="flex items-center gap-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-sm text-gray-200"
            >
              {copied ? (
                <span className="text-green-400">Copied!</span>
              ) : (
                <>
                  <Copy className="w-4 h-4" /> Copy All
                </>
              )}
            </button>
          )}
        </div>

        <div className="max-h-80 overflow-y-auto space-y-2 pr-1 [scrollbar-width:thin]">
          {fetching ? (
            <div className="text-gray-400 text-sm animate-pulse">Fetching transcript...</div>
          ) : Array.isArray(activeTranscript) && activeTranscript.length > 0 ? (
            activeTranscript.map((line, i) => (
              <div
                key={i}
                className="p-2 bg-gray-900 border border-gray-800 rounded-lg text-sm"
              >
                <span className="text-xs text-blue-400 font-mono block mb-0.5">
                  {line.time}
                </span>
                <span className="text-gray-200">{line.text}</span>
              </div>
            ))
          ) : (
            <div className="text-gray-400 text-sm">No transcript available.</div>
          )}
        </div>
      </div>
    </div>
  );
}
