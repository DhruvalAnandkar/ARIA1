from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://aria:aria@localhost:5432/aria"
    mongo_url: str = "mongodb://aria:aria@localhost:27017/aria?authSource=admin"
    redis_url: str = "redis://localhost:6379/0"

    # API Keys
    gemini_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    google_maps_api_key: str = ""

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours (simple auth)

    # Vision
    vision_provider_order: str = "gemini,openai,claude,local"

    # Audio
    audio_output_dir: str = "/app/audio_output"
    audio_cleanup_max_age_seconds: int = 300  # 5 minutes

    # App
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
