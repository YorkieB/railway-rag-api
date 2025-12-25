"""
Rate Limiting

Provides rate limiting middleware and decorators.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute
            requests_per_hour: Max requests per hour
            requests_per_day: Max requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        
        # Store request timestamps per identifier (IP, user_id, etc.)
        self._minute_requests: Dict[str, list] = defaultdict(list)
        self._hour_requests: Dict[str, list] = defaultdict(list)
        self._day_requests: Dict[str, list] = defaultdict(list)
        
        self._lock = threading.Lock()
    
    def _get_identifier(self, request: Request, user_id: Optional[str] = None) -> str:
        """Get identifier for rate limiting (IP or user_id)."""
        if user_id:
            return f"user:{user_id}"
        
        # Use IP address
        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP if multiple
            client_host = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_host}"
    
    def _clean_old_requests(self, requests: list, window_seconds: int):
        """Remove requests outside the time window."""
        cutoff = time.time() - window_seconds
        return [ts for ts in requests if ts > cutoff]
    
    def is_allowed(
        self,
        identifier: str,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed.
        
        Args:
            identifier: Request identifier (IP or user_id)
            requests_per_minute: Override per-minute limit
            requests_per_hour: Override per-hour limit
            requests_per_day: Override per-day limit
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        with self._lock:
            now = time.time()
            
            # Clean old requests
            self._minute_requests[identifier] = self._clean_old_requests(
                self._minute_requests[identifier], 60
            )
            self._hour_requests[identifier] = self._clean_old_requests(
                self._hour_requests[identifier], 3600
            )
            self._day_requests[identifier] = self._clean_old_requests(
                self._day_requests[identifier], 86400
            )
            
            # Check limits
            minute_limit = requests_per_minute or self.requests_per_minute
            hour_limit = requests_per_hour or self.requests_per_hour
            day_limit = requests_per_day or self.requests_per_day
            
            if len(self._minute_requests[identifier]) >= minute_limit:
                return False, f"Rate limit exceeded: {minute_limit} requests per minute"
            
            if len(self._hour_requests[identifier]) >= hour_limit:
                return False, f"Rate limit exceeded: {hour_limit} requests per hour"
            
            if len(self._day_requests[identifier]) >= day_limit:
                return False, f"Rate limit exceeded: {day_limit} requests per day"
            
            # Record request
            self._minute_requests[identifier].append(now)
            self._hour_requests[identifier].append(now)
            self._day_requests[identifier].append(now)
            
            return True, None
    
    def check_rate_limit(
        self,
        request: Request,
        user_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Check rate limit and raise exception if exceeded.
        
        Args:
            request: FastAPI request
            user_id: Optional user ID
            **kwargs: Override limits
        
        Raises:
            HTTPException if rate limit exceeded
        """
        identifier = self._get_identifier(request, user_id)
        allowed, error = self.is_allowed(identifier, **kwargs)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error,
                headers={"Retry-After": "60"}
            )


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        if enabled:
            requests_per_minute = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
            requests_per_hour = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
            requests_per_day = int(os.getenv("RATE_LIMIT_REQUESTS_PER_DAY", "10000"))
            _rate_limiter = RateLimiter(
                requests_per_minute=requests_per_minute,
                requests_per_hour=requests_per_hour,
                requests_per_day=requests_per_day
            )
        else:
            # Create a no-op limiter
            _rate_limiter = RateLimiter(requests_per_minute=999999, requests_per_hour=999999, requests_per_day=999999)
    return _rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or get_rate_limiter()
        # Exclude paths from rate limiting
        self.excluded_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Try to get user_id from token if available
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from .auth import get_jwt_manager
                token = auth_header.split(" ")[1]
                token_data = get_jwt_manager().verify_token(token)
                user_id = token_data.user_id
            except:
                pass  # If token invalid, use IP-based limiting
        
        # Check rate limit
        self.rate_limiter.check_rate_limit(request, user_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        
        return response


def rate_limit_middleware(app, rate_limiter: Optional[RateLimiter] = None):
    """Create rate limit middleware."""
    return RateLimitMiddleware(app, rate_limiter)

