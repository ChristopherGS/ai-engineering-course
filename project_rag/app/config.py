import pathlib
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / 'data_engineering' / 'prompts'
TRANSCRIPT_DIR = ROOT / 'data' / 'transcripts'
SUMMARY_DIR = ROOT / 'data' / 'summaries'
MODEL_DIR = ROOT / 'data_engineering' / 'models'

# New
INDEX_DIR = ROOT / "app" / "index_store"


class LLMSettings(BaseSettings):
    CONTEXT_WINDOW: int = 16000
    N_GPU_LAYERS: int = 1
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.8
    MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    TOGETHER_API_KEY: str  # picked up from environment


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"
    llm: LLMSettings = LLMSettings()

    class Config:
        case_sensitive = True


settings = Settings()
