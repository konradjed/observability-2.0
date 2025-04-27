import logging
import ecs_logging
from pythonjsonlogger import jsonlogger
from opentelemetry.trace import get_current_span
from app.config import settings


# class FluentBitJsonFormatter(jsonlogger.JsonFormatter):
#     """
#     JSON Formatter for Elastic ECS compatibility:
#       - One JSON object per line
#       - Uses '@timestamp' for the timestamp
#       - Renames levelname → 'log.level', name → 'log.logger'
#       - Injects service.name, trace_id & span_id
#     """
#     def add_fields(self, log_record, record, message_dict):
#         super().add_fields(log_record, record, message_dict)
#
#         # 1) Timestamp → '@timestamp'
#         if "asctime" in log_record:
#             log_record["@timestamp"] = log_record.pop("asctime")
#
#         # 2) Log level → 'log.level'
#         if "levelname" in log_record:
#             log_record["log.level"] = log_record.pop("levelname")
#
#         # 3) Logger name → 'log.logger'
#         if "name" in log_record:
#             log_record["log.logger"] = log_record.pop("name")
#
#         # 4) Ensure service name under ECS field
#         log_record.setdefault("service.name", settings.SERVICE_NAME)
#
#         # 5) Inject trace/span IDs if available
#         span = get_current_span()
#         ctx  = span.get_span_context()
#         if ctx.trace_id and ctx.span_id:
#             log_record["trace.id"] = format(ctx.trace_id, "032x")
#             log_record["span.id"]  = format(ctx.span_id,  "016x")
#
# def setup_logging():
#     # Create a single JSON handler
#     handler = logging.StreamHandler()
#     fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
#     handler.setFormatter(FluentBitJsonFormatter(fmt))
#
#     # Root logger at INFO
#     root = logging.getLogger()
#     root.setLevel(logging.INFO)
#     root.handlers = [handler]
#
#     # Silence Werkzeug access logs at INFO (only JSON errors)
#     werk = logging.getLogger("werkzeug")
#     werk.setLevel(logging.ERROR)
#     werk.handlers = [handler]
#     werk.propagate = False


class ECSPlainFormatter(logging.Formatter):
    """
    Plain-text formatter with ECS-style key=value tokens for Elastic:
      - '@timestamp' from asctime
      - 'log.logger' and 'log.level'
      - 'service.name', 'trace.id', 'span.id'
      - The actual message at the end
    """
    default_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    default_msec_format = "%s.%03dZ"

    def format(self, record):
        # Capture the base log record values
        ts = self.formatTime(record, self.default_time_format)
        logger_name = record.name
        level = record.levelname

        # Inject ECS fields
        span = get_current_span()
        ctx  = span.get_span_context()
        trace_id = format(ctx.trace_id, "032x") if ctx.trace_id else "UNSET"
        span_id  = format(ctx.span_id,  "016x") if ctx.span_id  else "UNSET"

        # Build the key=value prefix
        prefix = (
            f"@timestamp={ts} "
            f"log.logger={logger_name} "
            f"log.level={level} "
            f"service.name={settings.SERVICE_NAME} "
            f"trace.id={trace_id} "
            f"span.id={span_id}"
        )

        # Original message
        message = super().format(record)

        # Combine prefix and message
        return f"{prefix} {message}"

def setup_logging():
    # Handler
    handler = logging.StreamHandler()
    # fmt = "%(asctime)s %(message)s"  # timestamp used only by Formatter.formatTime
    handler.setFormatter(ecs_logging.StdlibFormatter())

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]

    # Reduce Werkzeug noise, but still parse errors
    werk = logging.getLogger("werkzeug")
    werk.setLevel(logging.ERROR)
    werk.handlers = [handler]
    werk.propagate = False