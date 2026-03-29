import json

from app.db.redis import get_redis
from app.utils.logger import get_logger

logger = get_logger(__name__)

SESSION_PREFIX = "aria:sign_session:"
SESSION_TTL = 3600  # 1 hour


async def get_session(user_id: str) -> dict:
    """Get or create a sign session for a user."""
    redis = get_redis()
    key = f"{SESSION_PREFIX}{user_id}"
    data = await redis.get(key)

    if data:
        return json.loads(data)

    session = {
        "letter_buffer": [],
        "last_emotion": "neutral",
        "last_confidence": 0.0,
        "language": "en",
        "frame_count": 0,
    }
    await redis.setex(key, SESSION_TTL, json.dumps(session))
    return session


async def update_session(user_id: str, session: dict) -> None:
    """Persist updated session state."""
    redis = get_redis()
    key = f"{SESSION_PREFIX}{user_id}"
    await redis.setex(key, SESSION_TTL, json.dumps(session))


async def append_letter(user_id: str, letter: str) -> dict:
    """Append a letter to the user's buffer and return updated session."""
    session = await get_session(user_id)
    if letter.strip():
        session["letter_buffer"].append(letter)
    session["frame_count"] += 1
    await update_session(user_id, session)
    return session


async def clear_buffer(user_id: str) -> dict:
    """Clear the letter buffer and return updated session."""
    session = await get_session(user_id)
    session["letter_buffer"] = []
    await update_session(user_id, session)
    return session


async def set_language(user_id: str, language: str) -> dict:
    """Set the output language for the session."""
    session = await get_session(user_id)
    session["language"] = language
    await update_session(user_id, session)
    return session


async def set_emotion(user_id: str, emotion: str, confidence: float) -> dict:
    """Update the detected emotion in the session."""
    session = await get_session(user_id)
    session["last_emotion"] = emotion
    session["last_confidence"] = confidence
    await update_session(user_id, session)
    return session


async def get_and_clear_buffer(user_id: str) -> tuple[str, str]:
    """Get raw text from buffer and clear it. Returns (raw_text, emotion)."""
    session = await get_session(user_id)
    raw_text = "".join(session["letter_buffer"]).strip()
    emotion = session["last_emotion"]
    session["letter_buffer"] = []
    await update_session(user_id, session)
    return raw_text, emotion


async def should_build_sentence(user_id: str, threshold: int = 6) -> bool:
    """Check if the buffer has enough letters to trigger sentence building."""
    session = await get_session(user_id)
    return len(session["letter_buffer"]) >= threshold


async def delete_session(user_id: str) -> None:
    """Delete the session (on disconnect)."""
    redis = get_redis()
    key = f"{SESSION_PREFIX}{user_id}"
    await redis.delete(key)
