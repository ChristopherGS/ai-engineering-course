import json

from openai import OpenAI
import os

from pydantic import BaseModel, Field

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz",
)


def run_together_inference():
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant",
            },
            {
                "role": "user",
                "content": "Tell me about San Francisco",
            },
        ],
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=128,
    )

    print(chat_completion.choices[0].message.content)


def run_together_inference_stream():
    stream = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant",
            },
            {
                "role": "user",
                "content": "Tell me about San Francisco",
            },
        ],
        stream=True,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        max_tokens=256,
    )

    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)


# Define the schema for the output.
class User(BaseModel):
    name: str = Field(description="user name")
    address: str = Field(description="address")


def run_together_inference_schema():
    # Call the LLM with the JSON schema
    chat_completion = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        response_format={"type": "json_object", "schema": User.model_json_schema()},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that answers in JSON.",
            },
            {
                "role": "user",
                "content": "Create a user named Alice, who lives in 42, Wonderland Avenue.",
            },
        ],
    )

    created_user = json.loads(chat_completion.choices[0].message.content)
    print(json.dumps(created_user, indent=2))


# Example function to make available to model
def get_current_weather(location, unit="fahrenheit"):
    """Get the weather for some location"""
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


def run_together_inference_tools():
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
                            "description": "The city and state, e.g. San Francisco, CA",
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
            "content": "What is the current temperature of New York, San Francisco and Chicago?",
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
                    unit=function_args.get("unit"),
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
    run_together_inference_tools()
