from fastapi import APIRouter
from app.models.item import Item
from app.utils.dynamodb_client import add_item, get_item
from app.utils.redis_client import set_item, get_item as get_item_cache
import json
from decimal import Decimal

router = APIRouter()

# Helper because json.dumps() doesnt support Decimal types by default
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

@router.post("/items/")
def create_item(item: Item):
    item_data = item.model_dump()

    # Save to DynamoDB
    add_item(item_data)

    # Cache item in Redis
    set_item(f"item:{item.id}", json.dumps(item_data, default=decimal_to_float))

    return item_data

@router.get("/items/{item_id}")
def read_item(item_id: int):
    # Check Redis Cache
    cached_item = get_item_cache(f"item:{item_id}")
    if cached_item:
        return json.loads(cached_item)
    
    # If not in cache, check DynamoDB
    item_data = get_item(item_id)
    if item_data:
        set_item(f"item:{item_id}", json.dumps(item_data, default=decimal_to_float))
        return item_data
    
    return {"error": "Item not found"}