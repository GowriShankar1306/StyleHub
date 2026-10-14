
import hashlib
import hmac
import json
import os
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.order import Order
from app.models.webhook_event import WebhookEvent

load_dotenv()

WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
URL = "http://127.0.0.1:8000/orders/webhook"

if not WEBHOOK_SECRET or not WEBHOOK_SECRET.startswith("whsec_"):
    raise RuntimeError("Check STRIPE_WEBHOOK_SECRET in backend/.env")

db = SessionLocal()

try:
    
    order = (
        db.query(Order)
        .filter(Order.status == "paid")
        .order_by(Order.id.desc())
        .first()
    )

    if not order or not order.payment_intent_id:
        raise RuntimeError("No paid order with a PaymentIntent was found")

    
    event_record = (
        db.query(WebhookEvent)
        .filter(
            WebhookEvent.event_type == "payment_intent.succeeded"
        )
        .order_by(WebhookEvent.id.desc())
        .first()
    )

    if not event_record:
        raise RuntimeError("No successful webhook event was found")

    event_id = event_record.stripe_event_id
    payment_intent_id = order.payment_intent_id
    order_id = order.id

    print("Selected order:", order_id)
    print("Stored event ID:", event_id)
    print("PaymentIntent ID:", payment_intent_id)

    confirm = input(
        "Type REPLAY to simulate duplicate delivery: "
    ).strip()

    if confirm != "REPLAY":
        print("Test cancelled.")
        raise SystemExit(0)

    event = {
        "id": event_id,
        "object": "event",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": payment_intent_id,
                "object": "payment_intent",
                "metadata": {"order_id": str(order_id)},
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "type": "payment_intent.succeeded",
    }

    payload = json.dumps(
        event, separators=(",", ":")
    ).encode("utf-8")

    timestamp = int(time.time())
    signed_payload = str(timestamp).encode() + b"." + payload

    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    request = urllib.request.Request(
        URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Stripe-Signature": f"t={timestamp},v1={signature}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            print("HTTP status:", response.status)
            print("Response:", response.read().decode())
    except urllib.error.HTTPError as error:
        print("HTTP status:", error.code)
        print("Response:", error.read().decode())

finally:
    db.close()
