import json
from pathlib import Path

import numpy as np
import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric, GEval
from deepeval.models import DeepEvalBaseModel
from deepeval.test_case import LLMTestCase
from deepeval.test_case import LLMTestCaseParams
from llama_cpp import Llama, LlamaGrammar

from part_2_llama_cpp.llm import run_llm
from shared.settings import DATA_DIR, N_GPU_LAYERS


class CustomEvaluationModel(DeepEvalBaseModel):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def load_grammar(self) -> LlamaGrammar:
        file_path = DATA_DIR / "llama.gbnf"
        print(f"Reading grammar file from: {file_path}")  # Debug print
        with open(file_path, "r") as handler:
            content = handler.read()
            return LlamaGrammar.from_string(content)

    def _call(self, prompt: str) -> str:
        chat_model: Llama = self.load_model()
        return chat_model(prompt, max_tokens=256, grammar=self.load_grammar())[
            "choices"
        ][0]["text"]  # hack

    def get_model_name(self):
        return "Custom llama.cpp model"


@pytest.fixture(scope="module")
def llm() -> Llama:
    return Llama(
        model_path=str(DATA_DIR / "mixtral_8x7b_instruct_v0.1.Q4_K_M.gguf"),
        n_ctx=32000,
        n_gpu_layers=N_GPU_LAYERS,
        chat_format="llama-2",  # this is very close to the mixtral chat format
    )


@pytest.fixture(scope="module")
def custom_deep_eval_model(llm: Llama) -> CustomEvaluationModel:
    return CustomEvaluationModel(model=llm)


@pytest.fixture(scope="module")
def test_data_dir() -> Path:
    return DATA_DIR / "test_data"


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


PROMPT_BASE = (
    "Summarize this transcript in a JSON output with keys 'title' and 'summary'"
)


@pytest.mark.parametrize(
    "system_prompt, prompt_type, model_name, chat_format",
    [
        (
            PROMPT_BASE,
            "base",
            "mixtral_8x7b_instruct_v0.1.Q4_K_M.gguf",
            "llama-2",
        ),  # Q4
        # (PROMPT_BASE, "base", "Mixtral_8x7B_Instruct_v0.1.gguf", "llama-2"),
    ],
)
def test_insights_case(
    system_prompt: str,
    prompt_type: str,
    model_name: str,
    chat_format: str,
    test_data_dir: Path,
    llm: Llama,
    custom_deep_eval_model: CustomEvaluationModel,
) -> None:
    # Given
    with open(test_data_dir / "transcript_044_micro.json") as handler:
        transcript = json.load(handler)

    user_prompt = f"{system_prompt}: {transcript}"
    actual_output = run_llm(llm=llm, user_prompt=user_prompt, json_format=True)

    # Save the actual_output to a file
    output_file = (
        test_data_dir / f"actual_output_{prompt_type}_{model_name}_{chat_format}.json"
    )
    content_str = actual_output["choices"][0]["message"]["content"]

    # Since 'content' is a string that contains JSON, you need to parse it as JSON
    try:
        content = json.loads(content_str.strip())
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        # Handle the error or debug further
        raise e

    with open(output_file, "w") as file:
        json.dump(content, file, indent=4)

    # When
    # Note that only input and actual_output is mandatory.
    test_case = LLMTestCase(
        input=user_prompt,
        # Replace this with your actual LLM application
        actual_output=content["summary"],
        expected_output="fragmented nature of the supply chain and existing monopolies",
        context=[user_prompt],  # required to use HallucinationMetric
    )

    chat_model = custom_deep_eval_model

    # metric 1: insights
    insights_metric = GEval(
        name="Insights",
        model=chat_model,  # must pass in
        threshold=0.5,  # default is 0.5
        # NOTE: you can only provide either criteria or evaluation_steps, and not both
        evaluation_steps=[
            "Determine if the actual output contains the key insights from the input transcription."
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    # This metric uses vectara's hallucination evaluation model.
    # metric 2: hallucination
    hallucination_metric = HallucinationMetric(threshold=0.5)

    # Initialize a dictionary to store the scores for each metric
    all_scores = {}
    for metric in [insights_metric, hallucination_metric]:
        metric.measure(test_case)
        print(insights_metric.score)
        print(insights_metric.reason)
        # Accumulate the scores in the dictionary
        all_scores[metric.__name__] = {
            "score": metric.score,
            "details": {
                "alignment": getattr(metric, "alignment_score", None),
                "inclusion": getattr(metric, "inclusion_score", None),
                "reason": getattr(metric, "reason", None),
            },
        }
    output_file = (
        test_data_dir
        / f"actual_output_{prompt_type}_{model_name}_{chat_format}_summary_score.json"
    )
    with open(output_file, "w") as file:
        json.dump(all_scores, file, indent=4, cls=CustomJSONEncoder)

    # insights test case fails
    assert_test(test_case, [hallucination_metric, insights_metric])


# to use confident-ai:
# deepeval login (will ask for API key)
# PYTHONPATH=. deepeval test run part_4_eval/test_llm.py
