from fastapi import APIRouter, Depends, HTTPException, Request
from dotenv import load_dotenv
from app.configs.log_config import setup_logger
from app.schemas.moderation import ModerationRequest, ModerationResponse, ModerationResultResponse
from app.tasks.celery_task import moderate_text_task
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.moderation import ModerationResult
from app.configs.db_config import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from app.repo.moderation import save_moderation_result
from celery.result import AsyncResult
from app.repo.moderation import get_moderation_result_by_text, get_moderation_result_by_id
setup_logger()
load_dotenv()
moderation_router = APIRouter()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)


@moderation_router.post("/moderate/text")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def moderate_text(
    request: Request,  
    moderation_request: ModerationRequest,  
    db: AsyncSession = Depends(get_async_db)  # Use async session
):
    """
    Enqueue moderation task and return task ID.
    """
    try:
        text = moderation_request.text
        logger.info(f"Received text for moderation: {text}")

        mod_result: ModerationResult = await get_moderation_result_by_text(text, db)
        if mod_result:
            logger.info(f"Moderation result: {mod_result} found in database for text: {text}")
            return ModerationResponse(task_id=mod_result.task_id)
        
        # Run Celery task asynchronously
        task = moderate_text_task.delay(text)

        # Store the task in the database asynchronously
        moderation_result = ModerationResult(task_id=task.id, text=text, status=task.state)
        logger.info(f"Save moderation result for task {task.id} in database")
        await save_moderation_result(moderation_result, db)
        logger.info(f"Task {task.id} enqueued for moderation")
        return ModerationResponse(task_id=task.id)
    
    except Exception as e:
        logger.error(f"Error while enqueuing moderation task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@moderation_router.get("/moderate/result/{task_id}", response_model=ModerationResultResponse)
@limiter.limit("10/minute")  
async def get_moderation_result(request: Request, task_id: str):
    """
    Retrieve moderation result by task ID.
    """
    logger.info(f"Fetching result for task ID: {task_id}")
    
    try:
        task_result = AsyncResult(task_id)
        if not task_result:
            mod_result: ModerationResult = await get_moderation_result_by_id(task_id)
            if not mod_result:
                logger.error(f"Task {task_id} not found in database")
                return {"status": "failed", "error": "Task not found"}
            return ModerationResultResponse(task_id=task_id, result=mod_result.results, status=mod_result.status)
        logger.info(f"Task {task_result} is still pending")
        if task_result.state == "PENDING":
            logger.info(f"Task {task_id} is still pending")
            return ModerationResultResponse(task_id=task_id, result=None, status="PENDING")

        elif task_result.state == "SUCCESS":
            logger.info(f"Task {task_id} completed successfully")
            return ModerationResultResponse(task_id=task_id, result=task_result.result, status="SUCCESS")

        else:
            logger.error(f"Task {task_id} failed with error: {str(task_result.info)}")
            return {"status": "failed", "error": str(task_result.info)}

    except Exception as e:
        logger.error(f"Error fetching task result: {e}")
        raise HTTPException(status_code=500, detail=str(e))