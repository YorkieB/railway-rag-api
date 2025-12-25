"""
Cost Tracking Middleware

FastAPI middleware for tracking costs and adding cost headers to responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
import time

from .cost import CostTracker


class CostTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking costs and adding cost headers.
    
    Adds headers:
    - X-Cost-Tokens: Total tokens used
    - X-Cost-Dollars: Total cost in dollars
    - X-Budget-Warning: Warning message if at 80% threshold
    """
    
    def __init__(self, app: ASGIApp, cost_tracker: CostTracker):
        """
        Initialize cost tracking middleware.
        
        Args:
            app: ASGI application
            cost_tracker: CostTracker instance
        """
        super().__init__(app)
        self.cost_tracker = cost_tracker
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track costs.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response with cost headers
        """
        # Extract user_id from request (adjust based on your auth system)
        user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id") or "anonymous"
        
        # Get budget status before request
        budget_status = self.cost_tracker.get_budget_status(user_id)
        
        # Check if budget exceeded
        if budget_status["is_exceeded"]:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Daily budget limit reached",
                    "message": "Please try again tomorrow or contact support to increase your limit."
                }
            )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Extract cost info from response (if available)
        # This assumes the endpoint sets cost info in response state
        cost_info = getattr(request.state, "cost_info", {})
        
        # Add cost headers
        if cost_info:
            response.headers["X-Cost-Tokens"] = str(cost_info.get("text_tokens", 0))
            response.headers["X-Cost-Vision-Tokens"] = str(cost_info.get("vision_tokens", 0))
            response.headers["X-Cost-Audio-Minutes"] = str(cost_info.get("audio_minutes", 0))
            response.headers["X-Cost-Dollars"] = f"{cost_info.get('total_cost', 0):.4f}"
        
        # Add budget warning if needed
        if budget_status["should_warn"]:
            warnings = budget_status["warnings"]
            response.headers["X-Budget-Warning"] = "; ".join(warnings)
        
        # Add budget status headers
        response.headers["X-Budget-Text-Tokens-Remaining"] = str(budget_status["text_tokens"]["remaining"])
        response.headers["X-Budget-Dollars-Remaining"] = f"{budget_status['dollars']['remaining']:.2f}"
        
        return response

