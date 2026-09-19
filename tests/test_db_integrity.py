import json
from pathlib import Path
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

# 1. Load JSON test data
DATA_PATH = Path(__file__).parent / "test_data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# 2. Define GEval metric for Output Completeness & Format Compliance
json_format_metric = GEval(
    name="JSON Structure and Persistence Criteria",
    criteria="Determine if the actual output is valid JSON, contains mandatory fields (ticker, sentiment, summary), and retains financial disclaimers.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    threshold=0.70,
)

# 3. Parametrize test suite
@pytest.mark.parametrize("scenario", scenarios, ids=[s["id"] for s in scenarios])
def test_database_persistence_and_eval(scenario):
    # A. Validate JSON payload parsing & Database Schema constraints
    output = scenario["actual_output"]
    
    # Optional check: If the output is expected to be a serialized database record
    if output.startswith("{") and output.endswith("}"):
        parsed_data = json.loads(output)
        
        # Check field existence (Database non-null constraints)
        assert "ticker" in parsed_data, "Database Integrity Error: 'ticker' field is missing."
        assert "sentiment" in parsed_data, "Database Integrity Error: 'sentiment' field is missing."
        assert parsed_data["sentiment"] in ["BULLISH", "BEARISH", "NEUTRAL"], "Database Enum Constraint Error."
        assert isinstance(parsed_data["confidence"], float), "Type Error: 'confidence' must be float."

    # B. Execute DeepEval metric evaluation
    test_case = LLMTestCase(
        input=scenario["input"],
        actual_output=scenario["actual_output"],
        retrieval_context=scenario["context"],
    )
    
    assert_test(test_case, [json_format_metric])