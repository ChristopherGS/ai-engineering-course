from pydantic import BaseModel


class ChatInput(BaseModel):
    """
    Represents the input for the chat inference endpoint.

    Attributes:
        user_message (str): The user's message to the AI model.
        max_tokens (int): The maximum number of tokens to generate in the response.
    """

    user_message: str = "Tell me about Paris"
    max_tokens: int = 100