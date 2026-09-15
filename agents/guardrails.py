import re
from typing import Tuple
from opentelemetry import metrics

# Obtain OTel Meter
meter = metrics.get_meter("tradepulse.guardrails")

# Metrics
guardrail_eval_counter = meter.create_counter(
    name="tradepulse_guardrail_evaluations_total",
    description="Total number of guardrail evaluations executed",
    unit="1",
)

guardrail_violation_counter = meter.create_counter(
    name="tradepulse_guardrail_violations_total",
    description="Total number of guardrail violations by category",
    unit="1",
)

COMPLIANCE_DISCLAIMER = "\n\n*Disclaimer: Automated market analysis — not financial advice.*"
INJECTION_PATTERNS = [r"drop\s+table", r"select\s+\*", r"<script>", r"ignore\s+previous\s+instructions"]
PROHIBITED_FINANCIAL_TERMS = ["guaranteed return", "100% profit", "risk-free investment"]


def validate_input_ticker(symbol: str) -> Tuple[bool, str]:
    """Validates ticker format and checks for injection patterns."""
    if not symbol or not isinstance(symbol, str):
        guardrail_eval_counter.add(1, {"type": "input", "status": "fail"})
        guardrail_violation_counter.add(1, {"category": "empty_or_non_string"})
        return False, "Invalid ticker symbol format."

    clean_symbol = symbol.strip().upper()

    # Check prompt injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, clean_symbol, re.IGNORECASE):
            guardrail_eval_counter.add(1, {"type": "input", "status": "fail"})
            guardrail_violation_counter.add(1, {"category": "prompt_injection_attempt"})
            return False, "Input blocked: Prompt injection detected."

    # Validate ticker regex (1-5 alphanumeric chars)
    if not re.match(r"^[A-Z0-9]{1,5}$", clean_symbol):
        guardrail_eval_counter.add(1, {"type": "input", "status": "fail"})
        guardrail_violation_counter.add(1, {"category": "invalid_ticker_format"})
        return False, f"Invalid ticker format: '{symbol}'."

    guardrail_eval_counter.add(1, {"type": "input", "status": "pass"})
    return True, clean_symbol


def enforce_output_guardrails(analysis_text: str) -> str:
    """Sanitizes LLM outputs, flags unsanctioned financial claims, and appends disclaimers."""
    if not analysis_text:
        guardrail_eval_counter.add(1, {"type": "output", "status": "fail"})
        guardrail_violation_counter.add(1, {"category": "empty_llm_output"})
        return f"No analysis generated.{COMPLIANCE_DISCLAIMER}"

    sanitized_text = analysis_text.strip()

    # Check for prohibited financial promises
    for term in PROHIBITED_FINANCIAL_TERMS:
        if term in sanitized_text.lower():
            guardrail_eval_counter.add(1, {"type": "output", "status": "fail"})
            guardrail_violation_counter.add(1, {"category": "prohibited_financial_claims"})
            sanitized_text = re.sub(re.escape(term), "[REDACTED CLAIM]", sanitized_text, flags=re.IGNORECASE)

    # Check and append disclaimer
    if "not financial advice" not in sanitized_text.lower():
        guardrail_eval_counter.add(1, {"type": "output", "status": "fail"})
        guardrail_violation_counter.add(1, {"category": "missing_disclaimer"})
        sanitized_text += COMPLIANCE_DISCLAIMER
    else:
        guardrail_eval_counter.add(1, {"type": "output", "status": "pass"})

    return sanitized_text