from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse
from app.services.auth import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post("/items", response_model=CartItemResponse,
             status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == item_data.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_data.product_id
    ).first()

    new_quantity = item_data.quantity

    if cart_item:
        new_quantity += cart_item.quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    if cart_item:
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product.id,
            quantity=new_quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.get("/items")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.product))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )

    items = []
    total_price = 0.0

    for item in cart_items:
        subtotal = item.product.price * item.quantity
        total_price += subtotal

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": round(subtotal, 2)
        })

    return {
        "items": items,
        "total_price": round(total_price, 2)
    }


@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = db.query(Product).filter(
        Product.id == cart_item.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Requested quantity exceeds available stock"
        )

    cart_item.quantity = item_data.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item


@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Cart item removed successfully"
    }