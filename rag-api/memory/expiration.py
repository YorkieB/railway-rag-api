"""
Memory Expiration
Manages TTL (Time-To-Live) and expiration policies for memories.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading


class ExpirationPolicy:
    """Defines expiration policy for memories."""
    
    def __init__(
        self,
        ttl_days: Optional[int] = None,  # Time-to-live in days
        auto_cleanup: bool = True,
        priority: str = "normal"  # "high", "normal", "low"
    ):
        self.ttl_days = ttl_days
        self.auto_cleanup = auto_cleanup
        self.priority = priority
        self.created_at = datetime.now()
    
    def is_expired(self, created_at: datetime) -> bool:
        """
        Check if a memory is expired based on this policy.
        
        Args:
            created_at: Memory creation timestamp
            
        Returns:
            True if expired
        """
        if self.ttl_days is None:
            return False  # No expiration
        
        expiration_date = created_at + timedelta(days=self.ttl_days)
        return datetime.now() > expiration_date
    
    def get_expiration_date(self, created_at: datetime) -> Optional[datetime]:
        """
        Get expiration date for a memory.
        
        Args:
            created_at: Memory creation timestamp
            
        Returns:
            Expiration date or None if no expiration
        """
        if self.ttl_days is None:
            return None
        return created_at + timedelta(days=self.ttl_days)


class MemoryExpirationManager:
    """
    Manages memory expiration and cleanup.
    
    Features:
    - TTL support
    - Auto-cleanup
    - Expiration policies
    - Manual expiration override
    """
    
    def __init__(self, memory_storage=None):
        """
        Initialize expiration manager.
        
        Args:
            memory_storage: MemoryStorage instance for cleanup operations
        """
        self.memory_storage = memory_storage
        self.policies: Dict[str, ExpirationPolicy] = {}
        self.expired_memories: Dict[str, datetime] = {}  # memory_id -> expiration_date
        self.lock = threading.Lock()
        
        # Default policies
        self.default_policy = ExpirationPolicy(ttl_days=None, auto_cleanup=False)
    
    def set_policy(
        self,
        memory_id: str,
        ttl_days: Optional[int] = None,
        auto_cleanup: bool = True,
        priority: str = "normal"
    ) -> ExpirationPolicy:
        """
        Set expiration policy for a memory.
        
        Args:
            memory_id: Memory ID
            ttl_days: Time-to-live in days (None = no expiration)
            auto_cleanup: Whether to auto-cleanup when expired
            priority: Policy priority
            
        Returns:
            Created policy
        """
        policy = ExpirationPolicy(
            ttl_days=ttl_days,
            auto_cleanup=auto_cleanup,
            priority=priority
        )
        
        with self.lock:
            self.policies[memory_id] = policy
            
            # Calculate expiration date
            if self.memory_storage:
                memory = self.memory_storage.get_memory(memory_id)
                if memory:
                    expiration_date = policy.get_expiration_date(memory.created_at)
                    if expiration_date:
                        self.expired_memories[memory_id] = expiration_date
                    elif memory_id in self.expired_memories:
                        del self.expired_memories[memory_id]
        
        return policy
    
    def get_policy(self, memory_id: str) -> ExpirationPolicy:
        """
        Get expiration policy for a memory.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Expiration policy (default if not set)
        """
        return self.policies.get(memory_id, self.default_policy)
    
    def check_expiration(self, memory_id: str) -> Dict:
        """
        Check if a memory is expired.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Dict with expiration status
        """
        if not self.memory_storage:
            return {
                "expired": False,
                "expiration_date": None,
                "message": "Memory storage not available"
            }
        
        memory = self.memory_storage.get_memory(memory_id)
        if not memory:
            return {
                "expired": False,
                "expiration_date": None,
                "message": "Memory not found"
            }
        
        policy = self.get_policy(memory_id)
        is_expired = policy.is_expired(memory.created_at)
        expiration_date = policy.get_expiration_date(memory.created_at)
        
        return {
            "expired": is_expired,
            "expiration_date": expiration_date.isoformat() if expiration_date else None,
            "ttl_days": policy.ttl_days,
            "auto_cleanup": policy.auto_cleanup
        }
    
    def cleanup_expired(self, user_id: Optional[str] = None) -> Dict:
        """
        Cleanup expired memories.
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            Dict with cleanup results
        """
        if not self.memory_storage:
            return {
                "success": False,
                "error": "Memory storage not available",
                "cleaned": 0
            }
        
        cleaned = []
        
        with self.lock:
            # Get all memories (or filtered by user_id)
            if user_id:
                memories = self.memory_storage.list_memories(user_id=user_id)
            else:
                memories = self.memory_storage.list_memories()
            
            for memory in memories:
                policy = self.get_policy(memory.id)
                
                if policy.auto_cleanup and policy.is_expired(memory.created_at):
                    # Delete expired memory
                    if self.memory_storage.delete_memory(memory.id):
                        cleaned.append(memory.id)
                        # Remove from policies and expired list
                        if memory.id in self.policies:
                            del self.policies[memory.id]
                        if memory.id in self.expired_memories:
                            del self.expired_memories[memory.id]
        
        return {
            "success": True,
            "cleaned": len(cleaned),
            "memory_ids": cleaned
        }
    
    def expire_manually(self, memory_id: str) -> bool:
        """
        Manually expire a memory (override TTL).
        
        Args:
            memory_id: Memory ID
            
        Returns:
            True if expired successfully
        """
        if not self.memory_storage:
            return False
        
        with self.lock:
            # Set expiration date to now
            self.expired_memories[memory_id] = datetime.now()
            
            # Update policy to mark as expired
            if memory_id in self.policies:
                self.policies[memory_id].ttl_days = 0
            else:
                self.policies[memory_id] = ExpirationPolicy(ttl_days=0, auto_cleanup=True)
        
        return True
    
    def get_expiring_soon(self, days: int = 7) -> List[Dict]:
        """
        Get memories expiring soon.
        
        Args:
            days: Number of days ahead to check
            
        Returns:
            List of memories expiring soon
        """
        if not self.memory_storage:
            return []
        
        expiring_soon = []
        cutoff_date = datetime.now() + timedelta(days=days)
        
        with self.lock:
            for memory_id, expiration_date in self.expired_memories.items():
                if expiration_date <= cutoff_date:
                    memory = self.memory_storage.get_memory(memory_id)
                    if memory:
                        expiring_soon.append({
                            "memory_id": memory_id,
                            "expiration_date": expiration_date.isoformat(),
                            "days_until_expiration": (expiration_date - datetime.now()).days,
                            "memory": memory.to_dict() if hasattr(memory, 'to_dict') else str(memory)
                        })
        
        return expiring_soon


# Global expiration manager instance
expiration_manager = None

def get_expiration_manager(memory_storage=None) -> MemoryExpirationManager:
    """Get or create global expiration manager."""
    global expiration_manager
    if expiration_manager is None:
        expiration_manager = MemoryExpirationManager(memory_storage=memory_storage)
    return expiration_manager

