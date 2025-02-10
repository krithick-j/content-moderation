from fastapi import FastAPI
from app.api.moderation import moderation_router, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.middleware.monitoring import PrometheusMiddleware
from app.monitoring.prometheus import metrics_router

app = FastAPI(title="Content Moderation API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(PrometheusMiddleware)


@app.get("/")
async def root():
    return {"message": "FastAPI with Prometheus Monitoring"}

app.include_router(moderation_router, prefix="/api/v1")
 
app.include_router(metrics_router)
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)