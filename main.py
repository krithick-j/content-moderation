from fastapi import FastAPI

app = FastAPI(title="Content Moderation API")

@app.get("/")
async def root():
    return {"message": "Content Moderation API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
