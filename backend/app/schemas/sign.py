from pydantic import BaseModel


class SpeakRequest(BaseModel):
    text: str
    emotion: str = "neutral"
    language: str = "en"


class SpeakResponse(BaseModel):
    sentence: str
    audio_url: str


class SOSRequest(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class TranscriptEntryResponse(BaseModel):
    id: str
    text: str
    raw_letters: str | None
    emotion: str
    language: str
    created_at: str
