from fastapi import APIRouter, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
import redis

from app.tasks.celery_task import moderate_text_task

load_dotenv()

moderation_router = APIRouter()

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@moderation_router.post("/moderate/text")
async def moderate_text(content: dict):
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
async def get_moderation_result(task_id: str):
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