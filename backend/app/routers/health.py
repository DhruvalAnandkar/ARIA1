import time

from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])

_start_time = time.time()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - _start_time, 1),
    }


@router.get("/health/services")
async def health_services():
    results = {}

    # PostgreSQL
    try:
        from app.db.postgres import engine

        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        results["postgres"] = "ok"
    except Exception as e:
        results["postgres"] = f"error: {e}"

    # MongoDB
    try:
        from app.db.mongo import get_mongo_db

        db = get_mongo_db()
        await db.command("ping")
        results["mongo"] = "ok"
    except Exception as e:
        results["mongo"] = f"error: {e}"

    # Redis
    try:
        from app.db.redis import get_redis

        r = get_redis()
        await r.ping()
        results["redis"] = "ok"
    except Exception as e:
        results["redis"] = f"error: {e}"

    # Vision providers
    from app.services.vision.manager import vision_manager

    results["vision_providers"] = vision_manager.get_provider_status()

    return results
