"""
User Management

Handles user registration, authentication, and user data.
"""
import os
import json
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import uuid
import secrets
from .jwt_handler import hash_password, verify_password, create_access_token

# Persistent user storage file
USER_STORAGE_FILE = os.getenv("USER_STORAGE_FILE", os.path.join(os.getcwd(), "users.json"))

def load_users() -> Dict[str, Dict]:
    """Load users from persistent storage"""
    if os.path.exists(USER_STORAGE_FILE):
        try:
            with open(USER_STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"Warning: Could not load users from {USER_STORAGE_FILE}: {e}")
            return {}
    return {}

def save_users(users: Dict[str, Dict]) -> bool:
    """Save users to persistent storage"""
    try:
        # Create directory if it doesn't exist
        storage_dir = os.path.dirname(USER_STORAGE_FILE) if os.path.dirname(USER_STORAGE_FILE) else '.'
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)
        
        with open(USER_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error: Could not save users to {USER_STORAGE_FILE}: {e}")
        return False

# Load users from persistent storage on module import
users_db: Dict[str, Dict] = load_users()


class UserManager:
    """Manages user accounts and authentication"""
    
    def create_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict:
        """
        Create new user account.
        
        Args:
            email: User email
            password: Plain text password
            username: Optional username
            is_admin: Whether user is admin (default: False, first user becomes admin)
            
        Returns:
            Dict with user_id and user data
        """
        # Check if user exists
        for user_id, user_data in users_db.items():
            if user_data.get("email") == email:
                raise Exception("User already exists")
        
        user_id = str(uuid.uuid4())
        
        # Debug: Check password type and length
        print(f"DEBUG: Creating user - email: {email}, password type: {type(password)}, password length: {len(password) if isinstance(password, str) else 'N/A'}")
        
        try:
            hashed_password = hash_password(password)
            print(f"DEBUG: Password hashed successfully")
        except Exception as e:
            print(f"DEBUG: Password hashing failed: {e}")
            print(f"DEBUG: Password value: {repr(password)}")
            raise
        
        # First user automatically becomes admin
        if len(users_db) == 0:
            is_admin = True
        
        user_data = {
            "user_id": user_id,
            "email": email,
            "username": username or email.split("@")[0],
            "password_hash": hashed_password,
            "created_at": datetime.now().isoformat(),
            "is_active": True,
            "is_admin": is_admin,
            "reset_token": None,
            "reset_token_expiry": None
        }
        
        users_db[user_id] = user_data
        save_users(users_db)  # Persist to disk
        
        return {
            "user_id": user_id,
            "email": email,
            "username": user_data["username"],
            "created_at": user_data["created_at"],
            "is_admin": is_admin
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
            "username": user_data["username"],
            "is_admin": user_data.get("is_admin", False)
        }
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user_data["user_id"],
                "email": email,
                "username": user_data["username"],
                "is_admin": user_data.get("is_admin", False)
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
            "created_at": user_data["created_at"],
            "is_admin": user_data.get("is_admin", False)
        }
    
    def list_users(self) -> List[Dict]:
        """List all users"""
        return [
            {
                "user_id": user["user_id"],
                "email": user["email"],
                "username": user["username"],
                "created_at": user["created_at"],
                "is_admin": user.get("is_admin", False)
            }
            for user in users_db.values()
        ]
    
    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """Update user password (admin can reset any user password)"""
        user_data = users_db.get(user_id)
        if not user_data:
            return False
        
        user_data["password_hash"] = hash_password(new_password)
        user_data["reset_token"] = None
        user_data["reset_token_expiry"] = None
        return True
    
    def generate_password_reset_token(self, email: str) -> Optional[str]:
        """Generate password reset token for user"""
        user_data = None
        for user_id, user in users_db.items():
            if user.get("email") == email:
                user_data = user
                break
        
        if not user_data:
            return None  # Don't reveal if email exists
        
        # Generate secure token
        reset_token = secrets.token_urlsafe(32)
        reset_token_expiry = datetime.now() + timedelta(hours=1)  # 1 hour expiry
        
        user_data["reset_token"] = reset_token
        user_data["reset_token_expiry"] = reset_token_expiry.isoformat()
        save_users(users_db)  # Persist to disk
        
        return reset_token
    
    def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify reset token and return user_id if valid"""
        for user_id, user_data in users_db.items():
            if user_data.get("reset_token") == token:
                expiry_str = user_data.get("reset_token_expiry")
                if expiry_str:
                    expiry = datetime.fromisoformat(expiry_str)
                    if datetime.now() < expiry:
                        return user_id
        return None
    
    def reset_password_with_token(self, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        user_id = self.verify_reset_token(token)
        if not user_id:
            return False
        
        user_data = users_db.get(user_id)
        if not user_data:
            return False
        
        user_data["password_hash"] = hash_password(new_password)
        user_data["reset_token"] = None
        user_data["reset_token_expiry"] = None
        save_users(users_db)  # Persist to disk
        return True
    
    def set_admin(self, user_id: str, is_admin: bool) -> bool:
        """Set admin status for user"""
        user_data = users_db.get(user_id)
        if not user_data:
            return False
        
        user_data["is_admin"] = is_admin
        save_users(users_db)  # Persist to disk
        return True
    
    def update_user(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> bool:
        """Update user email and/or username"""
        user_data = users_db.get(user_id)
        if not user_data:
            return False
        
        # Check if email already exists (if changing)
        if email and email != user_data.get("email"):
            for uid, user in users_db.items():
                if uid != user_id and user.get("email") == email:
                    raise Exception("Email already exists")
        
        if email:
            user_data["email"] = email
        if username:
            user_data["username"] = username
        
        save_users(users_db)  # Persist to disk
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id in users_db:
            del users_db[user_id]
            save_users(users_db)  # Persist to disk
            return True
        return False
    
    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        user_data = users_db.get(user_id)
        if not user_data:
            return False
        return user_data.get("is_admin", False)


# Global user manager instance
user_manager = UserManager()

