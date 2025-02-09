from fastapi import APIRouter, Depends, HTTPException, Request
from dotenv import load_dotenv
from app.configs.log_config import setup_logger
from app.schemas.moderation import ModerationRequest, ModerationResponse, ModerationResultResponse
from app.tasks.celery_task import moderate_text_task
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.moderation import ModerationResult
from sqlalchemy.orm import Session
from app.configs.db_config import get_db
from loguru import logger
from app.repo.moderation import save_moderation_result
setup_logger()
load_dotenv()
moderation_router = APIRouter()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)


@moderation_router.post("/moderate/text", response_model=ModerationResponse)
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def moderate_text(
    request: Request,  # Inject the Request object for rate limiting
    moderation_request: ModerationRequest,  # Validate the request body
    db: Session = Depends(get_db)
):
    """
    Enqueue moderation task and return task ID.
    """
    try:
        text = moderation_request.text
        logger.info(f"Received text for moderation: {text}")
        task = moderate_text_task.apply_async(args=[text])  # Run asynchronously
        
        # Store the task in the database
        moderation_result = ModerationResult(task_id=task.id, text=text, status="PENDING")
        save_moderation_result(moderation_result, db)
        logger.info(f"Task {task.id} enqueued for moderation")
        return ModerationResponse(task_id=task.id)
    except Exception as e:
        logger.error(f"Error while enqueuing moderation task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@moderation_router.get("/moderate/result/{task_id}", response_model=ModerationResultResponse)
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def get_moderation_result(request: Request, task_id: str):
    """
    Retrieve moderation result by task ID.
    """
    logger.info(f"Fetching result for task ID: {task_id}")
    task_result = moderate_text_task.AsyncResult(task_id)
    if task_result.state == "PENDING":
        logger.info(f"Task {task_id} is still pending")
        return ModerationResultResponse(task_id=task_id, result=task_result.result, status="PENDING")
    elif task_result.state == "SUCCESS":
        logger.info(f"Task {task_id} completed successfully")
        logger.info(f"Task result type: {type(task_result.result)}")
        return ModerationResultResponse(task_id=task_id, result=task_result.result, status="SUCCESS")
    else:
        logger.error(f"Task {task_id} failed with error: {str(task_result.info)}")
        return {"status": "failed", "error": str(task_result.info)}