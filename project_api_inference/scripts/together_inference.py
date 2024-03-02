import json
import os
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel, Field

# Retrieve the API key from environment variables
TOGETHER_API_KEY: str = os.environ.get("TOGETHER_API_KEY", "")

# Initialize the OpenAI client with the API key
client: OpenAI = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz",
)


def run_together_inference_batch() -> str:
    """
    Executes a batch inference request to the LLM chat model and returns the response.

    This function demonstrates how to send a batch request for completions and return the model's response.

    Returns:
        A string containing the content of the chat model's response.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant"},
            {"role": "user", "content": "Tell me about San Francisco"},
        ],
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=128,
    )

    return chat_completion.choices[0].message.content


def run_together_inference_stream(user_prompt: str) -> str:
    """
    Executes a streaming inference request to the LLM chat model with a given user prompt and returns the concatenated response.

    Args:
        user_prompt (str): The user's prompt to send to the chat model.

    Returns:
        str: A string containing the concatenated content of the chat model's streaming response.
    """
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI assistant"},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=500,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        yield content


class User(BaseModel):
    """Defines the schema for a user with name and address fields."""

    name: str = Field(..., description="The user's name")
    address: str = Field(..., description="The user's address")


def run_together_inference_schema(user_prompt: str) -> Dict[str, Any]:
    """
    Executes an inference request to the LLM chat model with a given user prompt, using a JSON schema for the response format. Returns the parsed JSON response.

    Args:
        user_prompt (str): The user's prompt to send to the chat model, expecting a structured JSON response based on a predefined schema.

    Returns:
        Dict[str, Any]: The parsed JSON object representing the structured data response from the chat model.
    """
    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        response_format={"type": "json_object", "schema": User.schema_json()},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers in JSON.",
            },
            {
                "role": "user",
                "content": "Create a user named Stringer Bell, who lives at 42, Game Avenue.",
            },
        ],
    )

    created_user = json.loads(chat_completion.choices[0].message.content)
    return created_user


def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """
    Simulates fetching the current weather for a given location.

    Parameters:
    - location: The location for which to get the weather.
    - unit: The unit of temperature, either 'fahrenheit' or 'celsius'.

    Returns:
    A JSON string containing the weather information.
    """
    if "chicago" in location.lower():
        return json.dumps({"location": "Chicago", "temperature": "13", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "55", "unit": unit}
        )
    elif "new york" in location.lower():
        return json.dumps({"location": "New York", "temperature": "11", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def run_together_inference_tools() -> None:
    """
    Demonstrates executing an inference request with the capability to call external tools or functions.
    This function showcases how external function calls can enrich the LLM's responses.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g., San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can access external functions. The responses from these function calls will be appended to this dialogue. Please provide responses based on the information from these function calls.",
        },
        {
            "role": "user",
            "content": "What is the current temperature of New York, San Francisco, and Chicago?",
        },
    ]

    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_current_weather":
                function_response = get_current_weather(
                    location=function_args.get("location"),
                    unit=function_args.get("unit", "fahrenheit"),
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        function_enriched_response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
        )
        print(
            json.dumps(
                function_enriched_response.choices[0].message.model_dump(), indent=2
            )
        )


if __name__ == "__main__":
    for part in run_together_inference_stream(user_prompt="Tell me about Paris"):
        print(part, end="", flush=True)
