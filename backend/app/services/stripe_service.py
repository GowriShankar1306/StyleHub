import os

import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY is missing from .env")

stripe.api_key = STRIPE_SECRET_KEY


def create_payment_intent(
    amount_in_paise: int,
    order_id: int
):
    if amount_in_paise <= 0:
        raise ValueError("Payment amount must be greater than zero")

    payment_intent = stripe.PaymentIntent.create(
        amount=amount_in_paise,
        currency="inr",
        metadata={
            "order_id": str(order_id)
        },
        automatic_payment_methods={
            "enabled": True
        }
    )

    return payment_intent