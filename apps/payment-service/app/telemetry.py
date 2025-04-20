import os
import time
import logging
from fastapi import FastAPI
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from app.config import settings
import logging

logger = logging.getLogger(__name__)

def init_tracer_provider():
    """Configure and return an OpenTelemetry TracerProvider."""
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: settings.SERVICE_NAME,
        ResourceAttributes.TELEMETRY_SDK_NAME: "python",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "local",
    })
    provider = TracerProvider(resource=resource)

    # Console exporter (for local/dev)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # OTLP exporter (if configured)
    if settings.OTEL_ENDPOINT:
        base = settings.OTEL_ENDPOINT.rstrip("/")
        full_endpoint = f"{base}/v1/traces"
        logger.info(f"Configuring OTLP HTTP exporter at {full_endpoint}")
        otlp_exporter = OTLPSpanExporter(endpoint=full_endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(provider)
    logger.info("OpenTelemetry tracer provider initialized")

# Initialize metrics
def init_meter_provider():
    if settings.OTEL_ENDPOINT:
        base = settings.OTEL_ENDPOINT.rstrip("/")
        metric_url = f"{base}/v1/metrics"
        logger.info(f"Configuring OTLP metric exporter at {metric_url}")
        metric_exporter = OTLPMetricExporter(endpoint=metric_url)
        metric_reader = PeriodicExportingMetricReader(metric_exporter)
        meter_provider = MeterProvider(metric_readers=[metric_reader], resource=Resource(attributes={SERVICE_NAME: settings.SERVICE_NAME}))
        metrics.set_meter_provider(meter_provider)
        logger.info("OpenTelemetry meter provider initialized")
    else:
        logger.warning("OTEL_ENDPOINT not set; metrics will not be exported")

# Instrument and record automatic metrics
def instrument_app(app: FastAPI):
    # Instrument for tracing
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    logger.info("FastAPI and requests instrumentation enabled")

    # Create a meter and instruments
    meter = metrics.get_meter(__name__)
    request_counter = meter.create_counter(
        name="http.server_requests",
        description="Count of HTTP requests",
    )
    request_histogram = meter.create_histogram(
        name="http.server_request_duration_ms",
        description="Duration of HTTP requests in milliseconds",
    )

    # Add ASGI middleware for metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start_ns = time.time_ns()
        response = await call_next(request)
        elapsed_ms = (time.time_ns() - start_ns) / 1_000_000

        labels = {
            "method": request.method,
            "path": request.url.path,
            "status_code": str(response.status_code)
        }
        request_counter.add(1, labels)
        request_histogram.record(elapsed_ms, labels)
        return response

    logger.info("Metrics middleware installed")