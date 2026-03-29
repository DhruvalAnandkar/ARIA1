from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.mongo.user_preferences import get_user_preferences, update_user_preferences
from app.models.mongo.user_profile import get_user_profile, update_user_profile
from app.models.postgres.user import User
from app.schemas.user import (
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserPreferencesResponse,
    UserProfileResponse,
)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return UserProfileResponse(
        user_id=str(user.id),
        email=user.email,
        name=user.name,
        created_at=user.created_at.isoformat(),
    )


@router.patch("/profile", response_model=UserProfileResponse)
async def update_profile_endpoint(
    req: UpdateProfileRequest,
    user: User = Depends(get_current_user),
):
    updates = req.model_dump(exclude_none=True)
    if updates:
        await update_user_profile(str(user.id), updates)

    return UserProfileResponse(
        user_id=str(user.id),
        email=user.email,
        name=updates.get("name", user.name),
        created_at=user.created_at.isoformat(),
    )


@router.get("/preferences")
async def get_preferences_endpoint(user: User = Depends(get_current_user)):
    prefs = await get_user_preferences(str(user.id))
    if not prefs:
        return {"message": "No preferences found"}
    return prefs


@router.patch("/preferences")
async def update_preferences_endpoint(
    req: UpdatePreferencesRequest,
    user: User = Depends(get_current_user),
):
    updates = req.model_dump(exclude_none=True)
    if updates:
        await update_user_preferences(str(user.id), updates)

    prefs = await get_user_preferences(str(user.id))
    return prefs
