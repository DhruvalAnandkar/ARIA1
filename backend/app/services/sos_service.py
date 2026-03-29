import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.postgres.sos_event import SOSEvent
from app.services.tts_service import speak
from app.utils.logger import get_logger

logger = get_logger(__name__)

SOS_MESSAGE = "EMERGENCY. I NEED IMMEDIATE HELP. PLEASE CALL FOR ASSISTANCE NOW."
SOS_TRIGGER_WORDS = {"help", "emergency", "danger", "pain", "hurt", "scared", "fire", "stop"}


def contains_sos_trigger(text: str) -> bool:
    """Check if text contains any SOS trigger words."""
    lower = text.lower()
    return any(word in lower for word in SOS_TRIGGER_WORDS)


async def trigger_sos(
    user_id: str,
    db: AsyncSession,
    latitude: float | None = None,
    longitude: float | None = None,
) -> tuple[str, str]:
    """Trigger an SOS event. Returns (sentence, audio_filename)."""
    # Log to database
    event = SOSEvent(
        user_id=uuid.UUID(user_id),
        latitude=latitude,
        longitude=longitude,
    )
    db.add(event)
    await db.flush()

    # Generate urgent audio
    audio_filename = await speak(SOS_MESSAGE, emotion="sos")

    logger.warning(
        "sos_triggered",
        user_id=user_id,
        lat=latitude,
        lng=longitude,
    )

    return SOS_MESSAGE, audio_filename
