from fastapi import APIRouter
from app.models.item import Item

router = APIRouter()

# Using in memory storage now; need to use a db later
items_db = []

@router.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    return {"error": "Item not found"}

@router.post("/items/", response_model=Item)
def create_item(item: Item):
    items_db.append(item)
    return item

