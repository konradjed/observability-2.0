import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import setup_logging
from app.telemetry import init_tracer_provider, instrument_app
from app.routers import payments

# 1. JSON logging
setup_logging(settings.SERVICE_NAME)
logger = logging.getLogger(settings.SERVICE_NAME)

# 2. Telemetry
init_tracer_provider()

# 3. FastAPI app & instrumentation
app = FastAPI()
instrument_app(app)

# 4. Middleware for auto‑logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("incoming request", extra={
        "method": request.method,
        "path": request.url.path
    })
    resp = await call_next(request)
    logger.info("outgoing response", extra={
        "method": request.method,
        "path": request.url.path,
        "status": resp.status_code
    })
    return resp

# 5. Error handlers
@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    logger.error("HTTPException", extra={
        "path": request.url.path, "detail": exc.detail
    })
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

@app.exception_handler(Exception)
async def exc_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", extra={"path": request.url.path})
    return JSONResponse({"error": "Internal server error"}, status_code=500)

# 6. Include routes
app.include_router(payments.router)