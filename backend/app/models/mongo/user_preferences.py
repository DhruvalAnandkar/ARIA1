from datetime import datetime, timezone

from app.db.mongo import get_mongo_db

DEFAULT_PREFERENCES = {
    "default_mode": "sign",
    "language": "en",
    "voice_style": "rachel",
    "tts_speed": 1.0,
    "obstacle_scan_interval_ms": 1500,
    "high_contrast": False,
    "large_text": False,
    "sign_mode": {
        "auto_speak": True,
        "buffer_threshold": 6,
    },
    "guide_mode": {
        "speak_clear_path": False,
        "haptic_on_obstacle": True,
    },
}


async def get_user_preferences(user_id: str) -> dict | None:
    db = get_mongo_db()
    return await db.user_preferences.find_one({"user_id": user_id}, {"_id": 0})


async def create_user_preferences(user_id: str) -> dict:
    db = get_mongo_db()
    prefs = {
        "user_id": user_id,
        **DEFAULT_PREFERENCES,
        "updated_at": datetime.now(timezone.utc),
    }
    await db.user_preferences.insert_one(prefs)
    prefs.pop("_id", None)
    return prefs


async def update_user_preferences(user_id: str, updates: dict) -> dict | None:
    db = get_mongo_db()
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.user_preferences.update_one({"user_id": user_id}, {"$set": updates})
    return await get_user_preferences(user_id)
