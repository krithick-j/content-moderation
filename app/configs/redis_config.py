import redis
from dotenv import load_dotenv
import os

load_dotenv()


# Set up Redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True  # Ensures responses are returned as strings instead of bytes
)
