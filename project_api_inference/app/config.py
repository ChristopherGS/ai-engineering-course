from typing import ClassVar

from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """
    Configuration settings for the Large Language Model (LLM) interactions.

    Attributes:
        CONTEXT_WINDOW (int): The number of tokens in the context window.
        MAX_TOKENS (int): The maximum number of tokens that can be generated in a chat completion.
        TEMPERATURE (float): Controls the randomness of output generation, with a range between 0 and 2.
        MODEL (str): Identifier for the model used in chat completions.
        CHAT_FORMAT (str): The format used for chat interactions.
        TOGETHER_API_KEY (str): The API key for accessing the Together platform, picked up from environment variables.
    """

    CONTEXT_WINDOW: int = 16000
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.8
    MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    BASE_URL: str = "https://api.together.xyz"
    TOGETHER_API_KEY: str  # Will be picked up from environment variables


class Settings(BaseSettings):
    """
    Application settings, aggregating configurations for different components.

    Attributes:
        llm (LLMSettings): Settings related to the Large Language Model.
    """

    llm: LLMSettings = LLMSettings()

    class Config:
        """
        Configuration class for Settings.

        Attributes:
            case_sensitive (bool): If True, field names are case-sensitive.
        """

        case_sensitive: ClassVar[bool] = True


settings = Settings()
