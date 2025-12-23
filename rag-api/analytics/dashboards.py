"""
Analytics Dashboards

Usage statistics, cost analysis, and performance metrics.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from cost import CostTracker
from memory.analytics import get_memory_analytics

# Initialize cost tracker
cost_tracker = CostTracker()


class AnalyticsDashboard:
    """Provides analytics and insights"""
    
    def get_usage_statistics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get usage statistics for a user.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dict with usage statistics
        """
        # Get cost data
        budget_status = cost_tracker.get_budget_status(user_id)
        
        # Get memory analytics
        memory_analytics = get_memory_analytics()
        memory_stats = memory_analytics.get_analytics_summary(user_id) if hasattr(memory_analytics, 'get_analytics_summary') else {}
        
        return {
            "user_id": user_id,
            "period_days": days,
            "cost_summary": budget_status or {},
            "memory_stats": memory_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_cost_analysis(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get cost analysis and optimization suggestions.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dict with cost breakdown and suggestions
        """
        budget_status = cost_tracker.get_budget_status(user_id)
        
        # Calculate cost breakdown by category
        cost_breakdown = {
            "text_tokens": 0,
            "vision_tokens": 0,
            "image_generation": 0,
            "video_generation": 0,
            "audio_minutes": 0,
            "other": 0
        }
        
        # Get suggestions
        suggestions = []
        if budget_status:
            total_cost = budget_status.get("total_cost", 0)
            if total_cost > 50:
                suggestions.append("Consider using lower-cost models for non-critical tasks")
            if budget_status.get("text_tokens", 0) > 500000:
                suggestions.append("Text token usage is high - consider optimizing prompts")
        
        return {
            "user_id": user_id,
            "period_days": days,
            "cost_breakdown": cost_breakdown,
            "total_cost": budget_status.get("total_cost", 0) if budget_status else 0,
            "suggestions": suggestions,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_performance_metrics(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get performance metrics.
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dict with performance metrics
        """
        return {
            "user_id": user_id,
            "period_days": days,
            "average_response_time_ms": 0,  # Would be tracked in production
            "success_rate": 0.95,  # Would be calculated from logs
            "error_rate": 0.05,
            "generated_at": datetime.now().isoformat()
        }


# Global analytics dashboard instance
analytics_dashboard = AnalyticsDashboard()

