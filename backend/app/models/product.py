from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    stock = Column(Integer, default=0, nullable=False)