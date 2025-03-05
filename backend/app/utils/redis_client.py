import redis
import os
from app.config import settings

# Connect to remote Redis server
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def set_item(key: str, value: str):
    redis_client.set(key, value)

def get_item(key: str):
    return redis_client.get(key)