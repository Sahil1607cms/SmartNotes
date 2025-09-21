import React from "react";
import { Routes, Route} from "react-router-dom";
import Layout from "./components/Layout.jsx"; // Layout will include Sidebar + Navbar
import YouTubeSummarizer from "./pages/YoutubeSummarizer.jsx";
import AudioVideoSummarizer from "./pages/AudioVideoSummarizer.jsx";
import PdfTextSummarizer from "./pages/PdfTextSummarizer.jsx";
import LiveMeetingTranscriber from "./pages/LiveMeetingTranscriber.jsx";
import History from "./pages/History.jsx";

function App() {
  return (
    <div className="h-screen">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<YouTubeSummarizer />} />
            <Route path="/yt" element={<YouTubeSummarizer />} />
            <Route path="/audio-video" element={<AudioVideoSummarizer />} />
            <Route path="/pdf-text" element={<PdfTextSummarizer />} />
            <Route path="/meeting" element={<LiveMeetingTranscriber />} />
            <Route path="/history" element={<History />} />
          </Route>
        </Routes>
    </div>
  );
}

export default App;
