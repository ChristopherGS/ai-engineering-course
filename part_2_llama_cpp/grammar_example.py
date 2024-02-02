import json
import pprint

from llama_cpp import Llama

from shared.settings import N_GPU_LAYERS, DATA_DIR
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
        response_format={"type": "json_object"} if json_format else None,
    )

    return response


if __name__ == "__main__":
    # https://huggingface.co/mistralai/Mixtral-8x7B-Instruct-v0.1
    mixtral_llm = Llama(
        model_path=str(DATA_DIR / "mixtral_8x7b_instruct_v0.1.Q4_K_M.gguf"),
        n_ctx=32000,
        n_gpu_layers=N_GPU_LAYERS,
        chat_format="llama-2",  # this is very close to the mixtral chat format
    )
    with open(DATA_DIR / "transcript_044.json", "r") as handler:
        transcript_text = handler.readlines()

    prompt = (
        "Summarize this podcast episode in 100 words or less. Do not halluncinate. "
        "Think it through step by step. If the summary is bad I will be fired."
        f"here is the transcript: {transcript_text[0]}"
    )
    result = run_llm(llm=mixtral_llm, user_prompt=prompt, json_format=True)
    with open(DATA_DIR / "summary_044.json", "w") as handler:
        json.dump(result, handler)
