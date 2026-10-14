from fastapi import FastAPI

from app.database import Base, engine
from app.models.user import User # class
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.webhook_event import WebhookEvent

from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.cart import router as cart_router
from app.routers.orders import router as orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StyleHub – Fashion Mini Store",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)

@app.get("/")
def root():
    return {
        "message": "StyleHub API is running"
    }