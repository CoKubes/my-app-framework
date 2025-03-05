from fastapi import APIRouter
from app.models.item import Item

router = APIRouter()

@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    sample_item = Item(
        id=item_id,
        name=f"Item {item_id}",
        description="A sample item description",
        price=19.99,
        in_stock=True
    )
    return sample_item

