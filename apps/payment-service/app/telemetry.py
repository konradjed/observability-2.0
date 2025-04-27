# app/telemetry.py
import logging
import time
import psutil
from typing import Iterable
from flask import Flask, g, request
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import get_current_span
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
    get_meter_provider,
    set_meter_provider,
)

from app.config import settings

logger = logging.getLogger(__name__)

resource = Resource(attributes={
    ResourceAttributes.SERVICE_NAME: settings.SERVICE_NAME,
    ResourceAttributes.TELEMETRY_SDK_NAME: "python",
    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "local",
})

# Initialize tracing
def init_tracer_provider():
    """Configure and return an OpenTelemetry TracerProvider."""
    provider = TracerProvider(resource=resource)

    # Console exporter for traces (dev)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # OTLP HTTP exporter for traces
    if settings.OTEL_ENDPOINT:
        base = settings.OTEL_ENDPOINT.rstrip("/")
        trace_url = f"{base}/v1/traces"
        logger.info(f"Configuring OTLP trace exporter at {trace_url}")
        otlp_trace_exporter = OTLPSpanExporter(endpoint=trace_url)
        provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))

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
        meter_provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
        metrics.set_meter_provider(meter_provider)
        logger.info("OpenTelemetry meter provider initialized")
    else:
        logger.warning("OTEL_ENDPOINT not set; metrics will not be exported")

# Hook to log access inside the active span
def _access_log_hook(span, scope):
    uv_logger = logging.getLogger("uvicorn.access")
    client = scope.get("client")[0] if scope.get("client") else None
    method = scope.get("method")
    path = scope.get("path")
    status = span.status.status_code.name if span.status else "UNSET"
    ctx = span.get_span_context()
    trace_id = format(ctx.trace_id, "032x") if ctx.trace_id else "UNSET"
    span_id = format(ctx.span_id, "032x") if ctx.span_id else "UNSET"

    uv_logger.info(
        f"{client} - \"{method} {path}\" {status}",
        extra={"service.name": settings.SERVICE_NAME,
               "trace_id": trace_id,
               "span_id": span_id}
    )

# Instrument application and record metrics
def instrument_app(app: Flask):
    # 1) Trace all incoming Flask requests
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    logger.info("Flask and requests instrumentation enabled")

    # Create meter and instruments
    meter = metrics.get_meter(__name__)
    request_counter = meter.create_counter(
        name="http.server_requests",
        description="Count of HTTP requests",
    )
    request_histogram = meter.create_histogram(
        name="http.server_request_duration_ms",
        description="Duration of HTTP requests in milliseconds",
    )

    # Observable gauges for system metrics
    def cpu_usage_callback(options: CallbackOptions) -> Iterable[Observation]:
        usage = psutil.cpu_percent(interval=0.1)
        yield Observation(usage, {})

    def get_memory_usage(options: CallbackOptions) -> Iterable[Observation]:
        mem = psutil.virtual_memory()
        yield Observation(mem.percent, {})


    meter.create_observable_gauge(
        name="system.cpu.usage",
        description="CPU usage percentage",
        unit="percent",
        callbacks=[cpu_usage_callback],
    )
    meter.create_observable_gauge(
        name="system.memory.usage",
        description="Memory usage percentage",
        unit="By",
        callbacks=[get_memory_usage]
    )

    # Middleware for HTTP metrics
    @app.before_request
    def start_timer():
        # store start time in the request context
        g.start_ns = time.time_ns()

    @app.after_request
    def record_metrics(response):
        # compute elapsed ms
        elapsed_ms = (time.time_ns() - g.start_ns) / 1_000_000

        labels = {
            "method":      request.method,
            "path":        request.path,
            "status_code": str(response.status_code),
        }
        request_counter.add(1, labels)
        request_histogram.record(elapsed_ms, labels)
        return response

    logger.info("Metrics middleware installed")
