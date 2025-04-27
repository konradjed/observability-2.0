import logging
import os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from opentelemetry.trace import get_current_span

from app.config import settings
from app.logging_config import setup_logging
from app.otel_log_exporter import setup_otel_logging
from app.telemetry import init_tracer_provider, init_meter_provider, instrument_app
from app.services.payment_fee_service import fetch_fee
from app.services.user_service import fetch_user
# from app.routers import payments

# 1. JSON logging
setup_logging()
setup_otel_logging()
logger = logging.getLogger(settings.SERVICE_NAME)

# 2. Telemetry
init_tracer_provider()
init_meter_provider()

# 3. FastAPI app & instrumentation
app = Flask(__name__)
instrument_app(app)

# 4. Request / Response logging (inside the active span)
@app.before_request
def log_request():
    span = get_current_span()
    ctx  = span.get_span_context()
    tid  = f"{ctx.trace_id:032x}" if ctx.trace_id else "UNSET"
    sid  = f"{ctx.span_id:016x}"  if ctx.span_id  else "UNSET"
    logger.info("incoming request", extra={
        "service.name": settings.SERVICE_NAME,
        "method":       request.method,
        "path":         request.path,
        "trace.id":     tid,
        "span.id":      sid,
    })

@app.after_request
def log_response(response):
    span = get_current_span()
    ctx  = span.get_span_context()
    tid  = f"{ctx.trace_id:032x}" if ctx.trace_id else "UNSET"
    sid  = f"{ctx.span_id:016x}"  if ctx.span_id  else "UNSET"
    logger.info("outgoing response", extra={
        "service.name": settings.SERVICE_NAME,
        "method":       request.method,
        "path":         request.path,
        "status":       response.status_code,
        "trace.id":     tid,
        "span.id":      sid,
    })
    return response

# 5. Error handlers
# 2) Handle Flask/Werkzeug HTTP exceptions
@app.errorhandler(HTTPException)
def handle_http_error(e: HTTPException):
    # e.code is the status code; e.description is the message
    logging.getLogger(settings.SERVICE_NAME).error(
        "HTTPException",
        extra={"status_code": e.code, "error": e.description}
    )
    return jsonify(error=e.description), e.code

# 3) Catch-all for unexpected errors
@app.errorhandler(Exception)
def handle_unexpected_error(e):
    logging.getLogger(settings.SERVICE_NAME).exception("Unhandled exception")
    return jsonify(error="Internal server error"), 500

# 6. Payment endpoint
@app.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    amount  = data.get("amount")
    if not user_id or amount is None:
        abort(400, description="user_id and amount are required")

    user = fetch_user(user_id)
    fee  = fetch_fee(amount)

    logger.info("Processed payment", extra={
        "service.name": settings.SERVICE_NAME,
        "user_id":      user_id,
        "amount":       amount,
        "fee":          fee,
    })
    return jsonify(status="success", user=user, amount=amount, fee=fee)

if __name__ == "__main__":
    # allow `python -m app.main` or `flask run` to work
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))