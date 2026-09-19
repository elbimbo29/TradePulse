import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

# 1. Load JSON relative to this file's location
DATA_PATH = Path(__file__).parent / "test_data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# 2. Define evaluation metric using LLMTestCaseParams
sentiment_metric = GEval(
    name="Sentiment Accuracy",
    criteria="Determine if the actual output captures the sentiment of the input accurately.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.70,
)

# 3. Parametrize individual tests dynamically
@pytest.mark.parametrize("scenario", scenarios, ids=[s["id"] for s in scenarios])
def test_sentiment_evaluation(scenario):
    test_case = LLMTestCase(
        input=scenario["input"],
        actual_output=scenario["actual_output"],
        retrieval_context=scenario["context"],
    )
    
    assert_test(test_case, [sentiment_metric])