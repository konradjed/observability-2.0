import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    USER_SERVICE_BASE_URL: str = os.getenv("USER_SERVICE_BASE_URL", "http://localhost:8001")
    FEE_SERVICE_BASE_URL: str = os.getenv("FEE_SERVICE_BASE_URL", "http://localhost:8080")
    OTEL_ENDPOINT: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "payment-service")

settings = Settings()