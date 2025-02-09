from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.moderation import moderation_router, limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address

app = FastAPI(title="Content Moderation API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
async def root():
    return {"message": "Content Moderation API is running"}

app.include_router(moderation_router, prefix="/api/v1")
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)