import redis
import os
from dotenv import load_dotenv
from app.config import settings

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise ValueError("REDIS_URL is not set")

# Connect to remote Redis server
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def set_item(key: str, value: str):
    redis_client.set(key, value)

def get_item(key: str):
    return redis_client.get(key)