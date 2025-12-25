"""
Metrics Collection

Tracks performance metrics, request counts, latency, etc.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading


class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.Lock()
        self._counters = defaultdict(int)
        self._histograms = defaultdict(list)
        self._gauges = {}
        self._start_time = datetime.utcnow()
    
    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self._counters[key] += value
    
    def record(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram value."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self._histograms[key].append({
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            })
            # Keep only last 1000 values
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
    
    def set_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge value."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            self._gauges[key] = {
                "value": value,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_counter(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            return self._counters.get(key, 0)
    
    def get_histogram_stats(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            values = [item["value"] for item in self._histograms.get(key, [])]
            if not values:
                return {"count": 0, "min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0}
            
            values.sort()
            count = len(values)
            return {
                "count": count,
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / count,
                "p50": values[int(count * 0.5)] if count > 0 else 0,
                "p95": values[int(count * 0.95)] if count > 0 else 0,
                "p99": values[int(count * 0.99)] if count > 0 else 0,
            }
    
    def get_gauge(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get gauge value."""
        with self._lock:
            key = self._make_key(metric_name, tags)
            gauge = self._gauges.get(key)
            return gauge["value"] if gauge else None
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": {k: v["value"] for k, v in self._gauges.items()},
                "histograms": {
                    k: self.get_histogram_stats(k.split(":")[0], self._parse_tags(k))
                    for k in self._histograms.keys()
                },
                "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds()
            }
    
    def _make_key(self, metric_name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a key from metric name and tags."""
        if not tags:
            return metric_name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{metric_name}:{tag_str}"
    
    def _parse_tags(self, key: str) -> Dict[str, str]:
        """Parse tags from key."""
        if ":" not in key:
            return {}
        tag_str = key.split(":", 1)[1]
        tags = {}
        for pair in tag_str.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                tags[k] = v
        return tags


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

