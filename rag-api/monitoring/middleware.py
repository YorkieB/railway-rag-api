"""
Monitoring Middleware

Tracks requests, latency, and errors.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable

from .metrics import get_metrics_collector
from .logger import get_logger

logger = get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request monitoring."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track metrics."""
        metrics = get_metrics_collector()
        
        # Start timer
        start_time = time.time()
        
        # Track request
        metrics.increment("http_requests_total", tags={"method": request.method, "path": request.url.path})
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate latency
            latency = time.time() - start_time
            metrics.record("http_request_duration_seconds", latency, tags={
                "method": request.method,
                "path": request.url.path,
                "status": str(response.status_code)
            })
            
            # Track response status
            status_class = f"{response.status_code // 100}xx"
            metrics.increment("http_responses_total", tags={
                "method": request.method,
                "status": str(response.status_code),
                "status_class": status_class
            })
            
            return response
        
        except Exception as e:
            # Track errors
            latency = time.time() - start_time
            metrics.increment("http_errors_total", tags={
                "method": request.method,
                "path": request.url.path,
                "error_type": type(e).__name__
            })
            metrics.record("http_request_duration_seconds", latency, tags={
                "method": request.method,
                "path": request.url.path,
                "status": "500"
            })
            
            logger.error(f"Request failed: {request.method} {request.url.path}", extra={
                "extra_fields": {
                    "error": str(e),
                    "latency": latency
                }
            })
            
            raise

