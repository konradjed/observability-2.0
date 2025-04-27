import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource




def setup_otel_logging():
    # Create and set the logger provider
    logger_provider = LoggerProvider()
    set_logger_provider(logger_provider)

    # Create the OTLP log exporter that sends logs to configured destination
    exporter = OTLPLogExporter()
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    # Attach OTLP handler to root logger
    handler = LoggingHandler(logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)