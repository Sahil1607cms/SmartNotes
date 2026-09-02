import re
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import IpBlocked, NoTranscriptFound

logger = logging.getLogger(__name__)


def extract_video_id(url_or_id: str) -> str:
    """Extract 11-character YouTube video ID from various URL formats."""
    regex = r"(?:v=|\/|be\/|embed\/|shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url_or_id)
    if match:
        return match.group(1)
    return url_or_id.strip()


def format_time_compact(seconds: float) -> str:
    """Formats seconds into compact MM:SS or HH:MM:SS string."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_transcripts(url_or_id: str) -> list[dict]:
    """
    Fetches transcript segments for a YouTube video.
    Returns list of dicts with compact timestamps: [{'time': '00:00', 'text': 'Hello world'}]
    """
    video_id = extract_video_id(url_or_id)
    api = YouTubeTranscriptApi()

    data = None
    try:
        data = api.fetch(video_id, languages=["en", "hi"])
    except Exception as e:
        logger.info(f"Primary fetch with languages failed ({e}), attempting fallback fetch...")
        try:
            data = api.fetch(video_id)
        except Exception as e2:
            logger.info(f"Fallback fetch failed ({e2}), attempting list()...")
            try:
                transcript_list = api.list(video_id)
                t = transcript_list.find_transcript(["en", "hi"]) or transcript_list.find_generated_transcript(["en", "hi"])
                data = t.fetch()
            except Exception as e3:
                logger.error(f"All transcript fetch attempts failed for video {video_id}: {e3}")
                raise e3

    formatted = []
    if data:
        for item in data:
            if isinstance(item, dict):
                start = float(item.get("start", 0.0))
                text = str(item.get("text", "")).replace("\n", " ").strip()
            else:
                start = float(getattr(item, "start", 0.0))
                text = str(getattr(item, "text", "")).replace("\n", " ").strip()

            if text:
                formatted.append({
                    "time": format_time_compact(start),
                    "text": text
                })

    return formatted


def clean_transcript_text(full_text: str) -> str:
    """Removes filler words (English & Hindi) and normalizes whitespace."""
    filler_words_en = r"\b(uh|um|erm|like|you know|so|yeah|basically|actually|right|I mean|kinda|sorta|well)\b"
    filler_words_hi = r"\b(अच्छा|हम्म|मतलब|चलिए|चलो|ठीक है|अरे|उफ़|ओह|सुनो|जानते हो|वैसे|देखो|बस|तो|हाँ|है ना|यानी|क्या कहते हैं|वैसे तो)\b"
    fillers = f"({filler_words_en}|{filler_words_hi})"
    cleaned = re.sub(fillers, "", full_text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()
