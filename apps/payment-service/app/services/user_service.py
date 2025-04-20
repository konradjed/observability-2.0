import requests
from fastapi import HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def fetch_user(user_id: str) -> dict:
    url = f"{settings.USER_SERVICE_BASE_URL}/users/{user_id}"
    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as e:
        logger.error("User service unreachable", exc_info=e)
        raise HTTPException(status_code=502, detail="User service unreachable")

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="User not found")

    return resp.json()