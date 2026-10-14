import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

load_dotenv()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

from decimal import Decimal, ROUND_HALF_UP

import stripe
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.cart import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.user import User
from app.models.webhook_event import WebhookEvent
from app.models.product import Product
from app.services.auth import get_current_user
from app.services.stripe_service import create_payment_intent


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    total = Decimal("0.00")

    for item in cart_items:
        if item.product is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A product in the cart no longer exists"
            )

        if item.quantity <= 0 or item.quantity > item.product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {item.product.name}"
            )

        unit_price = Decimal(str(item.product.price))
        total += unit_price * item.quantity

    total = total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    amount_in_paise = int(total * 100)

    if amount_in_paise <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order total must be greater than zero"
        )

    order = Order(
        user_id=current_user.id,
        total_amount=float(total),
        status="pending"
    )

    try:
        db.add(order)
        db.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.product.price)
            )
            db.add(order_item)

        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create order"
        )

    try:
        payment_intent = create_payment_intent(
            amount_in_paise=amount_in_paise,
            order_id=order.id
        )

    except (stripe.StripeError, ValueError):
        order.status = "payment_failed"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not initiate payment. Please try again."
        )

    order.payment_intent_id = payment_intent.id
    db.commit()

    return {
        "order_id": order.id,
        "total_amount": float(total),
        "currency": "inr",
        "payment_intent_id": payment_intent.id,
        "client_secret": payment_intent.client_secret,
        "status": order.status
    }




@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Stripe webhook secret is not configured",
        )

    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload or signature",
        )

    event_id = event["id"]
    event_type = event["type"]

    if event_type not in (
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
    ):
        return {"received": True, "ignored": True}

    payment_intent = event["data"]["object"].to_dict()
    payment_intent_id = payment_intent.get("id")
    metadata = payment_intent.get("metadata") or {}
    order_id = metadata.get("order_id")

    if not payment_intent_id or not order_id:
        return {"received": True, "ignored": True}

    try:
        order_id = int(order_id)
    except (TypeError, ValueError):
        return {"received": True, "ignored": True}

    try:
        existing_event = (
            db.query(WebhookEvent)
            .filter(WebhookEvent.stripe_event_id == event_id)
            .first()
        )

        if existing_event:
            return {"received": True, "duplicate": True}

        order = (
            db.query(Order)
            .filter(Order.id == order_id)
            .with_for_update()
            .first()
        )

        if not order or order.payment_intent_id != payment_intent_id:
            return {"received": True, "ignored": True}

        db.add(
            WebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
            )
        )

        if event_type == "payment_intent.succeeded":
            # Process inventory only the first time the order is paid.
            if order.status != "paid":
                order_items = (
                    db.query(OrderItem)
                    .filter(OrderItem.order_id == order.id)
                    .all()
                )

                # Validate every item before changing any stock.
                for item in order_items:
                    product = (
                        db.query(Product)
                        .filter(Product.id == item.product_id)
                        .first()
                    )

                    if product is None or product.stock < item.quantity:
                        raise HTTPException(
                            status_code=409,
                            detail=(
                                "Insufficient inventory for a paid order. "
                                "Manual reconciliation is required."
                            ),
                        )

                # Reduce stock after all items pass validation.
                for item in order_items:
                    product = (
                        db.query(Product)
                        .filter(Product.id == item.product_id)
                        .first()
                    )
                    product.stock -= item.quantity

                # Remove purchased items from this user's cart.
                for item in order_items:
                    cart_item = (
                        db.query(CartItem)
                        .filter(
                            CartItem.user_id == order.user_id,
                            CartItem.product_id == item.product_id,
                        )
                        .first()
                    )

                    if cart_item:
                        db.delete(cart_item)

                order.status = "paid"

        elif event_type == "payment_intent.payment_failed":
            if order.status != "paid":
                order.status = "payment_failed"

        db.commit()

    except IntegrityError:
        db.rollback()
        return {"received": True, "duplicate": True}

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not process webhook event",
        )

    return {"received": True}



@router.get("/my-orders")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

    return [
        {
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]
