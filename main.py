from fastapi import FastAPI
from app.api.moderation import moderation_router
app = FastAPI(title="Content Moderation API")

@app.get("/")
async def root():
    return {"message": "Content Moderation API is running"}

app.include_router(moderation_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)