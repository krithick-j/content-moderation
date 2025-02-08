from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

moderation_router = APIRouter()

# Mock OpenAI Moderation API URL
MODERATION_API_URL = "https://api.openai.com/v1/moderations"
 
@moderation_router.post("/moderate/text")
async def moderate_text(content: dict):
    """
    Sends text to OpenAI's moderation API and returns the result.
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=content["text"],
        )
        print(response)
        data = response.results
        return {"moderation_result": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))