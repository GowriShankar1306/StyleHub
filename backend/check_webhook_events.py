
from app.database import SessionLocal
from app.models.webhook_event import WebhookEvent

db = SessionLocal()

try:
    events = (
        db.query(WebhookEvent)
        .order_by(WebhookEvent.id.desc())
        .limit(10)
        .all()
    )

    for event in events:
        print(
            "Event ID:", event.stripe_event_id,
            "| Type:", event.event_type,
            "| Processed at:", event.processed_at,
        )

finally:
    db.close()
