from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Core settings
    anthropic_api_key: str = ""
    app_name: str = "The Equalizer"
    debug: bool = True

    # Plivo settings (for WhatsApp)
    plivo_auth_id: Optional[str] = None
    plivo_auth_token: Optional[str] = None
    plivo_whatsapp_number: Optional[str] = None

    # Twitter/X settings (for social media posts)
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_token_secret: Optional[str] = None

    # Demo mode (safe default)
    demo_mode: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore any extra env vars


@lru_cache()
def get_settings() -> Settings:
    return Settings()
