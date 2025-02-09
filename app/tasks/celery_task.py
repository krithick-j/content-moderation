import os
import json
from dotenv import load_dotenv
from app.configs.celery_config import celery
from app.configs.db_config import SessionLocal
from app.configs.redis_config import redis_client
from openai import OpenAI, OpenAIError
from loguru import logger
from app.configs.log_config import setup_logger
from celery.exceptions import MaxRetriesExceededError
from sqlalchemy.orm import Session
from app.models.moderation import ModerationResult
from app.repo.moderation import get_moderation_result_by_text


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
        db: Session = SessionLocal()
        
        # Update status to "PROCESSING"
        moderation_entry = get_moderation_result_by_text(text, db)
        if moderation_entry:
            moderation_entry.status = "PROCESSING"
            db.commit()
        # Check if result is cached
        cached_result = redis_client.get(text)
        if cached_result:
            logger.info("Cache hit for text")
            moderation_entry.status = "COMPLETED"
            moderation_entry.result = json.loads(cached_result)  # Save result to DB
            db.commit()
            return json.loads(cached_result)

        logger.info("Cache miss for text, calling OpenAI API")
        
        # Call OpenAI Moderation API
        client = OpenAI(api_key=OPENAIKEY)
        MODERATION_MODEL = os.getenv("MODERATION_MODEL")

        response = client.moderations.create(model=MODERATION_MODEL, input=text)
        response_json = response.to_json()
        # Cache result for 1 hour
        redis_client.setex(text, 3600, response_json)
        logger.info("Response cached for text")

        # Update status to "COMPLETED" and save result
        if moderation_entry:
            moderation_entry.status = "COMPLETED"
            moderation_entry.result = response_json  # Store API response
            db.commit()

        return response.results

    except OpenAIError as e:
        logger.error(f"OpenAIError in moderate_text_task: {str(e)}")
        if moderation_entry:
            moderation_entry.status = "FAILED"
            db.commit()
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            logger.error("Max retries exceeded for moderate_text_task")
            return {"error": "Service unavailable, please try again later."}
    except Exception as e:
        logger.error(f"Error in moderate_text_task: {str(e)}")
        if moderation_entry:
            moderation_entry.status = "FAILED"
            db.commit()
        return {"error": str(e)}
    finally:
        db.close()  # Close database session