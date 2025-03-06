from fastapi import APIRouter, HTTPException
from app.models.item import Item
from app.utils.dynamodb_client import add_item, get_item, update_item
from app.utils.redis_client import set_item, get_item as get_item_cache
from app.utils.logger import logger
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
    logger.info(f"Received new item: {item_data}")

    # Save to DynamoDB
    add_item(item_data)

    # Cache item in Redis
    set_item(f"item:{item.id}", json.dumps(item_data, default=decimal_to_float))

    logger.info(f"Item stored in DynamoDB and cached: {item.id}")
    return item_data

@router.get("/items/{item_id}")
def read_item(item_id: int):
    logger.info(f"Fetching item: {item_id}")

    # Check Redis Cache
    cached_item = get_item_cache(f"item:{item_id}")
    if cached_item:
        logger.info(f"Item {item_id} found in cache")
        return json.loads(cached_item)
    
    # If not in cache, check DynamoDB
    item_data = get_item(item_id)
    if item_data:
        set_item(f"Item:{item_id}", json.dumps(item_data, default=decimal_to_float))
        logger.info(f"Item {item_id} fetched from DynamoDB and cached")
        return item_data
    
    logger.warning(f"Item {item_id} not found")
    return {"error": "Item not found"}

@router.put("/items/{item_id}")
def update_existing_item(item_id: int, updated_item: Item):
    logger.info(f"Updating item: {item_id}")

    existing_item = get_item(item_id)
    if not existing_item:
        logger.warning(f"Item {item_id} not found in DynamoDB")
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Convert Pydantic model to dictionary
    updated_data = updated_item.model_dump()

    update_item(item_id, updated_data)

    set_item(f"item:{item_id}", json.dumps(updated_data, default=decimal_to_float))

    logger.info(f"Item {item_id} updated successfully")
    return {"message": "Item updated successfully", "item": updated_data}