from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: str


class UpdateProfileRequest(BaseModel):
    name: str | None = None


class UserPreferencesResponse(BaseModel):
    user_id: str
    default_mode: str
    language: str
    voice_style: str
    tts_speed: float
    obstacle_scan_interval_ms: int
    high_contrast: bool
    large_text: bool
    sign_mode: dict
    guide_mode: dict


class UpdatePreferencesRequest(BaseModel):
    default_mode: str | None = None
    language: str | None = None
    voice_style: str | None = None
    tts_speed: float | None = None
    obstacle_scan_interval_ms: int | None = None
    high_contrast: bool | None = None
    large_text: bool | None = None
    sign_mode: dict | None = None
    guide_mode: dict | None = None
