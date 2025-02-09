import os
import json
from dotenv import load_dotenv
from app.configs.celery_config import celery
from app.configs.redis_config import redis_client
from openai import OpenAI, OpenAIError
from loguru import logger
from app.configs.log_config import setup_logger
from celery.exceptions import MaxRetriesExceededError

# Ensure logger is set up
setup_logger()
load_dotenv()
OPENAIKEY = os.getenv("OPENAI_API_KEY")

@celery.task(name="moderate_text_task", bind=True, max_retries=3, default_retry_delay=60)
def moderate_text_task(self, text: str):
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
    except OpenAIError as e:
        logger.error(f"OpenAIError in moderate_text_task: {str(e)}")
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for moderate_text_task")
            return {"error": "Service unavailable, please try again later."}
    except Exception as e:
        logger.error(f"Error in moderate_text_task: {str(e)}")
        return {"error": str(e)}