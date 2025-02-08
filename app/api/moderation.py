import json
from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv
import redis

load_dotenv()

moderation_router = APIRouter()

# Mock OpenAI Moderation API URL
MODERATION_API_URL = "https://api.openai.com/v1/moderations"

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@moderation_router.post("/moderate/text")
async def moderate_text(content: dict):
    """
    Sends text to OpenAI's moderation API and returns the result.
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        text = content["text"]
        cached_result = redis_client.get(text)
        if cached_result:
            cached_result_json = json.loads(cached_result)
            return {"moderation_result": cached_result_json}
        
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )
        data = response.results
        redis_client.setex(text, 3600, json.dumps(data)) # Cache the result for 1 hour

        return {"moderation_result": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))