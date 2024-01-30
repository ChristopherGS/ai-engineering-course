import whisper
import pprint

from shared.settings import DATA_DIR

PRINTER = pprint.PrettyPrinter(indent=4)


def transcribe_audio() -> None:
    """Transcribe an mp3 audio file to text."""

    # For production usage you would cache this call.
    # To increase the quality of transcription, use a different model size:
    # https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages
    model = whisper.load_model("tiny")

    # # We use this prompt to help whisper correctly transcribe names and companies
    # (this is not guaranteed work, particularly with smaller models!)
    prompt = (
        "This is a podcast called The Latent Space podcast which talks about AI Engineering. The"
        "interviewers are Shawn Wang (AKA swyx not Michael Oswitz) and Alessio Fanelli the "
        "interviewee is Dylan Patel of Semi Analysis"
    )

    # important to convert pathlib Path to a string
    result = model.transcribe(
        str(DATA_DIR / "episode44.mp3"),
        language="en",
        verbose=True,
        initial_prompt=prompt,
    )

    PRINTER.pprint(result["text"][:500])
    PRINTER.pprint(result["segments"][:5])
    PRINTER.pprint(
        "Very cool! Transcription of this quality even a few years ago would have required a "
        "research team and weeks of work. Welcome to the future."
    )


if __name__ == "__main__":
    transcribe_audio()
