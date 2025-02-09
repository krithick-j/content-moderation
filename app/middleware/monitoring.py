import time
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

# Import Prometheus metrics from monitoring module
from app.monitoring.prometheus import REQUEST_COUNT, REQUEST_LATENCY

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track request count and latency."""

    async def dispatch(self, request, call_next):
        method = request.method
        endpoint = request.url.path
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

        return response
