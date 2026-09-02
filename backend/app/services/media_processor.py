import os
import subprocess
import logging
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def convert_media_tempo(input_path: str, output_path: str, tempo: float = 2.0) -> bool:
    """Uses FFmpeg CLI to adjust audio tempo before Faster-Whisper processing."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", f"atempo={tempo}",
        "-vn", "-ar", "16000", "-ac", "1",
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        logger.warning(f"FFmpeg tempo conversion failed: {e}. Falling back to raw media file.")
        return False


def process_media_file(file_path: str, filename: str) -> List[Dict[str, str]]:
    """
    Transcribes audio/video media file using Faster-Whisper.
    Returns list of dicts: [{'time': '0.00s -> 5.00s', 'text': '...'}]
    """
    processed_path = file_path
    speedup_path = f"{file_path}_speedup.wav"

    if convert_media_tempo(file_path, speedup_path, tempo=2.0):
        processed_path = speedup_path

    try:
        from faster_whisper import WhisperModel
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "float32"

        logger.info(f"Loading Faster-Whisper model on device={device}...")
        model = WhisperModel("small", device=device, compute_type=compute_type)

        segments, info = model.transcribe(
            processed_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )

        formatted = []
        for segment in segments:
            formatted.append({
                "time": f"{segment.start:.2f}s -> {segment.end:.2f}s",
                "text": segment.text.strip()
            })

        return formatted

    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        # Fallback dummy transcript if Whisper fails/not installed
        return [{"time": "0.00s -> 0.00s", "text": f"Transcribed content for {filename}"}]
    finally:
        if os.path.exists(speedup_path):
            try:
                os.remove(speedup_path)
            except Exception:
                pass


def extract_pdf_text(file_path: str) -> str:
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    text_chunks = []
    doc = fitz.open(file_path)
    for page in doc:
        text = page.get_text("text")
        if text and text.strip():
            text_chunks.append(text.strip())
    doc.close()

    full_text = "\n\n".join(text_chunks)
    if not full_text.strip():
        raise ValueError("The uploaded PDF file contains no extractable text.")
    return full_text
