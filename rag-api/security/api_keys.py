"""
API Key Management

Manages API keys for service-to-service authentication.
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
import os
import hashlib
import secrets
from dataclasses import dataclass


@dataclass
class APIKey:
    """API Key data structure."""
    key_id: str
    key_hash: str  # Hashed key (never store plain keys)
    name: str
    user_id: Optional[str] = None
    permissions: List[str] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class APIKeyManager:
    """Manages API keys for authentication."""
    
    def __init__(self):
        """Initialize API key manager."""
        # In production, store in database
        # For now, use in-memory storage
        self._keys: Dict[str, APIKey] = {}
        self._key_by_hash: Dict[str, APIKey] = {}
    
    def generate_key(
        self,
        name: str,
        user_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """
        Generate a new API key.
        
        Args:
            name: Key name/description
            user_id: Associated user ID
            permissions: List of permissions
            expires_in_days: Expiration in days (None = no expiration)
        
        Returns:
            Tuple of (plain_key, APIKey object)
        """
        # Generate secure random key
        plain_key = f"jarvis_{secrets.token_urlsafe(32)}"
        
        # Hash the key
        key_hash = hashlib.sha256(plain_key.encode()).hexdigest()
        
        # Generate key ID
        key_id = secrets.token_urlsafe(16)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            permissions=permissions or [],
            expires_at=expires_at
        )
        
        # Store (in production, save to database)
        self._keys[key_id] = api_key
        self._key_by_hash[key_hash] = api_key
        
        return plain_key, api_key
    
    def verify_key(self, api_key: str) -> Optional[APIKey]:
        """
        Verify an API key.
        
        Args:
            api_key: Plain API key string
        
        Returns:
            APIKey object if valid, None otherwise
        """
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Look up key
        stored_key = self._key_by_hash.get(key_hash)
        
        if not stored_key:
            return None
        
        # Check if active
        if not stored_key.is_active:
            return None
        
        # Check expiration
        if stored_key.expires_at and stored_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        stored_key.last_used_at = datetime.utcnow()
        
        return stored_key
    
    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: Key ID to revoke
        
        Returns:
            True if revoked, False if not found
        """
        if key_id in self._keys:
            self._keys[key_id].is_active = False
            return True
        return False
    
    def list_keys(self, user_id: Optional[str] = None) -> List[APIKey]:
        """
        List API keys.
        
        Args:
            user_id: Filter by user ID
        
        Returns:
            List of API keys
        """
        keys = list(self._keys.values())
        
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
        
        return keys
    
    def get_key(self, key_id: str) -> Optional[APIKey]:
        """Get API key by ID."""
        return self._keys.get(key_id)


# Global API key manager instance
_api_key_manager: Optional[APIKeyManager] = None

def get_api_key_manager() -> APIKeyManager:
    """Get API key manager instance."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

