import pathlib
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# Project Directories
ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR: pathlib.Path = ROOT / 'data_engineering' / 'prompts'
TRANSCRIPT_DIR: pathlib.Path = ROOT / 'data' / 'transcripts'
SUMMARY_DIR: pathlib.Path = ROOT / 'data' / 'summaries'
MODEL_DIR: pathlib.Path = ROOT / 'data_engineering' / 'models'
INDEX_DIR: pathlib.Path = ROOT / "app" / "index_store"

class LLMSettings(BaseSettings):
    """
    Defines the settings for the Large Language Model (LLM).

    Attributes:
        CONTEXT_WINDOW (int): The context window size for the LLM.
        N_GPU_LAYERS (int): The number of GPU layers to be used by the LLM.
        MAX_TOKENS (int): The maximum number of tokens to be generated in one response.
        TEMPERATURE (float): The temperature setting for the LLM's creativity in responses.
        MODEL (str): The identifier for the LLM model to be used.
        TOGETHER_API_KEY (str): The API key for accessing the LLM, expected to be loaded from the environment.
    """
    CONTEXT_WINDOW: int = 16000
    N_GPU_LAYERS: int = 1
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.8
    MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    TOGETHER_API_KEY: str  # picked up from environment

class Settings(BaseSettings):
    """
    Configuration settings for the application, including database and LLM configurations.

    Attributes:
        SQLALCHEMY_DATABASE_URI (Optional[str]): The database connection URI.
        llm (LLMSettings): Nested settings for configuring the Large Language Model.
    """
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"
    llm: LLMSettings = LLMSettings()

    class Config:
        """
        Configuration class for settings.

        Attributes:
            case_sensitive (bool): Specifies if the configuration keys should be case-sensitive.
        """
        case_sensitive: bool = True

settings: Settings = Settings()
