"""
Faster-Whisper parallel transcription with overlapping chunks + word-level overlap-trimming.

Features:
- Splits an input audio file into overlapping chunks (default 30s chunks, 0.8s overlap).
- Uses a ProcessPoolExecutor to transcribe chunks in parallel.
- Loads a Faster-Whisper model inside each worker process (safe for process-based parallelism).
- Uses word-level timestamps to remove duplicate words that fall inside overlap regions.
- Merges transcriptions in chronological order and writes a final `transcription.txt`.

Notes for your system (RTX 2050, ~4GB VRAM):
- Default `max_workers` is 1 to avoid running out of VRAM. You can try 2 but watch memory.
- Requires ffmpeg installed on your PATH (pydub uses it).
- Install dependencies: `pip install faster-whisper pydub`

"""

import os
import math
import tempfile
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Tuple
from faster_whisper import WhisperModel, BatchedInferencePipeline
import subprocess

# We'll import faster_whisper inside worker initializer to avoid pickling issues
MODEL = WhisperModel("turbo", device="cuda", compute_type="float16")  # or "cpu" if needed
MODEL_NAME = "turbo"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
BATCH_SIZE = 8


def model_initializer(model_name: str, device: str = "cuda", compute_type: str = "float16", batch_size: int = 8):
    """Initializer for worker processes. Loads the Faster-Whisper model once per process."""
    global MODEL, MODEL_NAME, DEVICE, COMPUTE_TYPE, BATCH_SIZE
    from faster_whisper import WhisperModel
    MODEL_NAME = model_name
    DEVICE = device
    COMPUTE_TYPE = compute_type
    BATCH_SIZE = batch_size
    MODEL = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)


def transcribe_chunk_worker(args) -> Dict:
    """Worker to transcribe a single chunk. Returns a dict with chunk_offset and segments (with word timestamps).

    args should be a tuple: (chunk_path, chunk_start_seconds)
    """
    global MODEL, BATCH_SIZE
    from faster_whisper import BatchedInferencePipeline
    chunk_path, chunk_start = args

    # create pipeline per-process (using the already loaded global MODEL)
    pipeline = BatchedInferencePipeline(model=MODEL)

    segments, info = pipeline.transcribe(chunk_path, batch_size=BATCH_SIZE, word_timestamps=True)

    # Convert segments to serializable structures (floats & strings)
    out_segments = []
    for seg in segments:
        seg_dict = {
            "start": float(seg.start),
            "end": float(seg.end),
            "text": str(seg.text),
            "words": []
        }
        # seg.words is iterable of objects with start, end, and word/text
        # We'll capture each word/token with timestamps
        if hasattr(seg, "words") and seg.words is not None:
            for w in seg.words:
                # some versions return 'word' attr, some 'text'
                word_text = getattr(w, "word", None) or getattr(w, "token", None) or getattr(w, "text", "")
                seg_dict["words"].append({
                    "start": float(w.start),
                    "end": float(w.end),
                    "word": str(word_text),
                })
        out_segments.append(seg_dict)

    return {"chunk_start": chunk_start, "segments": out_segments}


def get_audio_duration(input_path: str) -> float:
    """Return audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "a:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        input_path,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0 or not proc.stdout:
        raise RuntimeError(f"ffprobe failed to get duration for {input_path}: {proc.stderr}")
    try:
        return float(proc.stdout.strip())
    except ValueError:
        raise RuntimeError(f"Unable to parse duration from ffprobe output: {proc.stdout}")


def split_audio_to_chunks(input_path: str, chunk_length_s: int = 30, overlap_s: float = 0.8, tmp_dir: str = None) -> List[Tuple[str, float]]:
    """Split input audio into chunks with a given overlap using ffmpeg (no pydub required).

    Returns list of tuples: (temp_chunk_path, chunk_start_seconds)
    Requires ffmpeg/ffprobe to be installed and on PATH.
    """
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="fw_chunks_")

    total_s = get_audio_duration(input_path)
    chunk_s = float(chunk_length_s)
    overlap_s = float(overlap_s)

    step = chunk_s - overlap_s
    if step <= 0:
        raise ValueError("chunk_length_s must be greater than overlap_s")

    chunks = []
    start = 0.0
    idx = 0
    while start < total_s - 1e-6:
        duration = min(chunk_s, total_s - start)
        chunk_path = os.path.join(tmp_dir, f"chunk_{idx:04d}.wav")
        # ffmpeg command: seek (-ss) then take duration (-t), convert to mono 16k WAV
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-ss",
            str(start),
            "-t",
            str(duration),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-vn",
            chunk_path,
        ]
        # suppress ffmpeg output unless it fails
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"ffmpeg failed to create chunk at {start}s: {e}")

        chunks.append((chunk_path, start))
        idx += 1
        start += step

    return chunks


def merge_segments_remove_overlap(results: List[Dict], overlap_trim_tolerance: float = 0.05) -> List[Dict]:
    """Merge segments from multiple chunk results, trimming overlapped words using word timestamps.

    Input: results = [ { 'chunk_start': s, 'segments': [ {start,end,text,words:[{start,end,word},...]}, ... ] }, ... ]
    Output: merged segments [{'start':..., 'end':..., 'text':..., 'words':[...]}] ordered by time.
    """
    # Collect all words across chunks, shifting times by chunk_start
    all_words = []
    for res in results:
        chunk_offset = res["chunk_start"]
        for seg in res["segments"]:
            for w in seg.get("words", []):
                w_global_start = w["start"] + chunk_offset
                w_global_end = w["end"] + chunk_offset
                all_words.append({
                    "start": w_global_start,
                    "end": w_global_end,
                    "word": w["word"],
                })

    # Sort all words by start time
    all_words.sort(key=lambda x: x["start"])

    # Remove duplicates due to overlap: if a word starts before last_end - tolerance, we skip it
    merged_words = []
    last_end = -1.0
    for w in all_words:
        if w["start"] + overlap_trim_tolerance <= last_end:
            # This word starts within the previous region -> skip (it's duplicate from overlap)
            continue
        merged_words.append(w)
        last_end = max(last_end, w["end"])

    # Reconstruct text segments by grouping words into segments separated by a pause > 1.2s (tunable)
    episodes = []
    if not merged_words:
        return episodes

    current = {"start": merged_words[0]["start"], "end": merged_words[0]["end"], "words": [merged_words[0]]}
    for w in merged_words[1:]:
        # If there's a big silence between words, start a new segment
        if w["start"] - current["end"] > 1.2:
            # finalize current
            episodes.append(current)
            current = {"start": w["start"], "end": w["end"], "words": [w]}
        else:
            current["words"].append(w)
            current["end"] = w["end"]
    episodes.append(current)

    # Build text for each episode by joining words (this will insert spaces naively)
    merged_segments = []
    for e in episodes:
        text = ""
        for i, w in enumerate(e["words"]):
            # simple spacing rule: no space before punctuation-like tokens
            if i > 0 and not (w["word"] in [",", ".", "!", "?", ":", ";"]):
                text += " "
            text += w["word"]
        merged_segments.append({
            "start": e["start"],
            "end": e["end"],
            "text": text,
        })

    return merged_segments


def parallel_transcribe(input_audio_path: str,
                        model_name: str = "turbo",
                        device: str = "cuda",
                        compute_type: str = "float16",
                        chunk_length_s: int = 30,
                        overlap_s: float = 0.8,
                        max_workers: int = 1,
                        batch_size: int = 8,
                        cleanup: bool = True,
                        tmp_dir: str = None) -> List[Dict]:
    """Top-level helper: splits audio, transcribes chunks in parallel, merges, and returns merged segments.

    By default configured conservatively for a small GPU: max_workers=1.
    """
    global BATCH_SIZE
    BATCH_SIZE = batch_size

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="fw_run_")

    chunks = split_audio_to_chunks(input_audio_path, chunk_length_s=chunk_length_s, overlap_s=overlap_s, tmp_dir=tmp_dir)

    # Prepare args for workers
    work_args = [(path, start) for (path, start) in chunks]

    results = []
    try:
        # Use ProcessPoolExecutor so each worker can load the model into its own process memory space.
        with ProcessPoolExecutor(max_workers=max_workers, initializer=model_initializer, initargs=(model_name, device, compute_type, batch_size)) as exe:
            futures = {exe.submit(transcribe_chunk_worker, arg): arg for arg in work_args}
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    results.append(res)
                    print(f"Completed chunk starting at {res['chunk_start']:.2f}s")
                except Exception as e:
                    print("Worker failed:", e)
    finally:
        # cleanup chunk files if requested
        if cleanup:
            try:
                shutil.rmtree(tmp_dir)
            except Exception:
                pass

    # Merge results (word-level dedup across overlaps)
    merged = merge_segments_remove_overlap(results)

    # write transcription to file
    with open("transcription.txt", "w", encoding="utf-8") as f:
        for seg in merged:
            line = f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}"
            f.write(line + "\n")

    return merged


if __name__ == "__main__":
    # ------------------ SIMPLE RUNNER (hardcoded variables) ------------------
    # You can edit these variables below and then run:
    #    python faster_whisper_parallel_transcribe.py
    # This avoids using CLI args and keeps a one-command run simple for your setup.

    INPUT_PATH = "sho.mp3"   # <-- change to your file
    MODEL_NAME = "turbo"
    DEVICE = "cuda"
    COMPUTE_TYPE = "float16"
    CHUNK_LEN = 30
    OVERLAP = 0.8
    WORKERS = 1    # keep low for RTX 2050 (4GB VRAM)
    BATCH_SIZE = 8

    print("Starting split+parallel transcription (simple runner)...")
    merged = parallel_transcribe(INPUT_PATH, model_name=MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE,
                                 chunk_length_s=CHUNK_LEN, overlap_s=OVERLAP, max_workers=WORKERS, batch_size=BATCH_SIZE)

    print("Done. Final transcript written to transcription.txt")

    # -------------------------------------------------------------------------
