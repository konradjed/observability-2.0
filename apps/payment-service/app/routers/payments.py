from fastapi import APIRouter, HTTPException
from services.user_service import fetch_user
from services.payment_fee_service import fetch_fee
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/payments")
async def create_payment(payload: dict):
    user_id = payload.get("user_id")
    amount = payload.get("amount")

    if not user_id or amount is None:
        raise HTTPException(status_code=400, detail="user_id and amount are required")

    user = fetch_user(user_id)

    # calculate fee
    fee = fetch_fee(amount)

    logger.info("Processed payment", extra={"user_id": user_id, "amount": amount, "fee": fee})
    return {
            "status": "success",
            "user": user,
            "amount": amount,
            "fee": fee,
        }