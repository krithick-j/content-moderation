from fastapi import APIRouter, HTTPException, Request
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from app.tasks.celery_task import moderate_text_task
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()
moderation_router = APIRouter()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)


@moderation_router.post("/moderate/text")
@limiter.limit("5/minute")  # Limit to 5 requests per minute per IP
async def moderate_text(request: Request, content: dict):
    """
    Enqueue moderation task and return task ID.
    """
    try:
        text = content["text"]
        task = moderate_text_task.apply_async(args=[text])  # Run asynchronously
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