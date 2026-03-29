from elevenlabs import ElevenLabs

from app.config import settings
from app.utils.audio import generate_audio_path
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ElevenLabs built-in voice IDs mapped to emotions
VOICE_MAP = {
    "neutral": "21m00Tcm4TlvDq8ikWAM",  # Rachel — warm, clear
    "happy": "AZnzlk1XvdvUeBnXmlld",    # Domi — bright, energetic
    "sad": "EXAVITQu4vr4xnSDxMaL",      # Bella — soft, gentle
    "fear": "yoZ06aMxZJJ28mfd3POQ",      # Sam — urgent, direct
    "angry": "yoZ06aMxZJJ28mfd3POQ",     # Sam — firm
    "surprise": "21m00Tcm4TlvDq8ikWAM",  # Rachel
    "disgust": "21m00Tcm4TlvDq8ikWAM",   # Rachel
    "guide": "21m00Tcm4TlvDq8ikWAM",     # Rachel — for GUIDE mode
    "sos": "yoZ06aMxZJJ28mfd3POQ",       # Sam — loud and clear
}

_client: ElevenLabs | None = None


def _get_client() -> ElevenLabs:
    global _client
    if _client is None:
        _client = ElevenLabs(api_key=settings.elevenlabs_api_key)
    return _client


async def speak(text: str, emotion: str = "neutral") -> str:
    """Convert text to speech using emotion-matched voice.

    Returns the filename (not full path) of the saved MP3.
    """
    voice_id = VOICE_MAP.get(emotion, VOICE_MAP["neutral"])
    output_path = generate_audio_path(f"aria_{emotion}")

    client = _get_client()
    audio_generator = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_monolingual_v1",
    )

    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    filename = output_path.split("/")[-1]
    logger.info("tts_generated", emotion=emotion, file=filename, text_length=len(text))
    return filename
