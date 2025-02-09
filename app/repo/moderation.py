from loguru import logger
from sqlalchemy.orm import Session

from app.configs.log_config import setup_logger
from app.models.moderation import ModerationResult

setup_logger()

def save_moderation_result(moderation_result: ModerationResult, db: Session):
    """
    Save the moderation result to the database.

    :param moderation_result: The moderation result object to save.
    :param db: The database session to use for saving the result.
    :return: The saved moderation result object.
    :raises Exception: If an error occurs while saving the moderation result.
    """
    
    try:
        db.add(moderation_result)
        db.commit()
        db.refresh(moderation_result)
        logger.info(f"Moderation result saved successfully")
        return moderation_result
    except Exception as e:
        logger.error(f"An error occurred while saving the moderation result: {e}")
        
def get_moderation_result_by_text(text: str, db: Session) -> ModerationResult:
    """
    Retrieve a moderation result from the database by text.

    :param text: The text to filter the moderation result by.
    :param db: The database session to use for querying the result.
    :return: The moderation result object if found, else None.
    """
    
    try:
        result = db.query(ModerationResult).filter_by(text=text).first()
        if result:
            logger.info(f"Moderation result retrieved successfully for text: {text}")
        else:
            logger.info(f"No moderation result found for text: {text}")
        return result
    except Exception as e:
        logger.error(f"An error occurred while retrieving the moderation result: {e}")
        return None