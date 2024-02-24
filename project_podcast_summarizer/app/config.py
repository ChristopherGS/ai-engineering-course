import pathlib

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from typing import List, Optional, Union


# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT_DIR = ROOT / 'data_engineering' / 'prompts'
TRANSCRIPT_DIR = ROOT / 'data' / 'transcripts'
SUMMARY_DIR = ROOT / 'data' / 'summaries'
MODEL_DIR = ROOT / 'data_engineering' / 'models'

class LLMSettings(BaseSettings):
    CONTEXT_WINDOW: int = 16000
    N_GPU_LAYERS: int = 1
    MAX_TOKENS: int = 256
    TEMPERATURE: float = 0.1
    MODEL_FILE_NAME: str = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    CHAT_FORMAT: str = 'mistral-instruct'


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"
    llm: LLMSettings = LLMSettings()

    class Config:
        case_sensitive = True


settings = Settings()
