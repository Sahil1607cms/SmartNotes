import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Flashcards({ summary }) {
  const STORAGE_KEY = "flashcards_data";
  const [cards, setCards] = useState([]);
  const [shuffled, setShuffled] = useState([]);
  const [activeCard, setActiveCard] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const savedCards = localStorage.getItem(STORAGE_KEY);
    if (savedCards) {
      try {
        const parsedCards = JSON.parse(savedCards);
        setCards(parsedCards);
      } catch (err) {
        console.error("Failed to load flashcards from localStorage:", err);
      }
    }
  }, []);

  useEffect(() => {
    if (cards && cards.length > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cards));
    }
  }, [cards]);

  const handleGenerateFlashcards = async () => {
    if (!summary || summary.trim() === "") {
      alert("Summary not available yet!");
      return;
    }
    
    // Check if flashcards already exist in state (from localStorage)
    if (cards && cards.length > 0) {
      console.log("Flashcards already exist in localStorage. Skipping API call.");
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/summarize-flashcard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      
      if (data.status === "success" && data.bullet_points) {
        // Convert bullet points to card objects
        const newCards = data.bullet_points.map((point, index) => ({
          id: index,
          text: point
        }));
        setCards(newCards);
      } else {
        alert("❌ Failed to generate flashcards: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      console.error(err);
      alert("❌ Failed to generate flashcards.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearFlashcards = () => {
    if (window.confirm("Are you sure you want to clear all flashcards?")) {
      setCards([]);
      setShuffled([]);
      setActiveCard(null);
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  useEffect(() => {
    if (cards && cards.length > 0) {
      const s = [...cards].sort(() => Math.random() - 0.5);
      setShuffled(s.slice(0, 6));
    }
  }, [cards]); 

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-6 bg-black text-white relative">
      {/* Generate Flashcards Button */}
      <div className="mb-8 flex gap-4">
        <button
          onClick={handleGenerateFlashcards}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Flashcards"}
        </button>
        
        {cards.length > 0 && (
          <button
            onClick={handleClearFlashcards}
            className="px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-500"
          >
            Clear Flashcards
          </button>
        )}
      </div>

      {/* Flashcards Grid */}
      {shuffled.length > 0 && (
        <div className="grid grid-cols-3 gap-6">
          {shuffled.map((card, index) => (
            <motion.div
              key={index}
              onClick={() => setActiveCard(card)}
              whileHover={{ scale: 1.15 }}
              className="bg-gradient-to-br from-gray-700 to-gray-900 rounded-2xl p-6 cursor-pointer shadow-lg h-40 flex items-center justify-center text-center w-[190px]"
            >
              <p className="text-sm font-medium line-clamp-3">{card.text}</p>
            </motion.div>
          ))}
        </div>
      )}

      {/* Active card popup */}
      <AnimatePresence>
        {activeCard && (
          <motion.div
            className="fixed inset-0 bg-black/70 backdrop-blur flex items-center justify-center p-6 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setActiveCard(null)}
          >
            <motion.div
              className="bg-gray-900 rounded-2xl p-10 max-w-xl text-center shadow-2xl"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.5, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 className="text-2xl font-bold mb-4">Key Point</h2>
              <p className="text-lg mb-6 whitespace-pre-wrap">{activeCard.text}</p>
              <button
                onClick={() => setActiveCard(null)}
                className="px-6 py-2 bg-yellow-500 text-black font-semibold rounded-xl hover:bg-yellow-400"
              >
                Close
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
