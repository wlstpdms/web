import json
import re
import secrets
from urllib.error import HTTPError, URLError
from urllib.request import Request as UrlRequest, urlopen

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routers.language import current_user
from app.core.config import settings
from app.db.database import get_db
from app.models.board import Board
from app.models.payment import ClothingOrder

router = APIRouter(prefix="/payments/clothing", tags=["clothing payments"])


def listing_price(contents: str) -> int:
    match = (
        re.search(r"판매가\s*[:：]?\s*([\d,]+)\s*원", contents)
        or re.search(r"가격\s*[:：]?\s*([\d,]+)\s*원", contents)
        or re.search(r"구매가\s*[:：]?\s*([\d,]+)\s*원", contents)
    )
    if not match:
        raise HTTPException(status_code=422, detail="This listing has no valid sale price")
    amount = int(match.group(1).replace(",", ""))
    if amount < 100 or amount > 10_000_000:
        raise HTTPException(status_code=422, detail="This listing price is outside the supported range")
    return amount


class CreateOrderRequest(BaseModel):
    board_idx: int = Field(gt=0)


class VerifyPaymentRequest(BaseModel):
    payment_id: str = Field(min_length=6, max_length=64)


@router.post("/orders")
def create_order(body: CreateOrderRequest, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    board = db.get(Board, body.board_idx)
    if board is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if db.scalar(select(ClothingOrder.id).where(
        ClothingOrder.board_idx == board.idx,
        ClothingOrder.status == "paid",
    )):
        raise HTTPException(status_code=409, detail="This product has already been purchased")
    if not settings.PORTONE_STORE_ID or not settings.PORTONE_CHANNEL_KEY:
        raise HTTPException(status_code=503, detail="PortOne Store ID and Toss Payments channel key are not configured")

    amount = listing_price(board.contents)
    payment_id = f"cloth-{board.idx}-{secrets.token_urlsafe(18)}"
    order = ClothingOrder(payment_id=payment_id, user_idx=user.idx, board_idx=board.idx, amount=amount)
    db.add(order)
    db.commit()
    return {
        "payment_id": payment_id,
        "order_name": board.title[:80],
        "amount": amount,
        "currency": "KRW",
        "store_id": settings.PORTONE_STORE_ID,
        "channel_key": settings.PORTONE_CHANNEL_KEY,
    }


@router.post("/verify")
def verify_payment(body: VerifyPaymentRequest, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    order = db.scalar(select(ClothingOrder).where(
        ClothingOrder.payment_id == body.payment_id,
        ClothingOrder.user_idx == user.idx,
    ))
    if order is None:
        raise HTTPException(status_code=404, detail="Payment order not found")
    if order.status == "paid":
        return {"status": "paid", "payment_id": order.payment_id}
    if not settings.PORTONE_API_SECRET:
        raise HTTPException(status_code=503, detail="PortOne V2 API secret is not configured on the server")

    api_request = UrlRequest(
        f"https://api.portone.io/payments/{body.payment_id}",
        headers={"Authorization": f"PortOne {settings.PORTONE_API_SECRET}", "Accept": "application/json"},
    )
    try:
        with urlopen(api_request, timeout=60) as response:
            payment = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Avoid returning provider response bodies, which can contain account details.
        raise HTTPException(status_code=502, detail="PortOne could not confirm this payment") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail="Could not reach PortOne to confirm payment") from exc

    received_amount = payment.get("amount")
    if isinstance(received_amount, dict):
        received_amount = received_amount.get("total")
    if (payment.get("status") != "PAID"
            or payment.get("paymentId") != order.payment_id
            or received_amount != order.amount
            or payment.get("currency") != "KRW"
            or (settings.PORTONE_STORE_ID and payment.get("storeId") != settings.PORTONE_STORE_ID)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment is not completed or does not match this order")

    order.status = "paid"
    db.commit()
    return {"status": "paid", "payment_id": order.payment_id}
