from fastapi import APIRouter, Depends, HTTPException, Request
from dotenv import load_dotenv
from app.tasks.celery_task import moderate_text_task
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.moderation import ModerationResult
from sqlalchemy.orm import Session
from app.configs.db_config import get_db

load_dotenv()
moderation_router = APIRouter()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)


@moderation_router.post("/moderate/text")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def moderate_text(request: Request, content: dict, db: Session = Depends(get_db)):
    """
    Enqueue moderation task and return task ID.
    """
    try:
        text = content["text"]
        task = moderate_text_task.apply_async(args=[text])  # Run asynchronously
        
        # Store the task in the database
        moderation_result = ModerationResult(task_id=task.id, text=text, status="PENDING")
        db.add(moderation_result)
        db.commit()
        db.refresh(moderation_result)
        
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@moderation_router.get("/moderate/result/{task_id}")
@limiter.limit("10/minute")  # Limit to 10 requests per minute per IP
async def get_moderation_result(request: Request, task_id: str):
    """
    Retrieve moderation result by task ID.
    """
    task_result = moderate_text_task.AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "processing"}
    elif task_result.state == "SUCCESS":
        return {"status": "completed", "moderation_result": task_result.result}
    else:
        return {"status": "failed", "error": str(task_result.info)}