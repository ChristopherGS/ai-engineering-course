import json
from pathlib import Path
from typing import Iterator

from llama_cpp import (
    Llama,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    LlamaGrammar,
)
import typer

from app.config import MODEL_DIR, PROMPT_DIR, TRANSCRIPT_DIR
from app.config import settings


app = typer.Typer()

def load_system_prompt() -> str:
    with open(settings.PROMPT_DIR / "summarize_podcast_transcript.md.j2", "r") as file:
        return file.read()

def prepare_user_prompt(transcript_path: Path) -> str:
    with open(transcript_path, "r") as file:
        transcript = json.load(file)

    return json.dumps(transcript)


def load_model(model_path: Path) -> Llama:
    return Llama(
        model_path=str(model_path),
        n_ctx=settings.llm.CONTEXT_WINDOW,
        n_gpu_layers=settings.llm.N_GPU_LAYERS,
    )

def prepare_output(
    llm: Llama,
    user_prompt: str,
    system_prompt: str,
    grammar: LlamaGrammar | None = None,
) -> CreateChatCompletionResponse | Iterator[CreateChatCompletionStreamResponse]:
    return llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=settings.LLM_MAX_TOKENS,
        stop=[],
        temperature=settings.TEMPERATURE,
        grammar=grammar,
    )

def summarize_transcript(transcript: str, llm: Llama) -> None:

    # Load prompt from jinja templates
    system_prompt = load_system_prompt()

    user_prompt = prepare_user_prompt(transcript_path=settings.TRANSCRIPT_DIR / transcript)

    output = prepare_output(llm=llm, system_prompt=system_prompt, user_prompt=user_prompt)



def save_summary(episode_id: int, summary: str) -> None:
    ...

@app.command()
def run_summary_pipeline(
    model: str = typer.Option(settings.llm.MODEL_FILE_NAME, "--model", "-m", help="local llm"),
    transcript_file_name: str = typer.Option(..., "--transcript-file", "-t", help="Transcript file name"),
) -> None:
    typer.echo(f"Loading model: {model}")
    llm = load_model(model_path=MODEL_DIR / model)
    typer.echo("Loaded LLM")


if __name__ == "__main__":
    app()