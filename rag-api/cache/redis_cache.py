"""
Redis Cache Implementation

Provides Redis-based caching for improved performance.
"""

from typing import Optional, Any
import os
import json
import pickle
from datetime import timedelta

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None


class RedisCache:
    """Redis-based cache implementation."""
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 3600,
        key_prefix: str = "jarvis:"
    ):
        """
        Initialize Redis cache.
        
        Args:
            redis_url: Redis connection URL (defaults to env var)
            default_ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis package is required. Install with: pip install redis"
            )
        
        redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        
        # Initialize Redis client
        try:
            self.client = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.client.ping()
        except Exception as e:
            raise Exception(f"Failed to connect to Redis: {e}")
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            full_key = self._make_key(key)
            value = self.client.get(full_key)
            
            if value is None:
                return None
            
            # Deserialize
            try:
                return pickle.loads(value)
            except:
                # Fallback to JSON
                return json.loads(value.decode('utf-8'))
        except Exception as e:
            # Log error but don't fail
            print(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (defaults to default_ttl)
        
        Returns:
            True if successful
        """
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize
            try:
                serialized = pickle.dumps(value)
            except:
                # Fallback to JSON
                serialized = json.dumps(value).encode('utf-8')
            
            # Set with expiration
            self.client.setex(full_key, ttl, serialized)
            return True
        except Exception as e:
            # Log error but don't fail
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted
        """
        try:
            full_key = self._make_key(key)
            return bool(self.client.delete(full_key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*")
        
        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            keys = self.client.keys(full_pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            full_key = self._make_key(key)
            return bool(self.client.exists(full_key))
        except:
            return False
    
    def get_or_set(
        self,
        key: str,
        callable_func,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache, or compute and cache if not found.
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            ttl: Time-to-live in seconds
        
        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = callable_func()
        
        # Cache it
        self.set(key, value, ttl)
        
        return value


# Global cache instance
_cache: Optional[RedisCache] = None

def get_cache() -> Optional[RedisCache]:
    """Get cache instance."""
    global _cache
    if _cache is None:
        enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        if enabled:
            try:
                _cache = RedisCache(
                    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                    default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", "3600")),
                    key_prefix=os.getenv("REDIS_KEY_PREFIX", "jarvis:")
                )
                print("✅ Redis cache enabled")
            except Exception as e:
                print(f"⚠️ Failed to initialize Redis cache: {e}")
                _cache = None
        else:
            print("ℹ️ Redis cache disabled")
    return _cache

