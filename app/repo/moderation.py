import json
from loguru import logger
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession 
from app.configs.db_config import SessionLocal, get_async_db
from sqlalchemy.orm import Session
from app.configs.log_config import setup_logger
from app.models.moderation import ModerationResult
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.configs.redis_config import redis_client
setup_logger()

async def save_moderation_result(moderation_result: ModerationResult, db: AsyncSession) -> ModerationResult:
    """
    Save the moderation result to the database.

    :param moderation_result: The moderation result object to save.
    :param db: The database session to use for saving the result.
    :return: The saved moderation result object.
    :raises Exception: If an error occurs while saving the moderation result.
    """
      
    try:
        logger.info("Moderation result saving...")
        db.add(moderation_result)
        await db.commit()
        await db.refresh(moderation_result)
        logger.info("Moderation result saved successfully")
        return moderation_result
    except Exception as e:
        logger.error(f"An error occurred while saving the moderation result: {e}")
        raise

async def get_moderation_result_by_text(text: str, db: AsyncSession) -> ModerationResult:
    """
    Retrieve a moderation result from the database by text.

    :param text: The text to filter the moderation result by.
    :param db: The database session to use for querying the result.
    :return: The moderation result object if found, else None.
    """
    
    try:
        result = await db.execute(select(ModerationResult).filter(ModerationResult.text == text))
        moderation_result = result.scalars().first()  # Extract the actual record
        
        if moderation_result:
            logger.info(f"Moderation result: {moderation_result.task_id} retrieved successfully for text: {text}")
        else:
            logger.info(f"No moderation result found for text: {text}")
        
        return moderation_result
    except Exception as e:
        logger.error(f"An error occurred while retrieving the moderation result: {e}")
        return None
    
async def get_moderation_result_by_id(id: int, db: AsyncSession) -> ModerationResult:
    """
    Retrieve a moderation result from the database by text.

    :param text: The text to filter the moderation result by.
    :param db: The database session to use for querying the result.
    :return: The moderation result object if found, else None.
    """
    
    try:
        result = await db.execute(select(ModerationResult).filter(ModerationResult.id == id))
        moderation_result = result.scalars().first()  # Extract the actual record
        
        if moderation_result:
            logger.info(f"Moderation result: {moderation_result.task_id} retrieved successfully for text: {id}")
        else:
            logger.info(f"No moderation result found for text: {id}")
        
        return moderation_result
    except Exception as e:
        logger.error(f"An error occurred while retrieving the moderation result: {e}")
        return None
    
### **2. Function to Store Result in PostgreSQL**
#This function will be responsible for saving the Celery task result in PostgreSQL.

def update_moderation_result(task_id: str, new_result: dict, status: str = "COMPLETED"):
    """
    Updates the results column in the moderation_results table using task_id.

    :param db: Session - SQLAlchemy sync session
    :param task_id: str - The task ID to identify the record
    :param new_result: dict - The new moderation result to be stored
    :param status: str - The updated status (default: "COMPLETED")
    :return: bool - True if update was successful, False otherwise
    """
    try:
        # Convert result dictionary to JSON string
        new_result_json = json.dumps(new_result)
        logger.info(f"Moderation result: {new_result_json} saving...")
        # Update query
        stmt = (
            update(ModerationResult)
            .where(ModerationResult.task_id == task_id)
            .values(results=new_result_json, status=status)
        )
        db: Session = SessionLocal()
        # Execute the update statement
        db.execute(stmt)
        db.commit()  # Commit the transaction
        logger.info(f"Moderation result: {new_result_json} saved successfully")

        return True
    except Exception as e:
        db.rollback()  # Rollback in case of error
        return False