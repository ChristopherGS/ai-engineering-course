import json
from pathlib import Path
from typing import Iterator
import argparse
import logging

from llama_cpp import (
    Llama,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    LlamaGrammar,
)

from app.config import MODEL_DIR, PROMPT_DIR, TRANSCRIPT_DIR, SUMMARY_DIR
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_system_prompt() -> str:
    with open(PROMPT_DIR / "summarize_podcast_transcript.md.j2", "r") as file:
        return file.read()

def prepare_user_prompt(transcript_path: Path) -> str:
    with open(transcript_path, "r", encoding='utf-8') as file:
        transcript = file.read()
    return transcript

def load_model(model_path: Path) -> Llama:
    return Llama(
        model_path=str(model_path),
        n_ctx=settings.llm.CONTEXT_WINDOW,
        n_gpu_layers=settings.llm.N_GPU_LAYERS,
        chat_format=settings.llm.CHAT_FORMAT
    )

def prepare_output(
    llm: Llama,
    user_prompt: str,
    system_prompt: str
) -> CreateChatCompletionResponse | Iterator[CreateChatCompletionStreamResponse]:
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=settings.llm.MAX_TOKENS,
        stop=[],
        temperature=settings.llm.TEMPERATURE,
        response_format={
            "type": "json_object",
            "schema": {
              "type": "object",
              "properties": {
                "summary": {
                  "type": "string",
                  "minLength": 200,
                  "maxLength": 300,
                  "description": "A brief summary of the interview content."
                },
                "quote": {
                  "type": "string",
                  "description": "A quote from the interview subject that captures a key theme of the podcast."
                },
                "interview_date": {
                  "type": "string",
                  "format": "date",
                  "description": "The date when the interview was conducted."
                }
              },
              "required": [
                "summary",
                "interview_date",
              ]
            }
        }
    )
    return result['choices'][0]['message']['content']

def summarize_transcript(transcript_path: Path, llm: Llama) -> None:
    system_prompt = load_system_prompt()
    user_prompt = prepare_user_prompt(transcript_path=transcript_path)
    return prepare_output(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

def write_summary_to_file(summary: str, transcript_file_name: Path):
    summary_file_name = f"{transcript_file_name.stem}_summary.json"
    summary_path = SUMMARY_DIR / summary_file_name
    with open(summary_path, "w") as file:
        file.write(summary)
    logger.info(f"Summary written to {summary_path}")

def run_summary_pipeline(model: str, transcript_file_name: str) -> None:
    logger.info(f"Loading model: {model}")
    llm = load_model(model_path=MODEL_DIR / model)
    logger.info("Loaded LLM")

    transcript_path = TRANSCRIPT_DIR / transcript_file_name
    logger.info(f'Summarizing transcript: {transcript_file_name}')
    summary = summarize_transcript(transcript_path=transcript_path, llm=llm)
    logger.info(f'Summary prepared: {summary}')

    write_summary_to_file(summary, Path(transcript_file_name))
    logger.info(f'Summary written to file')


if __name__ == "__main__":
    # Set up command-line argument parsing (you could also use Typer: https://github.com/tiangolo/typer)
    parser = argparse.ArgumentParser(description='Run the transcript summarization pipeline.')
    parser.add_argument('--model', '-m', help='local llm', default=settings.llm.MODEL_FILE_NAME)
    parser.add_argument('--transcript-file', '-t', help='Transcript file name', required=True)

    args = parser.parse_args()

    run_summary_pipeline(model=args.model, transcript_file_name=args.transcript_file)
