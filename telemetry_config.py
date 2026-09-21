import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# OpenTelemetry Logging Imports
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider


def setup_telemetry(endpoint: str = "localhost:4317"):
    """Initializes OpenTelemetry tracing and logging exporters."""
    # 1. Setup Tracing
    tracer_provider = TracerProvider()
    span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    # 2. Setup OTel Logging Provider & OTLP Exporter
    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)

    log_exporter = OTLPLogExporter(endpoint=endpoint, insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # 3. Attach OTel Handler to standard Python root logger
    otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(otel_handler)

    # 4. Inject trace_id & span_id into logging formatters
    LoggingInstrumentor().instrument(set_logging_format=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] [trace_id=%(trace_id)s span_id=%(span_id)s] - %(message)s"
    )

    return trace.get_tracer("tradepulse_tracer")


if __name__ == "__main__":
    # Allows running telemetry_config.py standalone for testing
    tracer = setup_telemetry()
    logger = logging.getLogger("telemetry_test")
    with tracer.start_as_current_span("standalone_test_span"):
        logger.info("Telemetry successfully initialized standalone!")
    print("Telemetry initialization test complete.")