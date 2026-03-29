from datetime import datetime, timezone

from app.db.mongo import get_mongo_db


async def get_user_profile(user_id: str) -> dict | None:
    db = get_mongo_db()
    return await db.user_profiles.find_one({"user_id": user_id}, {"_id": 0})


async def create_user_profile(user_id: str, name: str) -> dict:
    db = get_mongo_db()
    profile = {
        "user_id": user_id,
        "name": name,
        "avatar_url": None,
        "updated_at": datetime.now(timezone.utc),
    }
    await db.user_profiles.insert_one(profile)
    profile.pop("_id", None)
    return profile


async def update_user_profile(user_id: str, updates: dict) -> dict | None:
    db = get_mongo_db()
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.user_profiles.update_one({"user_id": user_id}, {"$set": updates})
    return await get_user_profile(user_id)
