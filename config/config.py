"""Typed environment configuration and CLI override support."""
from pathlib import Path
from typing import Literal
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AmazonSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AMAZON_", extra="ignore")

    env: str = Field(default="production", validation_alias="AMAZON_ENV")
    base_url: str = Field(default="https://www.amazon.com", validation_alias="AMAZON_BASE_URL")
    headless: bool = Field(default=True, validation_alias="AMAZON_HEADLESS")
    viewport_width: int = Field(default=1440, validation_alias="AMAZON_VIEWPORT_WIDTH")
    viewport_height: int = Field(default=900, validation_alias="AMAZON_VIEWPORT_HEIGHT")
    locale: str = Field(default="en-US", validation_alias="AMAZON_LOCALE")
    timezone: str = Field(default="America/New_York", validation_alias="AMAZON_TIMEZONE")
    timeout_ms: int = Field(default=30_000, validation_alias="AMAZON_TIMEOUT_MS")
    retries: int = Field(default=1, validation_alias="AMAZON_RETRIES")
    browser: Literal["chromium", "firefox", "webkit"] = Field(default="chromium", validation_alias="AMAZON_BROWSER")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
        validation_alias="AMAZON_USER_AGENT",
    )

    def apply_environment_yaml(self, yaml_path: Path | None = None) -> "AmazonSettings":
        """Overlay the named environment from YAML unless explicit env variables are set."""
        path = yaml_path or Path(__file__).with_name("environments.yaml")
        if not path.exists():
            return self
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        values = data.get(self.env, {})
        if values:
            object.__setattr__(self, "base_url", values.get("base_url", self.base_url))
            object.__setattr__(self, "locale", values.get("locale", self.locale))
            object.__setattr__(self, "timezone", values.get("timezone", self.timezone))
            width, height = values.get("viewport", [self.viewport_width, self.viewport_height])
            object.__setattr__(self, "viewport_width", width)
            object.__setattr__(self, "viewport_height", height)
            object.__setattr__(self, "headless", values.get("headless", self.headless))
        return self


settings = AmazonSettings().apply_environment_yaml()

