import json
from pathlib import Path

import numpy as np
import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric, GEval, BaseMetric
from deepeval.models import DeepEvalBaseModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from llama_cpp import Llama, LlamaGrammar

from shared.grammar import load_grammar
from shared.settings import DATA_DIR, N_GPU_LAYERS, MISTRAL_7B_FILE


def write_metric_scores(
    test_case: LLMTestCase, metrics: list[BaseMetric], write_dir: Path
):
    all_scores = {}
    for metric in metrics:
        metric.measure(test_case)
        all_scores[metric.__name__] = {
            "score": metric.score,
            "details": {
                "alignment": getattr(metric, "alignment_score", None),
                "inclusion": getattr(metric, "inclusion_score", None),
                "reason": getattr(metric, "reason", None),
            },
        }

    output_file = write_dir / "test_summary_score.json"
    with open(output_file, "w") as _file:
        json.dump(all_scores, _file, indent=4, cls=CustomJSONEncoder)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


class CustomEvaluationModel(DeepEvalBaseModel):
    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def load_grammar(self) -> LlamaGrammar:
        return load_grammar()

    def _call(self, prompt: str) -> str:
        chat_model: Llama = self.load_model()
        response = chat_model.create_completion(
            prompt, max_tokens=256, grammar=self.load_grammar()
        )

        return response["choices"][0]["text"]

    def get_model_name(self):
        return "Custom Open Source Model"


@pytest.fixture(scope="module")
def test_data_dir() -> Path:
    return DATA_DIR / "test_data"


@pytest.fixture(scope="module")
def short_transcript(test_data_dir: Path) -> str:
    with open(test_data_dir / "transcript_044_micro.json", "r") as handler:
        return json.load(handler)


@pytest.fixture(scope="module")
def llm() -> Llama:
    return Llama(
        model_path=str(DATA_DIR / MISTRAL_7B_FILE),
        n_ctx=32000,
        n_batch=N_GPU_LAYERS,
        chat_format="mistral-instruct",
    )


@pytest.fixture(scope="module")
def custom_deep_eval_model(llm: Llama) -> CustomEvaluationModel:
    return CustomEvaluationModel(model=llm)


def test_model_outputs(
    short_transcript: str,
    llm: Llama,
    custom_deep_eval_model: CustomEvaluationModel,
    test_data_dir: Path,
):
    # Given
    system_prompt = (
        "Summarize this transcript in a JSON output with keys 'title' and 'summary'"
    )
    user_prompt = f"{system_prompt}: {short_transcript}"
    actual_output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=-1,  # use n_ctx
        temperature=0.1,
        grammar=load_grammar(),
    )
    output = json.loads(actual_output["choices"][0]["message"]["content"].strip())

    # When
    test_case = LLMTestCase(
        input=short_transcript,
        actual_output=output["summary"],
        expected_output="fragmented nature of the supply chain and existing monopolies",
        context=[short_transcript],
    )

    # Metric 1: Hallucination
    # uses vectara's hallucination evaluation model
    hallucination_metric = HallucinationMetric(threshold=0.99)

    # Metric 2: Insights
    insights_metric = GEval(
        name="insights",
        model=custom_deep_eval_model,
        threshold=0.5,
        evaluation_steps=[
            "Determine how entertaining the summary of the transcript is"
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )

    write_metric_scores(
        test_case=test_case,
        metrics=[hallucination_metric, insights_metric],
        write_dir=test_data_dir,
    )

    assert_test(test_case, [hallucination_metric, insights_metric])
