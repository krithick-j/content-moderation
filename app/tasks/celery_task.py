import os
import json
from dotenv import load_dotenv
from app.configs.celery_config import celery
from app.configs.redis_config import redis_client
from openai import OpenAI

load_dotenv()
OPENAIKEY = os.getenv("OPENAI_API_KEY")
@celery.task(name="moderate_text_task")
def moderate_text_task(text: str):
    """
    Background task for text moderation.
    """
    try:
        # Check if result is cached
        cached_result = redis_client.get(text)
        if cached_result:
            return json.loads(cached_result)
        # Call OpenAI Moderation API
        client = OpenAI(api_key=OPENAIKEY)
        response = client.moderations.create(model="omni-moderation-latest", input=text)
        result_data = response.results if hasattr(response, 'results') else {}
        print("result data", result_data)
        print("response", response)
        # Cache result for 1 hour
        redis_client.setex(text, 3600, json.dumps(response.results))

        return response.results
    except Exception as e:
        return {"error": str(e)}

