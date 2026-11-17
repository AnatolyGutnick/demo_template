"""Environment-driven settings. Nothing environment-specific is hard-coded in tests.

Values come from environment variables or a local `.env` file (see `.env.example`).
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", env_ignore_empty=True)

    base_url: str = Field(default="https://console.akeyless.io", description="UI base URL")
    api_url: str = Field(default="https://api.akeyless.io", description="API base URL")

    user_name: str = Field(default="", description="Default test user")
    user_password: str = Field(default="", description="Default test user password")

    # Akeyless admin identity for test setup (API key auth method of a dedicated test account)
    akeyless_access_id: str = Field(default="", description="Admin access ID")
    akeyless_access_key: SecretStr = Field(default=SecretStr(""), description="Admin access key")
    test_root: str = Field(default="/qa-autotest", description="Folder for all test items")

    default_timeout_ms: int = 10_000
    api_timeout_ms: int = 15_000


settings = Settings()
