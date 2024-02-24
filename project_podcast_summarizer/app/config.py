import pathlib
from typing import Optional

from pydantic_settings import BaseSettings

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / 'data_engineering' / 'prompts'
TRANSCRIPT_DIR = ROOT / 'data' / 'transcripts'
SUMMARY_DIR = ROOT / 'data' / 'summaries'
MODEL_DIR = ROOT / 'data_engineering' / 'models'

class LLMSettings(BaseSettings):
    CONTEXT_WINDOW: int = 16000
    N_GPU_LAYERS: int = 1
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.2
    MODEL_FILE_NAME: str = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    CHAT_FORMAT: str = 'mistral-instruct'


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"
    llm: LLMSettings = LLMSettings()

    class Config:
        case_sensitive = True


settings = Settings()
