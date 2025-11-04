from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, EmailStr, Field


class Settings(BaseSettings):
    project_name: str = Field(default="GeM Bid Analyzer")
    api_v1_prefix: str = Field(default="/api/v1")

    database_url: str = Field(default="sqlite:///./gem_analyzer.db", env="DATABASE_URL")
    sqlalchemy_echo: bool = Field(default=False, env="SQLALCHEMY_ECHO")

    access_token_expire_minutes: int = Field(default=60 * 12, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_secret_key: str = Field(default="change-me", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")

    upload_dir: Path = Field(default=Path("storage/uploads"))
    export_dir: Path = Field(default=Path("storage/exports"))
    template_dir: Path = Field(default=Path("app/templates"))

    allowed_origins: List[str] = Field(default_factory=lambda: ["*"], env="ALLOWED_ORIGINS")

    translation_provider: str = Field(default="libretranslate", env="TRANSLATION_PROVIDER")
    libretranslate_url: str = Field(default="https://libretranslate.de", env="LIBRETRANSLATE_URL")
    libretranslate_api_key: Optional[str] = Field(default=None, env="LIBRETRANSLATE_API_KEY")
    translation_chunk_size: int = Field(default=3500, env="TRANSLATION_CHUNK_SIZE")
    translation_chunk_overlap: int = Field(default=200, env="TRANSLATION_CHUNK_OVERLAP")

    smtp_host: str = Field(default="smtp.example.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    email_sender: EmailStr = Field(default="noreply@example.com", env="EMAIL_SENDER")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for directory in (settings.upload_dir, settings.export_dir):
        directory.mkdir(parents=True, exist_ok=True)
    return settings
