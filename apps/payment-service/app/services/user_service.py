import requests
from flask import abort
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def fetch_user(user_id: str) -> dict:
    url = f"{settings.USER_SERVICE_BASE_URL}/users/{user_id}"
    logger.info("Fetching user data", extra={"url": url})

    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as e:
        logger.error("User service unreachable", exc_info=e)
        # 502 Bad Gateway
        abort(502, description="User service unreachable")

    if resp.status_code != 200:
        logger.info("User service returned non-200", extra={
            "status_code": resp.status_code, "body": resp.text
        })
        abort(resp.status_code, description="User not found")

    user = resp.json()
    logger.info("Fetched user successfully", extra={"user_id": user_id})
    return user