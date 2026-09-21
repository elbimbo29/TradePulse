import time
import json
import structlog
from tenacity import retry, stop_after_attempt, wait_fixed
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
import logging
from telemetry_config import setup_telemetry  # Import from the saved file

# Initialize OTel Traces + Logs before tests start
setup_telemetry()

logger = logging.getLogger(__name__)

def test_example_scenario():
    logger.info("Executing test scenario with trace context...")
    
# 1. Setup Structlog JSON Logger
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# 2. Setup OpenTelemetry Tracing
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("tradepulse-test-runner")

# 3. Setup OpenTelemetry Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("tradepulse-metrics")

# Define Prometheus / OTel Gauges & Counters
test_counter = meter.create_counter(
    "deepeval_test_executions_total",
    description="Total count of DeepEval test executions"
)
confidence_histogram = meter.create_histogram(
    "deepeval_model_confidence_score",
    description="Distribution of model confidence scores"
)

# 4. Helper Function with Tenacity Retry
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def simulate_llm_inference(scenario_name, should_fail=False):
    if should_fail:
        logger.error("llm_inference_failed", scenario=scenario_name, reason="Rate limit / Timeout")
        raise ConnectionError("Simulated LLM API Timeout")
    return {"sentiment": "BULLISH", "confidence": 0.94, "ticker": "TSLA"}

# 5. Execute Test Suite Pipeline
def run_suite():
    scenarios = [
        {"name": "bullish_scenario", "fail": False, "conf": 0.94, "sentiment": "BULLISH"},
        {"name": "bearish_scenario", "fail": False, "conf": 0.88, "sentiment": "BEARISH"},
        {"name": "database_persistence_scenario", "fail": False, "conf": 0.91, "sentiment": "NEUTRAL"},
        {"name": "retry_resilience_scenario", "fail": True, "conf": 0.0, "sentiment": "UNKNOWN"} # Triggers Tenacity retries
    ]

    for sc in scenarios:
        with tracer.start_as_current_span(f"pytest_scenario_{sc['name']}") as span:
            span.set_attribute("pytest.scenario_name", sc["name"])
            logger.info("test_scenario_started", scenario=sc["name"])

            try:
                # Test LLM Call with Retry logic
                result = simulate_llm_inference(sc["name"], should_fail=sc["fail"])
                
                # Record DeepEval & Guardrails outcomes
                span.set_attribute("guardrails.status", "PASSED")
                span.set_attribute("deepeval.confidence", sc["conf"])
                span.set_attribute("deepeval.status", "PASSED")

                # Metrics recording
                test_counter.add(1, {"status": "PASSED", "scenario": sc["name"]})
                confidence_histogram.record(sc["conf"], {"scenario": sc["name"]})

                logger.info("test_scenario_passed", scenario=sc["name"], confidence=sc["conf"])

            except Exception as e:
                span.set_attribute("guardrails.status", "FAILED")
                span.set_attribute("deepeval.status", "FAILED")
                test_counter.add(1, {"status": "FAILED", "scenario": sc["name"]})

                logger.error("test_scenario_failed", scenario=sc["name"], error=str(e))

if __name__ == "__main__":
    print("🚀 Running instrumented test suite...")
    run_suite()
    print("✅ Test run completed! Telemetry dispatched to OTEL Collector.")
    time.sleep(3) # Allow background metrics/spans to flush