"""
Authentication REST API Router

Provides endpoints for authentication and API key management.
"""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from .auth import JWTManager, get_jwt_manager, require_auth, TokenData
from .api_keys import APIKeyManager, get_api_key_manager

router = APIRouter(prefix="/auth", tags=["auth"])

security_scheme = HTTPBearer()


# Request/Response Models
class LoginRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # In production, verify password hash


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class APIKeyCreateRequest(BaseModel):
    name: str
    permissions: Optional[List[str]] = None
    expires_in_days: Optional[int] = None


class APIKeyResponse(BaseModel):
    key_id: str
    key: str  # Only returned on creation
    name: str
    permissions: List[str]
    expires_at: Optional[str] = None


# Endpoints
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, jwt_manager: JWTManager = Depends(get_jwt_manager)):
    """
    Login and get JWT token.
    
    Note: In production, verify password against database.
    """
    # TODO: Verify user credentials against database
    # For now, just create token for any user_id
    
    token = jwt_manager.create_token(
        user_id=request.user_id,
        email=request.email,
        roles=[]  # TODO: Get roles from database
    )
    
    return TokenResponse(
        access_token=token,
        expires_in=24 * 3600  # 24 hours in seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    jwt_manager: JWTManager = Depends(get_jwt_manager)
):
    """Refresh JWT token."""
    token = credentials.credentials
    new_token = jwt_manager.refresh_token(token)
    
    return TokenResponse(
        access_token=new_token,
        expires_in=24 * 3600
    )


@router.get("/me")
async def get_current_user(user: TokenData = Depends(require_auth)):
    """Get current user information from token."""
    return {
        "user_id": user.user_id,
        "email": user.email,
        "roles": user.roles
    }


# API Key Management
@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    user: TokenData = Depends(require_auth),
    key_manager: APIKeyManager = Depends(get_api_key_manager)
):
    """Create a new API key."""
    plain_key, api_key = key_manager.generate_key(
        name=request.name,
        user_id=user.user_id,
        permissions=request.permissions,
        expires_in_days=request.expires_in_days
    )
    
    return APIKeyResponse(
        key_id=api_key.key_id,
        key=plain_key,  # Only time plain key is returned
        name=api_key.name,
        permissions=api_key.permissions,
        expires_at=api_key.expires_at.isoformat() if api_key.expires_at else None
    )


@router.get("/api-keys")
async def list_api_keys(
    user: TokenData = Depends(require_auth),
    key_manager: APIKeyManager = Depends(get_api_key_manager)
):
    """List API keys for current user."""
    keys = key_manager.list_keys(user_id=user.user_id)
    
    return {
        "keys": [
            {
                "key_id": k.key_id,
                "name": k.name,
                "permissions": k.permissions,
                "created_at": k.created_at.isoformat(),
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                "is_active": k.is_active
            }
            for k in keys
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: TokenData = Depends(require_auth),
    key_manager: APIKeyManager = Depends(get_api_key_manager)
):
    """Revoke an API key."""
    key = key_manager.get_key(key_id)
    
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    if key.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    key_manager.revoke_key(key_id)
    
    return {"status": "revoked"}

