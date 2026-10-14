
from app.database import SessionLocal
from app.models.order_item import OrderItem
from app.models.product import Product

db = SessionLocal()

try:
    items = (
        db.query(OrderItem, Product.name)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == 2)
        .all()
    )

    for item, product_name in items:
        print(
            "Product:", product_name,
            "| Product ID:", item.product_id,
            "| Quantity:", item.quantity,
            "| Price:", item.price,
        )

finally:
    db.close()
