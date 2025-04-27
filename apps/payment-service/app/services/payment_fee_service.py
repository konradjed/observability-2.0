import logging
import requests
from flask import abort
from app.config import settings

logger = logging.getLogger(__name__)

def fetch_fee(amount: float) -> float:
    base = settings.FEE_SERVICE_BASE_URL.rstrip("/")
    url = f"{base}/api/fee-calculator/fee"
    logger.info("Calculating fee", extra={"url": url, "amount": amount})

    try:
        resp = requests.post(url, json={"amount": amount}, timeout=5)
    except requests.RequestException as exc:
        logger.error("Fee service unreachable", exc_info=exc)
        abort(502, description="Fee service unreachable")

    if resp.status_code != 200:
        logger.info("Fee service returned non-200", extra={
            "status_code": resp.status_code, "body": resp.text
        })
        abort(resp.status_code, description=resp.text or "Fee service error")

    body = resp.json()
    fee = body.get("fee")
    if fee is None:
        logger.error("Fee service returned unexpected payload", extra={"body": body})
        abort(502, description="Invalid fee service response")

    logger.info("Received fee from service", extra={"amount": amount, "fee": fee})
    return fee