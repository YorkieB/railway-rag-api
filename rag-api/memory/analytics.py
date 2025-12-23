"""
Memory Analytics
Tracks usage patterns, effectiveness metrics, and search frequency.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading


class MemoryAnalytics:
    """
    Tracks memory usage and effectiveness.
    
    Metrics:
    - Usage patterns (when memories are accessed)
    - Memory effectiveness (how often memories are used in answers)
    - Search frequency (how often memories are retrieved)
    - Memory age and relevance
    """
    
    def __init__(self):
        """Initialize analytics tracker."""
        self.access_log: List[Dict] = []  # Memory access events
        self.usage_counts: Dict[str, int] = defaultdict(int)  # memory_id -> access count
        self.search_log: List[Dict] = []  # Search events
        self.effectiveness_scores: Dict[str, float] = {}  # memory_id -> effectiveness score
        self.lock = threading.Lock()
    
    def log_access(
        self,
        memory_id: str,
        access_type: str,  # "retrieved", "used_in_answer", "updated", "deleted"
        context: Optional[Dict] = None
    ):
        """
        Log memory access event.
        
        Args:
            memory_id: Memory ID
            access_type: Type of access
            context: Optional context information
        """
        with self.lock:
            event = {
                "memory_id": memory_id,
                "access_type": access_type,
                "timestamp": datetime.now().isoformat(),
                "context": context or {}
            }
            self.access_log.append(event)
            self.usage_counts[memory_id] += 1
    
    def log_search(
        self,
        query: str,
        retrieved_memories: List[str],
        used_in_answer: List[str],
        user_id: Optional[str] = None
    ):
        """
        Log search event.
        
        Args:
            query: Search query
            retrieved_memories: List of memory IDs retrieved
            used_in_answer: List of memory IDs actually used in answer
            user_id: Optional user ID
        """
        with self.lock:
            event = {
                "query": query,
                "retrieved_memories": retrieved_memories,
                "used_in_answer": used_in_answer,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "retrieval_count": len(retrieved_memories),
                "usage_count": len(used_in_answer),
                "effectiveness": len(used_in_answer) / len(retrieved_memories) if retrieved_memories else 0.0
            }
            self.search_log.append(event)
            
            # Update effectiveness scores
            for memory_id in used_in_answer:
                if memory_id not in self.effectiveness_scores:
                    self.effectiveness_scores[memory_id] = 0.0
                # Increment effectiveness (simple scoring)
                self.effectiveness_scores[memory_id] += 1.0
    
    def get_usage_patterns(
        self,
        memory_id: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get usage patterns for memories.
        
        Args:
            memory_id: Optional specific memory ID
            days: Number of days to analyze
            
        Returns:
            Dict with usage patterns
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            if memory_id:
                # Filter by memory ID
                events = [
                    e for e in self.access_log
                    if e["memory_id"] == memory_id and datetime.fromisoformat(e["timestamp"]) >= cutoff_date
                ]
            else:
                # All events
                events = [
                    e for e in self.access_log
                    if datetime.fromisoformat(e["timestamp"]) >= cutoff_date
                ]
            
            # Group by access type
            by_type = defaultdict(int)
            by_day = defaultdict(int)
            
            for event in events:
                by_type[event["access_type"]] += 1
                day = datetime.fromisoformat(event["timestamp"]).date()
                by_day[day.isoformat()] += 1
            
            return {
                "total_events": len(events),
                "by_type": dict(by_type),
                "by_day": dict(by_day),
                "days_analyzed": days
            }
    
    def get_effectiveness_metrics(
        self,
        memory_id: Optional[str] = None,
        top_n: int = 10
    ) -> List[Dict]:
        """
        Get effectiveness metrics for memories.
        
        Args:
            memory_id: Optional specific memory ID
            top_n: Number of top memories to return
            
        Returns:
            List of memory effectiveness metrics
        """
        with self.lock:
            if memory_id:
                # Single memory
                if memory_id in self.effectiveness_scores:
                    return [{
                        "memory_id": memory_id,
                        "effectiveness_score": self.effectiveness_scores[memory_id],
                        "usage_count": self.usage_counts.get(memory_id, 0)
                    }]
                else:
                    return []
            else:
                # Top N memories
                sorted_memories = sorted(
                    self.effectiveness_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:top_n]
                
                return [
                    {
                        "memory_id": mem_id,
                        "effectiveness_score": score,
                        "usage_count": self.usage_counts.get(mem_id, 0)
                    }
                    for mem_id, score in sorted_memories
                ]
    
    def get_search_frequency(
        self,
        days: int = 30
    ) -> Dict:
        """
        Get search frequency statistics.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with search frequency metrics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.lock:
            recent_searches = [
                s for s in self.search_log
                if datetime.fromisoformat(s["timestamp"]) >= cutoff_date
            ]
            
            total_searches = len(recent_searches)
            avg_retrieval = sum(s["retrieval_count"] for s in recent_searches) / total_searches if total_searches > 0 else 0
            avg_usage = sum(s["usage_count"] for s in recent_searches) / total_searches if total_searches > 0 else 0
            avg_effectiveness = sum(s["effectiveness"] for s in recent_searches) / total_searches if total_searches > 0 else 0
            
            return {
                "total_searches": total_searches,
                "avg_retrieval_count": avg_retrieval,
                "avg_usage_count": avg_usage,
                "avg_effectiveness": avg_effectiveness,
                "days_analyzed": days
            }
    
    def get_analytics_summary(self) -> Dict:
        """
        Get comprehensive analytics summary.
        
        Returns:
            Dict with analytics summary
        """
        with self.lock:
            return {
                "total_memories_tracked": len(self.usage_counts),
                "total_access_events": len(self.access_log),
                "total_search_events": len(self.search_log),
                "most_used_memories": [
                    {"memory_id": mem_id, "count": count}
                    for mem_id, count in sorted(
                        self.usage_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:10]
                ],
                "most_effective_memories": self.get_effectiveness_metrics(top_n=10),
                "search_frequency": self.get_search_frequency(days=30)
            }


# Global analytics instance
memory_analytics = MemoryAnalytics()

def get_memory_analytics() -> MemoryAnalytics:
    """Get global memory analytics instance."""
    return memory_analytics

