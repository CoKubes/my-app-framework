from fastapi import APIRouter
from app.models.item import Item
from app.utils.redis_client import set_item, get_item as get_item_cache
import json

router = APIRouter()

# Using in memory storage now; need to use a db later
items_db = {}

@router.post("/items/", response_model=Item)
def create_item(item: Item):
    item_data = item.model_dump()

    # Store in in-memory db
    items_db[item.id] = item_data

    # Cache item in Redis
    set_item(f"item:{item.id}", json.dumps(item_data))

    return item_data

@router.get("/items/{item_id}")
def read_item(item_id: int):
    # Check Redis Cache
    cached_item = get_item_cache(f"item:{item_id}")
    if cached_item:
        return json.loads(cached_item)
    
    # If not in cache, check in-memory store
    item_data = items_db.get(item_id)
    if item_data:
        set_item(f"item:{item_id}", json.dumps(item_data))
        return item_data
    
    return {"error": "Item not found"}