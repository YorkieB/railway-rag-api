# Security Guide

This guide covers security features and best practices for the Jarvis API.

## Features

### 1. JWT Authentication

JWT (JSON Web Tokens) are used for user authentication.

#### Getting a Token

```bash
POST /auth/login
{
  "user_id": "user123",
  "email": "user@example.com"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Using a Token

Include in Authorization header:
```
Authorization: Bearer <token>
```

#### Protected Endpoints

```python
from rag_api.security.auth import require_auth, TokenData

@app.get("/protected")
async def protected_route(user: TokenData = Depends(require_auth)):
    return {"user_id": user.user_id}
```

#### Role-Based Access

```python
from rag_api.security.auth import require_role

@app.get("/admin")
async def admin_route(user: TokenData = Depends(require_role("admin"))):
    return {"message": "Admin access"}
```

### 2. Rate Limiting

Rate limiting prevents abuse by limiting requests per time period.

#### Configuration

```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000
RATE_LIMIT_REQUESTS_PER_DAY=10000
```

#### How It Works

- Limits are applied per IP address or user ID
- Authenticated users get separate limits
- Returns `429 Too Many Requests` when exceeded
- Includes `Retry-After` header

#### Excluded Paths

These paths are excluded from rate limiting:
- `/docs`
- `/redoc`
- `/openapi.json`
- `/health`

### 3. Input Validation

All user input should be validated before processing.

#### Usage

```python
from rag_api.security.validation import validate_input, sanitize_input

# Validate input
user_id = validate_input(
    request.user_id,
    field_type=str,
    min_length=1,
    max_length=100,
    required=True
)

# Sanitize input
safe_content = sanitize_input(user_input, allow_html=False)
```

#### Validation Functions

- `validate_email(email)` - Validate email format
- `validate_url(url)` - Validate URL format
- `validate_uuid(uuid_string)` - Validate UUID format
- `sanitize_filename(filename)` - Sanitize file names

### 4. API Key Management

API keys for service-to-service authentication.

#### Create API Key

```bash
POST /auth/api-keys
Authorization: Bearer <jwt_token>
{
  "name": "My Service",
  "permissions": ["read", "write"],
  "expires_in_days": 90
}

Response:
{
  "key_id": "abc123",
  "key": "jarvis_...",  # Only shown once!
  "name": "My Service",
  "permissions": ["read", "write"],
  "expires_at": "2026-03-25T00:00:00Z"
}
```

#### List API Keys

```bash
GET /auth/api-keys
Authorization: Bearer <jwt_token>
```

#### Revoke API Key

```bash
DELETE /auth/api-keys/{key_id}
Authorization: Bearer <jwt_token>
```

## Security Best Practices

### 1. Environment Variables

- Never commit secrets to version control
- Use strong, unique secrets for JWT
- Rotate secrets regularly
- Use secret management services in production

### 2. JWT Secrets

```bash
# Generate a strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
JWT_SECRET=<generated-secret>
```

### 3. Rate Limiting

- Adjust limits based on your use case
- Monitor rate limit violations
- Consider different limits for different endpoints
- Use user-based limits for authenticated users

### 4. Input Validation

- Always validate user input
- Sanitize HTML content
- Validate file uploads
- Check file sizes and types

### 5. API Keys

- Store keys securely (never in code)
- Rotate keys regularly
- Set appropriate expiration dates
- Revoke unused keys
- Use least privilege (minimal permissions)

### 6. HTTPS

- Always use HTTPS in production
- Configure SSL/TLS certificates
- Use secure cookie settings
- Enable HSTS headers

### 7. CORS

Configure CORS properly:
```python
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### 8. Error Handling

- Don't expose sensitive information in errors
- Log errors securely
- Use generic error messages for users
- Include detailed errors only in logs

## Production Checklist

- [ ] Change default JWT secret
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Use HTTPS
- [ ] Set up monitoring for security events
- [ ] Enable audit logging
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Use secret management service
- [ ] Implement proper password hashing (if adding password auth)
- [ ] Set up intrusion detection
- [ ] Regular penetration testing

## Monitoring

Monitor these security metrics:
- Failed authentication attempts
- Rate limit violations
- Unusual API usage patterns
- Error rates
- Token expiration rates

## Incident Response

If a security incident occurs:
1. Revoke compromised tokens/keys immediately
2. Rotate secrets
3. Review access logs
4. Notify affected users
5. Document the incident
6. Update security measures

