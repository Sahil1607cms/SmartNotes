"""
Media processing service for audio/video transcription and summarization.
Handles file uploads, video-to-audio conversion, and transcription.
"""
import os
import tempfile
import gc
import torch
from typing import List, Dict, Any
from faster_whisper import WhisperModel, BatchedInferencePipeline
from dotenv import load_dotenv
import subprocess
import asyncio

load_dotenv()

# Initialize device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

def convert_video_to_audio(input_file: str, output_file: str, speed: float = 1.25) -> bool:
    """
    Convert an MP4 file to MP3 using ffmpeg.
    
    Args:
        input_file: Path to input video file
        output_file: Path to output audio file
        speed: Audio speed multiplier (default 1.25)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        command = [
            "ffmpeg",
            "-i", input_file,
            "-vn",  # No video
            "-filter:a", f"atempo={speed}",  # Speed up the audio
            "-acodec", "libmp3lame",  # MP3 codec
            "-b:a", "192k",  # Audio bitrate
            "-y",  # Overwrite output file if exists
            output_file
        ]
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        return False
    except FileNotFoundError:
        print("ffmpeg not found. Please install ffmpeg.")
        return False


def transcribe_audio(audio_path: str, model_size: str = "small", batch_size: int = 8) -> List[Dict[str, Any]]:
    """
    Transcribe audio file using Whisper model.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        batch_size: Batch size for transcription
    
    Returns:
        List of transcript segments with time and text
    """
    try:
        # Clean up GPU memory
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Initialize Whisper model
        compute_type = "float16" if device == "cuda" else "int8"
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        batched_model = BatchedInferencePipeline(model=model)
        
        # Transcribe
        segments, info = batched_model.transcribe(
            audio_path, 
            batch_size=batch_size, 
            word_timestamps=True
        )
        
        # Format transcript
        transcript = []
        for segment in segments:
            transcript.append({
                "time": f"{segment.start:.2f}s -> {segment.end:.2f}s",
                "text": segment.text.strip()
            })
        
        # Clean up
        del model
        del batched_model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return transcript
    
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise


async def process_media_file(file_path: str, filename: str) -> List[Dict[str, Any]]:
    """
    Process a media file (audio or video) and return transcript.
    Runs blocking operations in a thread pool to avoid blocking the event loop.
    
    Args:
        file_path: Path to the uploaded file
        filename: Original filename
    
    Returns:
        List of transcript segments
    """
    temp_audio_path = None
    
    def _process_sync():
        """Synchronous processing function to run in thread pool"""
        nonlocal temp_audio_path
        
        # Determine file type
        file_ext = os.path.splitext(filename)[1].lower()
        is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        is_audio = file_ext in ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac']
        
        if not (is_video or is_audio):
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # If video, convert to audio first
        if is_video:
            temp_audio_path = tempfile.mktemp(suffix='.mp3')
            success = convert_video_to_audio(file_path, temp_audio_path)
            if not success:
                raise Exception("Failed to convert video to audio")
            audio_path = temp_audio_path
        else:
            audio_path = file_path
        
        # Transcribe audio (this is a blocking operation)
        transcript = transcribe_audio(audio_path)
        
        return transcript
    
    try:
        # Run blocking operations in thread pool
        loop = asyncio.get_event_loop()
        transcript = await loop.run_in_executor(None, _process_sync)
        return transcript
    
    finally:
        # Clean up temporary audio file if created
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass

