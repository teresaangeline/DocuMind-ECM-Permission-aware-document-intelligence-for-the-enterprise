from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-5"
    data_dir: Path = Path("./data")
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5


settings = Settings()
