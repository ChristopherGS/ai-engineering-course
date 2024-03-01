import pathlib

from pydantic_settings import BaseSettings

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "data_engineering" / "prompts"


class LLMSettings(BaseSettings):
    CONTEXT_WINDOW: int = 16000
    N_GPU_LAYERS: int = 1
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.2
    MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    CHAT_FORMAT: str = "mistral-instruct"
    TOGETHER_API_KEY: str  # will be picked up from environment variable


class Settings(BaseSettings):
    llm: LLMSettings = LLMSettings()

    class Config:
        case_sensitive = True


settings = Settings()
