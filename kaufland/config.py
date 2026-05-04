from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KauflandSettings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="KAUFLAND_",
        extra="ignore",
    )

    app_base_url: str = "https://app.kaufland.net"
    app_version: str = "6.7.0"
    app_basic_user: str = Field(min_length=1)
    app_basic_password: str = Field(min_length=1)

    timeout: float = Field(default=20.0, gt=0)
    language: str = Field(default="de", min_length=1)


@lru_cache
def get_settings() -> KauflandSettings:
    return KauflandSettings()
