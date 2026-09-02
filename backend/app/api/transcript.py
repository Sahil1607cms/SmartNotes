from fastapi import APIRouter
from youtube_transcript_api._errors import IpBlocked, NoTranscriptFound
from app.services.youtube import get_transcripts

router = APIRouter()


@router.get("/transcript/")
def transcript_api(url: str):
    """Fetches YouTube video transcript segments."""
    try:
        transcripts = get_transcripts(url)
        return {"transcript": transcripts}
    except IpBlocked:
        return {"error": "Your IP is blocked by YouTube. Try again later or from a different network."}
    except NoTranscriptFound:
        return {"error": "Transcript not found for this video."}
    except Exception as e:
        return {"error": str(e)}
