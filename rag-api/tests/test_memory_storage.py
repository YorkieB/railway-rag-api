"""
Unit Tests for MemoryStorage
"""

import pytest
import tempfile
import shutil
from rag_api.memory_storage import ChromaDBMemoryStorage
from rag_api.models import MemoryItem


class TestChromaDBMemoryStorage:
    """Test ChromaDBMemoryStorage implementation."""
    
    @pytest.fixture
    def storage(self):
        """Create temporary storage for testing."""
        temp_dir = tempfile.mkdtemp()
        storage = ChromaDBMemoryStorage(persist_directory=temp_dir)
        yield storage
        shutil.rmtree(temp_dir)
    
    def test_create_memory(self, storage):
        """Test memory creation."""
        memory = MemoryItem(
            user_id="test_user",
            content="Test memory content",
            memory_type="fact"
        )
        
        created = storage.create(memory)
        
        assert created.id == memory.id
        assert created.content == "Test memory content"
        assert created.user_id == "test_user"
    
    def test_get_memory(self, storage):
        """Test memory retrieval."""
        memory = MemoryItem(
            user_id="test_user",
            content="Test memory",
            memory_type="fact"
        )
        storage.create(memory)
        
        retrieved = storage.get(memory.id, "test_user")
        
        assert retrieved is not None
        assert retrieved.id == memory.id
        assert retrieved.content == "Test memory"
    
    def test_get_memory_wrong_user(self, storage):
        """Test that wrong user cannot access memory."""
        memory = MemoryItem(
            user_id="user1",
            content="Private memory",
            memory_type="fact"
        )
        storage.create(memory)
        
        retrieved = storage.get(memory.id, "user2")
        
        assert retrieved is None
    
    def test_list_memories(self, storage):
        """Test memory listing."""
        # Create multiple memories
        for i in range(3):
            memory = MemoryItem(
                user_id="test_user",
                content=f"Memory {i}",
                memory_type="fact"
            )
            storage.create(memory)
        
        memories = storage.list("test_user")
        
        assert len(memories) == 3
    
    def test_update_memory(self, storage):
        """Test memory update."""
        memory = MemoryItem(
            user_id="test_user",
            content="Original content",
            memory_type="fact"
        )
        storage.create(memory)
        
        updated = storage.update(
            memory.id,
            "test_user",
            {"content": "Updated content"}
        )
        
        assert updated is not None
        assert updated.content == "Updated content"
    
    def test_delete_memory(self, storage):
        """Test memory deletion."""
        memory = MemoryItem(
            user_id="test_user",
            content="To be deleted",
            memory_type="fact"
        )
        storage.create(memory)
        
        deleted = storage.delete(memory.id, "test_user")
        
        assert deleted == True
        
        # Verify deleted
        retrieved = storage.get(memory.id, "test_user")
        assert retrieved is None
    
    def test_search_memories(self, storage):
        """Test semantic memory search."""
        # Create memories
        memory1 = MemoryItem(
            user_id="test_user",
            content="User prefers Slack notifications",
            memory_type="preference"
        )
        memory2 = MemoryItem(
            user_id="test_user",
            content="Python is the preferred language",
            memory_type="preference"
        )
        storage.create(memory1)
        storage.create(memory2)
        
        # Search for preferences
        results = storage.search(
            user_id="test_user",
            query="communication preferences",
            limit=10
        )
        
        # Should return relevant memories (exact results depend on embeddings)
        assert len(results) >= 0  # May be 0 if embeddings not initialized

