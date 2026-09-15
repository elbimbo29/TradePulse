# telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

def setup_telemetry():
    """Configure OpenTelemetry Tracer Provider and console exporter."""
    resource = Resource.create(attributes={"service.name": "tradepulse-engine"})
    
    provider = TracerProvider(resource=resource)
    
    # BatchSpanProcessor efficiently queues and exports spans
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer("tradepulse.pipeline")