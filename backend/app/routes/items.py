from fastapi import APIRouter, HTTPException
from app.models.item import Item
from app.utils.dynamodb_client import add_item, get_item, update_item, delete_item_from_db
from app.utils.redis_client import redis_client, set_item_cache, get_item_cache 
from app.utils.logger import log_event
from app.utils.metric import send_cloudwatch_metric
import json
from decimal import Decimal
from aws_xray_sdk.core import xray_recorder

router = APIRouter()

# Helper because json.dumps() doesnt support Decimal types by default
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

@router.post("/items/")
async def create_item(item: Item):
    send_cloudwatch_metric("TotalRequests")  # Track total API requests
    item_data = item.model_dump()
    log_event("info", f"Received new item: {item_data}")

    try:
        add_item(item_data)
        set_item_cache(f"item:{item.id}", json.dumps(item_data, default=decimal_to_float))
        log_event("info", f"Item stored in DynamoDB and cached: {item.id}")
        return item_data
    except Exception as e:
        send_cloudwatch_metric("FailedRequests")  # Track failed requests
        log_event("error", f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/items/{item_id}")
async def read_item(item_id: int):
    send_cloudwatch_metric("TotalRequests")
    log_event("info", f"Fetching item: {item_id}")

    cached_item = get_item_cache(f"item:{item_id}")
    if cached_item:
        send_cloudwatch_metric("CacheHits")  # Track cache hits
        log_event("info", f"Item {item_id} found in cache")
        return json.loads(cached_item)
    
    item_data = get_item(item_id)
    if item_data:
        set_item_cache(f"item:{item_id}", json.dumps(item_data, default=decimal_to_float))
        send_cloudwatch_metric("CacheMisses")  # Track cache misses
        log_event("info", f"Item {item_id} fetched from DynamoDB and cached")
        return item_data

    send_cloudwatch_metric("FailedRequests")
    log_event("warning", f"Item {item_id} not found")
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/items/{item_id}")
async def update_existing_item(item_id: int, updated_item: Item):
    send_cloudwatch_metric("TotalRequests")
    log_event("info", f"Updating item: {item_id}")

    existing_item = get_item(item_id)
    if not existing_item:
        send_cloudwatch_metric("FailedRequests")
        log_event("warning", f"Item {item_id} not found in DynamoDB")
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_data = updated_item.model_dump()

    if "id" in updated_data:
        del updated_data["id"]

    update_item(item_id, updated_data)
    set_item_cache(f"item:{item_id}", json.dumps(updated_data, default=decimal_to_float))

    log_event("info", f"Item {item_id} updated successfully")
    return {"message": "Item updated successfully", "item": updated_data}

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    send_cloudwatch_metric("TotalRequests")
    log_event("info", f"Deleting item: {item_id}")

    existing_item = get_item(item_id)
    if not existing_item:
        send_cloudwatch_metric("FailedRequests")
        log_event("warning", f"Item {item_id} not found in DynamoDB")
        raise HTTPException(status_code=404, detail="Item not found")

    delete_item_from_db(item_id)
    redis_client.delete(f"item:{item_id}")

    log_event("info", f"Item {item_id} deleted successfully")
    return {"message": "Item deleted successfully"}