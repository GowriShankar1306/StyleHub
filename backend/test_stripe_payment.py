
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key or not stripe.api_key.startswith("sk_test_"):
    raise RuntimeError(
        "Use a Stripe test-mode secret key in your backend .env"
    )

payment_intent_id = input(
    "Enter the FULL PaymentIntent ID (pi_...): "
).strip()

if not payment_intent_id.startswith("pi_"):
    raise ValueError("Enter a valid, complete PaymentIntent ID.")

# Retrieve the exact PaymentIntent.
intent = stripe.PaymentIntent.retrieve(payment_intent_id)

print("PaymentIntent ID:", intent.id)
print("Status before confirmation:", intent.status)
print("Amount (paise):", intent.amount)
print("Currency:", intent.currency)

if intent.status == "requires_payment_method":
    # Use Stripe's built-in test Visa payment method.
    intent = stripe.PaymentIntent.confirm(
        intent.id,
        payment_method="pm_card_visa",
        return_url="http://localhost:8000/payment/return",
    )
    
    print("Status after confirmation:", intent.status)

elif intent.status == "succeeded":
    print("Payment is already successful.")

else:
    print(
        "Payment needs another step. "
        "Do not create another order yet."
    )
