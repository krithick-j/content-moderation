import os
import json
from dotenv import load_dotenv
from app.configs.celery_config import celery
from app.configs.redis_config import redis_client
from openai import OpenAI
from loguru import logger
from app.configs.log_config import setup_logger


# Ensure logger is set up
setup_logger()
load_dotenv()
OPENAIKEY = os.getenv("OPENAI_API_KEY")

@celery.task(name="moderate_text_task")
def moderate_text_task(text: str):
    """
    Background task for text moderation.
    """
    logger.info("Starting moderate_text_task")
    try:
        # Check if result is cached
        cached_result = redis_client.get(text)
        if cached_result:
            logger.info("Cache hit for text")
            return json.loads(cached_result)
        
        logger.info("Cache miss for text, calling OpenAI API")
        # Call OpenAI Moderation API
        client = OpenAI(api_key=OPENAIKEY)
        response = client.moderations.create(model="omni-moderation-latest", input=text)
        
        # Cache result for 1 hour
        redis_client.setex(text, 3600, response.to_json())
        logger.info("Response cached for text")

        return response.results
    except Exception as e:
        logger.error(f"Error in moderate_text_task: {str(e)}")
        return {"error": str(e)}