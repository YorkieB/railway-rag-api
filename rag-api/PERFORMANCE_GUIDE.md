# Performance Optimization Guide

This guide covers performance optimizations implemented in Jarvis.

## Features

### 1. Redis Caching

Redis caching improves response times by caching frequently accessed data.

#### Setup

1. **Install Redis:**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   
   # Linux
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # Docker
   docker run -d -p 6379:6379 redis:latest
   ```

2. **Configure Environment:**
   ```bash
   REDIS_ENABLED=true
   REDIS_URL=redis://localhost:6379
   REDIS_DEFAULT_TTL=3600
   REDIS_KEY_PREFIX=jarvis:
   CACHE_TTL=300
   ```

3. **Install Python Package:**
   ```bash
   pip install redis
   ```

#### How It Works

- **Automatic Caching:** GET requests are automatically cached
- **TTL:** Cached responses expire after configured time
- **Key Prefixing:** All keys prefixed with `jarvis:`
- **Graceful Degradation:** If Redis unavailable, app continues without cache

#### Excluded Paths

These paths are not cached:
- `/docs`
- `/redoc`
- `/openapi.json`
- `/health`
- `/metrics`

#### Manual Caching

You can also use cache manually:

```python
from rag_api.cache import get_cache

cache = get_cache()

# Get or set
value = cache.get_or_set(
    "user:123",
    lambda: expensive_operation(),
    ttl=3600
)

# Direct operations
cache.set("key", "value", ttl=3600)
value = cache.get("key")
cache.delete("key")
```

### 2. Connection Pooling

Database connections are pooled for better performance.

#### Firestore

Firestore client automatically manages connection pooling.

#### BigQuery

BigQuery client uses connection pooling internally.

### 3. Query Optimization

#### Memory Queries

- Use project_id filters when possible
- Limit result sets
- Use search instead of full scans

#### Indexing

- Index frequently queried fields
- Use composite indexes for multi-field queries

### 4. Response Compression

Consider enabling gzip compression:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 5. Async Operations

All I/O operations are async for better concurrency:
- Database queries
- API calls
- File operations

## Performance Monitoring

### Metrics Endpoint

Monitor performance via `/metrics` endpoint:
- Request counts
- Latency percentiles (p50, p95, p99)
- Error rates
- Cache hit rates

### Key Metrics to Monitor

1. **Response Times:**
   - Average latency
   - P95 latency
   - P99 latency

2. **Throughput:**
   - Requests per second
   - Concurrent requests

3. **Cache Performance:**
   - Cache hit rate
   - Cache miss rate
   - Cache size

4. **Database Performance:**
   - Query latency
   - Connection pool usage
   - Query errors

## Optimization Tips

### 1. Cache Strategy

- **Cache frequently accessed data:** User profiles, configurations
- **Use appropriate TTLs:** Short for dynamic data, long for static
- **Invalidate on updates:** Clear cache when data changes
- **Cache at multiple levels:** Application cache + CDN

### 2. Database Queries

- **Use indexes:** Create indexes on frequently queried fields
- **Limit results:** Don't fetch more data than needed
- **Use projections:** Only fetch required fields
- **Batch operations:** Group multiple operations

### 3. API Calls

- **Batch requests:** Combine multiple API calls
- **Use async:** Don't block on I/O
- **Implement retries:** With exponential backoff
- **Cache responses:** Cache external API responses

### 4. Frontend Optimization

- **Code splitting:** Load only needed code
- **Lazy loading:** Load components on demand
- **Image optimization:** Compress and resize images
- **CDN:** Use CDN for static assets

## Load Testing

### Tools

- **Locust:** Python-based load testing
- **Apache Bench:** Simple HTTP benchmarking
- **k6:** Modern load testing tool

### Example Load Test

```python
from locust import HttpUser, task, between

class JarvisUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def query(self):
        self.client.post("/query", json={
            "message": "test query",
            "user_id": "user123"
        })
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer
- Stateless application design
- Shared cache (Redis)
- Shared database (Firestore/BigQuery)

### Vertical Scaling

- Increase server resources
- Optimize code
- Use faster hardware

### Database Scaling

- Firestore: Automatic scaling
- BigQuery: Automatic scaling
- Consider read replicas for high read loads

## Performance Checklist

- [ ] Redis caching enabled
- [ ] Connection pooling configured
- [ ] Database indexes created
- [ ] Response compression enabled
- [ ] Async operations used
- [ ] Monitoring set up
- [ ] Load testing performed
- [ ] Performance baselines established
- [ ] Optimization targets defined
- [ ] Regular performance reviews scheduled

