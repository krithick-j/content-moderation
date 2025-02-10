import os
from dotenv import load_dotenv
from app.configs.celery_config import celery
from openai import OpenAI, OpenAIError
from loguru import logger
from app.configs.log_config import setup_logger
from app.repo.moderation import update_moderation_result

# Ensure logger is set up
load_dotenv()
setup_logger()

OPENAIKEY = os.getenv("OPENAI_API_KEY")
MODERATION_MODEL = os.getenv("MODERATION_MODEL")

@celery.task(name="moderate_text_task", bind=True, max_retries=3, default_retry_delay=60)
def moderate_text_task(self, text: str):
    """
    Background task for text moderation.
    """
    logger.info("Starting moderate_text_task")

    try:
        logger.info("calling OpenAI API")

        # Call OpenAI Moderation API
        client = OpenAI(api_key=OPENAIKEY)
        response = client.moderations.create(model=MODERATION_MODEL, input=text)
        response_json = response.to_dict()

        # Store the result in PostgreSQL
        update_moderation_result(self.request.id, response_json, "SUCCESS")

        return response_json

    except OpenAIError as e:
        logger.error(f"OpenAIError in moderate_text_task: {str(e)}")
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for moderate_text_task")
            update_moderation_result(self.request.id, text, None, "FAILED")
            return {"error": "Service unavailable, please try again later."}

    except Exception as e:
        logger.error(f"Error in moderate_text_task: {str(e)}")
        update_moderation_result(self.request.id, None, "FAILED")
        return {"error": str(e)}