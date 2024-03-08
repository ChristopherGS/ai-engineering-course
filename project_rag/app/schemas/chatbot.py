from pydantic import BaseModel


class ChatInput(BaseModel):
    """
    Represents the input for the chat inference endpoint.

    Attributes:
        user_message (str): The user's message to the AI model.
    """

    user_message: str = "Tell me about Developer Tea"