from app.database import SessionLocal
from app.models.product import Product


products = [
    Product(
        name="Classic Cotton T-Shirt",
        description="Comfortable everyday cotton T-shirt",
        price=499.00,
        image_url="https://example.com/tshirt.jpg",
        stock=25
    ),
    Product(
        name="Slim Fit Jeans",
        description="Stylish slim-fit denim jeans",
        price=1299.00,
        image_url="https://example.com/jeans.jpg",
        stock=15
    ),
    Product(
        name="Casual Sneakers",
        description="Lightweight sneakers for daily wear",
        price=1999.00,
        image_url="https://example.com/sneakers.jpg",
        stock=10
    ),
    Product(
        name="Women's Summer Dress",
        description="Lightweight dress for casual outings",
        price=1499.00,
        image_url="https://example.com/dress.jpg",
        stock=12
    ),
    Product(
        name="Leather Wallet",
        description="Minimal everyday wallet",
        price=799.00,
        image_url="https://example.com/wallet.jpg",
        stock=20
    )
]


def seed_products():
    db = SessionLocal()

    try:
        existing_product = db.query(Product).first()

        if existing_product:
            print("Products already exist. Skipping insertion.")
            return

        db.add_all(products)
        db.commit()

        print("Sample products inserted successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_products()