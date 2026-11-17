"""Environment-driven settings. Nothing environment-specific is hard-coded in tests.

Values come from environment variables or a local `.env` file (see `.env.example`).
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    base_url: str = Field(default="http://localhost:3000", description="UI base URL")
    api_url: str = Field(default="http://localhost:3000/api", description="API base URL")

    user_name: str = Field(default="", description="Default test user")
    user_password: str = Field(default="", description="Default test user password")

    default_timeout_ms: int = 10_000
    api_timeout_ms: int = 15_000


settings = Settings()
