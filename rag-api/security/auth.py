"""
JWT Authentication

Provides JWT token generation, validation, and authentication decorators.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: Optional[str] = None
    roles: list[str] = []


class JWTManager:
    """JWT token management."""
    
    def __init__(self, secret: str = JWT_SECRET, algorithm: str = JWT_ALGORITHM):
        """
        Initialize JWT manager.
        
        Args:
            secret: JWT secret key
            algorithm: JWT algorithm
        """
        self.secret = secret
        self.algorithm = algorithm
        if secret == "your-secret-key-change-in-production":
            print("⚠️ WARNING: Using default JWT secret. Change JWT_SECRET in production!")
    
    def create_token(
        self,
        user_id: str,
        email: Optional[str] = None,
        roles: list[str] = None,
        expires_in_hours: Optional[int] = None
    ) -> str:
        """
        Create a JWT token.
        
        Args:
            user_id: User ID
            email: User email
            roles: User roles
            expires_in_hours: Token expiration in hours
        
        Returns:
            JWT token string
        """
        expiration = expires_in_hours or JWT_EXPIRATION_HOURS
        expires_at = datetime.utcnow() + timedelta(hours=expiration)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "roles": roles or [],
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            TokenData with user information
        
        Raises:
            HTTPException if token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            
            return TokenData(
                user_id=payload.get("user_id"),
                email=payload.get("email"),
                roles=payload.get("roles", [])
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def refresh_token(self, token: str) -> str:
        """
        Refresh a JWT token.
        
        Args:
            token: Current JWT token
        
        Returns:
            New JWT token
        """
        token_data = self.verify_token(token)
        return self.create_token(
            user_id=token_data.user_id,
            email=token_data.email,
            roles=token_data.roles
        )


# Global JWT manager instance
_jwt_manager: Optional[JWTManager] = None

def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance."""
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager()
    return _jwt_manager


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> TokenData:
    """
    FastAPI dependency for JWT authentication.
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(require_auth)):
            return {"user_id": user.user_id}
    """
    jwt_manager = get_jwt_manager()
    token = credentials.credentials
    return jwt_manager.verify_token(token)


async def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: TokenData = Depends(require_role("admin"))):
            return {"message": "Admin access"}
    """
    async def role_checker(user: TokenData = Depends(require_auth)) -> TokenData:
        if required_role not in user.roles:
            raise HTTPException(
                status_code=403,
                detail=f"Required role: {required_role}"
            )
        return user
    
    return role_checker

