
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key or not stripe.api_key.startswith("sk_test_"):
    raise RuntimeError("A Stripe test secret key (sk_test_...) is required.")

payment_intent_id = input("Enter the PaymentIntent ID for Order 3: ").strip()

if not payment_intent_id.startswith("pi_"):
    raise ValueError("Enter a valid PaymentIntent ID.")

intent = stripe.PaymentIntent.retrieve(payment_intent_id)

print("Current status:", intent.status)

if intent.status != "requires_payment_method":
    raise RuntimeError(
        f"Expected requires_payment_method, got {intent.status}. "
        "Stop and check the PaymentIntent before continuing."
    )

failed_intent = stripe.PaymentIntent.confirm(
    intent.id,
    payment_method="pm_card_chargeDeclined",
    return_url="http://localhost:8000/payment/return",
)

print("PaymentIntent status:", failed_intent.status)
