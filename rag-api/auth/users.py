"""
User Management

Handles user registration, authentication, and user data.
"""
import os
from typing import Optional, Dict, List
from datetime import datetime
import uuid
from .jwt_handler import hash_password, verify_password, create_access_token

# In-memory user storage (future: use database)
users_db: Dict[str, Dict] = {}


class UserManager:
    """Manages user accounts and authentication"""
    
    def create_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None
    ) -> Dict:
        """
        Create new user account.
        
        Args:
            email: User email
            password: Plain text password
            username: Optional username
            
        Returns:
            Dict with user_id and user data
        """
        # Check if user exists
        for user_id, user_data in users_db.items():
            if user_data.get("email") == email:
                raise Exception("User already exists")
        
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        user_data = {
            "user_id": user_id,
            "email": email,
            "username": username or email.split("@")[0],
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_active": True
        }
        
        users_db[user_id] = user_data
        
        return {
            "user_id": user_id,
            "email": email,
            "username": user_data["username"],
            "created_at": user_data["created_at"]
        }
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Authenticate user and return access token.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Dict with access_token and user data, or None if invalid
        """
        # Find user
        user_data = None
        for user_id, user in users_db.items():
            if user.get("email") == email:
                user_data = user
                break
        
        if not user_data:
            return None
        
        # Verify password
        if not verify_password(password, user_data["password_hash"]):
            return None
        
        # Create access token
        token_data = {
            "sub": user_data["user_id"],
            "email": email,
            "username": user_data["username"]
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user_data["user_id"],
                "email": email,
                "username": user_data["username"]
            }
        }
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        user_data = users_db.get(user_id)
        if not user_data:
            return None
        
        return {
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "username": user_data["username"],
            "created_at": user_data["created_at"]
        }
    
    def list_users(self) -> List[Dict]:
        """List all users"""
        return [
            {
                "user_id": user["user_id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"]
            }
            for user in users_db.values()
        ]


# Global user manager instance
user_manager = UserManager()

