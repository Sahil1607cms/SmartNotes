import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx"; // Layout will include Sidebar + Navbar
import YouTubeSummarizer from "./pages/YoutubeSummarizer.jsx";
import AudioVideoSummarizer from "./pages/AudioVideoSummarizer.jsx";
import PdfTextSummarizer from "./pages/PdfTextSummarizer.jsx";
import LiveMeetingTranscriber from "./pages/LiveMeetingTranscriber.jsx";
import History from "./pages/History.jsx";
import PublicOnlyRoute from "./components/PublicOnlyRoute.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Login from "./pages/Login.jsx";

function App() {
  return (
    <div className="h-screen bg-black">
      <Routes>
          <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/yt" replace />} />
          <Route path="/yt" element={<YouTubeSummarizer />} />
          <Route path="/audio-video" element={<AudioVideoSummarizer />} />
          <Route path="/pdf-text" element={<PdfTextSummarizer />} />
          <Route path="/meeting" element={<LiveMeetingTranscriber />} />
          <Route path="/history" element={<History />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}

export default App;
