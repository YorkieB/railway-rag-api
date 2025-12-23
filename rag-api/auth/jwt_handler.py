"""
JWT Token Handler

Handles JWT token creation, validation, and refresh.
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import bcrypt

# Password hashing - using bcrypt directly

# JWT secret key
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token (typically user_id, email)
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    # Debug logging
    print(f"DEBUG hash_password: Received password type: {type(password)}, value: {repr(password)}")
    
    # Ensure password is bytes
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    elif isinstance(password, bytes):
        password_bytes = password
    else:
        raise ValueError(f"Password must be str or bytes, got {type(password)}")
    
    print(f"DEBUG hash_password: Password bytes length: {len(password_bytes)}")
    
    # Truncate to 72 bytes if necessary (bcrypt limit)
    if len(password_bytes) > 72:
        print(f"DEBUG hash_password: Truncating password from {len(password_bytes)} to 72 bytes")
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        result = hashed.decode('utf-8')
        print(f"DEBUG hash_password: Successfully hashed password")
        return result
    except Exception as e:
        print(f"DEBUG hash_password: Error during hashing: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Ensure both are bytes
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    
    # Truncate password to 72 bytes if necessary
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    
    try:
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False

