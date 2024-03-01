import pathlib

from pydantic_settings import BaseSettings

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / "data_engineering" / "prompts"


class LLMSettings(BaseSettings):
    CONTEXT_WINDOW: int = 16000

    # The maximum number of tokens that can be generated in the chat completion.
    MAX_TOKENS: int = 1000

    # What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
    # make the output more random, while lower values like 0.2 will make it more
    # focused and deterministic.
    TEMPERATURE: float = 0.8
    MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    CHAT_FORMAT: str = "mistral-instruct"
    TOGETHER_API_KEY: str  # will be picked up from environment variable


class Settings(BaseSettings):
    llm: LLMSettings = LLMSettings()

    class Config:
        case_sensitive = True


settings = Settings()
