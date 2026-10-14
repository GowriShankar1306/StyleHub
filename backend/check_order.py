
from app.database import SessionLocal
from app.models.order import Order

db = SessionLocal()

try:
    order = db.query(Order).filter(Order.id == 2).first()

    if order:
        print("Order ID:", order.id)
        print("Order status:", order.status)
        print("Total amount:", order.total_amount)
        print("PaymentIntent ID:", order.payment_intent_id)
    else:
        print("Order not found")

finally:
    db.close()
