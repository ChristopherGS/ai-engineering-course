import pprint
import textwrap

from llama_cpp import Llama

from shared.grammar import load_grammar
from shared.settings import N_GPU_LAYERS, DATA_DIR, MISTRAL_7B_FILE
from shared.timer_utils import timer

PRINTER = pprint.PrettyPrinter(indent=4)


@timer
def run_llm(user_prompt: str, llm: Llama, json_format: bool = False):
    # n_ctx is the *total* context window, which includes the input prompt and the output
    # n_gpu_layers is set to greater than 0 to tell llama.cpp to use GPUs (this makes
    # inference much faster). If you only have access to CPU, then set it to 0.
    # chat_format is not a well documented (but important) parameter, you can find the source code here: https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/llama_chat_format.py
    system_prompt = "You are a helpful assistant, reply to any queries in English. Do not make up information."

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=-1,  # use n_ctx
        temperature=0.1,
        grammar=load_grammar() if json_format else None,
    )

    return response


if __name__ == "__main__":
    tiny_llm = Llama(
        model_path=str(DATA_DIR / "tiny_llama_v0.3.gguf"),
        n_ctx=512,
        n_gpu_layers=N_GPU_LAYERS,
        chat_format="chatml",
    )
    # https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
    mistral_llm = Llama(
        model_path=str(DATA_DIR / MISTRAL_7B_FILE),
        n_ctx=512,
        n_gpu_layers=N_GPU_LAYERS,
        chat_format="mistral-instruct",
    )

    # You'd do something more comprehensive like this: http://ciar.org/h/notes.test-prompts.json
    USER_PROMPTS = [
        "Hello, how are you?",
        "What is the capital of Spain?",
        "On a scale of 1-10 how good is Blade Runner 2049?",
    ]
    results = []
    for index, prompt in enumerate(USER_PROMPTS):
        tiny_result = run_llm(user_prompt=prompt, llm=tiny_llm)
        mistral_result = run_llm(user_prompt=prompt, llm=mistral_llm)
        results.append((prompt, tiny_result, mistral_result))

    # Now, print the results wrapping the lines with textwrap
    wrapper = textwrap.TextWrapper(width=80)

    for result in results:
        print(f"Prompt: {result[0]} \n")
        print(
            f'Tiny response: {wrapper.fill(result[1]["choices"][0]["message"]["content"].strip())} \n'
        )
        print(
            f'Mistral response: {wrapper.fill(result[2]["choices"][0]["message"]["content"].strip())}'
        )
        print("-----------------------------------\n")
