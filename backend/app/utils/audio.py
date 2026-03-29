import os
import time
import uuid
import asyncio

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def ensure_audio_dir() -> None:
    os.makedirs(settings.audio_output_dir, exist_ok=True)


def generate_audio_path(prefix: str = "aria") -> str:
    ensure_audio_dir()
    filename = f"{prefix}_{uuid.uuid4().hex}.mp3"
    return os.path.join(settings.audio_output_dir, filename)


def get_audio_filename(full_path: str) -> str:
    return os.path.basename(full_path)


async def cleanup_old_audio() -> None:
    """Remove audio files older than the configured max age."""
    while True:
        try:
            now = time.time()
            max_age = settings.audio_cleanup_max_age_seconds
            audio_dir = settings.audio_output_dir

            if not os.path.exists(audio_dir):
                await asyncio.sleep(60)
                continue

            for filename in os.listdir(audio_dir):
                filepath = os.path.join(audio_dir, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > max_age:
                        os.remove(filepath)
                        logger.debug("removed_old_audio", file=filename, age_seconds=file_age)
        except Exception:
            logger.exception("audio_cleanup_error")

        await asyncio.sleep(60)
