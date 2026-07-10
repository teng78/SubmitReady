from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SUBMITREADY_", env_file=".env", extra="ignore")

    data_dir: Path = Path("data")
    builtin_rules_dir: Path = Path("../examples/rules")
    database_url: str = "sqlite:///data/submitready.db"
    max_upload_bytes: int = 20 * 1024 * 1024
    max_zip_files: int = 2_000
    max_extracted_bytes: int = 100 * 1024 * 1024
    allow_untrusted_execution: bool = False
    output_limit: int = 16 * 1024

    @property
    def workspace_dir(self) -> Path:
        return self.data_dir / "workspaces"

    @property
    def custom_rules_dir(self) -> Path:
        return self.data_dir / "rules"


def get_settings() -> Settings:
    return Settings()
