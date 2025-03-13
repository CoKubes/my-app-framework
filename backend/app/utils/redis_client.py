import redis
import os
from dotenv import load_dotenv
from app.config import settings
from aws_xray_sdk.core import xray_recorder

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL is not set")

# Connect to remote Redis server
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_item_cache(key: str, value: str):
    with xray_recorder.in_subsegment("Redis SetItem") as subsegment:
        subsegment.put_annotation("cache_key", key)
        redis_client.set(key, value)
        subsegment.put_metadata("cache_status", "SET")

def get_item_cache(key: str):
    with xray_recorder.in_subsegment("Redis GetItem") as subsegment:
        subsegment.put_annotation("cache_key", key)
        value = redis_client.get(key)

        if value:
            subsegment.put_metadata("cache_status", "HIT")
        else:
            subsegment.put_metadata("cache_status", "MISS")

        return value