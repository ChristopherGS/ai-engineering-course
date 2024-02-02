from llama_cpp import LlamaGrammar

from shared.settings import DATA_DIR


def load_grammar() -> LlamaGrammar:
    file_path = DATA_DIR / "llama.gbnf"
    print(f"Reading grammar file from: {file_path}")  # Debug print
    with open(file_path, "r") as handler:
        content = handler.read()
        return LlamaGrammar.from_string(content)
