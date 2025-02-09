from fastapi import FastAPI
from loguru import logger
from app.api.moderation import moderation_router, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.configs.db_config import Base, engine
# from slowapi.util import get_remote_address
logger.info("Creating all tables in the database")
Base.metadata.create_all(engine)


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