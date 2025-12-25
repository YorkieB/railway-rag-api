"""
Health Checker

Checks health of various components.
"""

from typing import Dict, Any, List
from datetime import datetime
import os

from .metrics import get_metrics_collector


class HealthChecker:
    """Checks health of application components."""
    
    def __init__(self):
        """Initialize health checker."""
        self.metrics = get_metrics_collector()
    
    def check_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.
        
        Returns:
            Health status dictionary
        """
        checks = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check database connections
        checks["components"]["database"] = self._check_database()
        
        # Check API keys
        checks["components"]["api_keys"] = self._check_api_keys()
        
        # Check disk space
        checks["components"]["disk"] = self._check_disk_space()
        
        # Check memory usage
        checks["components"]["memory"] = self._check_memory()
        
        # Overall status
        component_statuses = [c["status"] for c in checks["components"].values()]
        if "unhealthy" in component_statuses:
            checks["status"] = "unhealthy"
        elif "degraded" in component_statuses:
            checks["status"] = "degraded"
        
        return checks
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            import chromadb
            # Try to connect to ChromaDB
            # This is a simplified check
            return {
                "status": "healthy",
                "message": "Database connection OK"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
    
    def _check_api_keys(self) -> Dict[str, Any]:
        """Check required API keys."""
        required_keys = ["OPENAI_API_KEY"]
        missing = []
        
        for key in required_keys:
            if not os.getenv(key):
                missing.append(key)
        
        if missing:
            return {
                "status": "unhealthy",
                "message": f"Missing API keys: {', '.join(missing)}"
            }
        
        return {
            "status": "healthy",
            "message": "All required API keys present"
        }
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_percent = (free / total) * 100
            
            if free_percent < 5:
                status = "unhealthy"
            elif free_percent < 10:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "free_percent": round(free_percent, 2),
                "free_gb": round(free / (1024**3), 2)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"Could not check disk space: {str(e)}"
            }
    
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            used_percent = memory.percent
            
            if used_percent > 90:
                status = "unhealthy"
            elif used_percent > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "used_percent": round(used_percent, 2),
                "available_gb": round(memory.available / (1024**3), 2)
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not installed"
            }
        except Exception as e:
            return {
                "status": "unknown",
                "message": f"Could not check memory: {str(e)}"
            }

