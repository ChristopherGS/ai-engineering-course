import json
import json
from pathlib import Path
from typing import Iterator

from django.core.management.base import BaseCommand
from llama_cpp import (
    Llama,
    CreateChatCompletionResponse,
    CreateChatCompletionStreamResponse,
    LlamaGrammar,
)

from django.conf import settings
from transcriber.monitoring.time_utilities import timer


# Test quality with episode 241 (pieter levels)


def load_prompt():
    with open(settings.PROMPT_DIR / "summarize_podcast_transcript.md.j2", "r") as file:
        return file.read()


def prepare_user_prompt(episode_dir: Path) -> str:
    metadata_file = next(episode_dir.glob("*metadata*.json"), None)
    transcript_file = next(episode_dir.glob("*transcript*.json"), None)

    # If all files are found, read and concatenate their contents
    # if metadata_file and segments_file and transcript_file:
    if metadata_file:
        with open(metadata_file, "r") as file:
            metadata = json.load(file)
        with open(transcript_file, "r") as file:
            transcript = json.load(file)

        del metadata["summary_detail"]  # can be really long (e.g. Latent Space)
        metadata["summary"] = metadata["summary"][
            :500
        ]  # can also be quite long (Latent Space)
        metadata_str = json.dumps(metadata)
        transcript_str = json.dumps(transcript)
    else:
        raise FileNotFoundError(f"missing a file: {episode_dir}")

    return f"{metadata_str}\n{transcript_str}"


@timer
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


def get_grammar() -> LlamaGrammar:
    file_path = settings.LLM_MODEL_DIR / settings.JSON_GRAMMAR_FILE
    print(f"Reading grammar file from: {file_path}")  # Debug print
    with open(file_path, "r") as handler:
        content = handler.read()
        return LlamaGrammar.from_string(content)


class Command(BaseCommand):
    help = "Analyze transcripts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            help="local llm",
            nargs="?",
            default=f"{settings.MODEL_FILE_NAME}",
        )
        parser.add_argument(
            "--transcript_directory", type=str, help="transcript directory"
        )

    @timer
    def load_model(self, model: str) -> Llama:
        self.stdout.write(f"Loading model: {model}")
        return Llama(
            model_path=str(settings.LLM_MODEL_DIR / model),
            n_ctx=settings.CONTEXT_WINDOW,
            n_gpu_layers=settings.N_GPU_LAYERS,
        )

    def handle(self, *args, **options):
        model = options["model"]
        transcript_directory = options["transcript_directory"]
        llm = self.load_model(model=model)
        path = Path(transcript_directory)
        missing_summary_count = 0

        # Load templates
        system_prompt = load_prompt()

        # Assume there's only one set of files for each episode in the directory
        for episode_dir in path.iterdir():
            if episode_dir.is_dir():  # Only proceed if it's a directory
                summary_files = list(episode_dir.glob("*summary*.json"))
                # Check if summary file exists
                if summary_files:
                    self.stdout.write(
                        f"Skipping summary for as already exists {episode_dir.name}"
                    )
                    continue

                missing_summary_count += 1
                self.stdout.write(f"Preparing input for {episode_dir.name}")
                full_prompt = prepare_user_prompt(episode_dir=episode_dir)
                grammar = get_grammar()

                try:
                    output = prepare_output(
                        llm=llm,
                        user_prompt=full_prompt,
                        system_prompt=system_prompt,
                        grammar=grammar,
                    )
                except Exception as e:
                    print(e)
                    self.stdout.write(f"Error analyzing: {episode_dir.name} \n {e}")
                    continue

                # Call the model with prompts
                # output = llm(full_prompt + system_prompt, max_tokens=100, temperature=0.3, top_p=0.1, echo=False)False
                final_result = output["choices"][0]["message"]["content"].strip()
                self.stdout.write(f"Model says: {final_result}")

                try:
                    # Parse the JSON string into a Python dictionary
                    data = json.loads(final_result)

                    # Write the dictionary as a JSON file without newlines
                    with open(episode_dir / "summary.json", "w") as handler:
                        json.dump(
                            data, handler, ensure_ascii=False, separators=(",", ":")
                        )
                except json.JSONDecodeError as error:
                    print(error)
