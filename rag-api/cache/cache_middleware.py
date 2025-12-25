"""
Cache Middleware

Middleware for caching API responses.
"""

from typing import Callable, Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import hashlib
import json

from .redis_cache import get_cache


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching GET requests."""
    
    def __init__(self, app, cache_ttl: int = 300, excluded_paths: Optional[list] = None):
        """
        Initialize cache middleware.
        
        Args:
            app: FastAPI application
            cache_ttl: Cache TTL in seconds
            excluded_paths: Paths to exclude from caching
        """
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]
        self.cache = get_cache()
    
    def _make_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        # Include method, path, and query params
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching."""
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Skip excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Skip if cache not available
        if not self.cache:
            return await call_next(request)
        
        # Try to get from cache
        cache_key = self._make_cache_key(request)
        cached_response = self.cache.get(cache_key)
        
        if cached_response:
            # Return cached response
            return Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response.get("media_type", "application/json")
            )
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Cache response
            self.cache.set(
                cache_key,
                {
                    "content": body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type
                },
                ttl=self.cache_ttl
            )
            
            # Return response (need to recreate since body was consumed)
            return Response(
                content=body,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )
        
        return response

