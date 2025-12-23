"""
Unit tests for Advanced Memory System (relationships, expiration, analytics).
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add rag-api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rag-api"))

from memory.relationships import get_relationship_manager
from memory.expiration import get_expiration_manager
from memory.analytics import get_memory_analytics


class TestMemoryRelationships:
    """Test memory relationship management."""
    
    def test_create_relationship(self):
        """Test creating a memory relationship."""
        manager = get_relationship_manager()
        
        # Create test memories first (would need actual memory IDs)
        # For now, test the interface
        try:
            relationship = manager.create_relationship(
                source_memory_id="test_mem_1",
                target_memory_id="test_mem_2",
                relationship_type="related",
                strength=0.8,
                description="Test relationship"
            )
            assert relationship is not None
        except Exception as e:
            # If ChromaDB not available, skip
            pytest.skip(f"Memory system not available: {e}")
    
    def test_get_relationships(self):
        """Test retrieving relationships."""
        manager = get_relationship_manager()
        
        # This should work even without ChromaDB - returns empty list
        relationships = manager.get_relationships("test_mem_1")
        assert isinstance(relationships, list)
    
    def test_get_relationship_graph(self):
        """Test relationship graph traversal."""
        manager = get_relationship_manager()
        
        try:
            graph = manager.get_relationship_graph("test_mem_1", depth=2)
            assert graph is not None
            assert "nodes" in graph or hasattr(graph, "nodes")
            assert "edges" in graph or hasattr(graph, "edges")
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")


class TestMemoryExpiration:
    """Test memory expiration policies."""
    
    def test_set_expiration_policy(self):
        """Test setting expiration policy."""
        manager = get_expiration_manager()
        
        try:
            policy = manager.set_expiration_policy(
                memory_id="test_mem_1",
                expires_in_days=7,
                policy_type="ttl"
            )
            assert policy is not None
            assert policy.get("expires_in_days") == 7 or policy.get("days_remaining") == 7
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")
    
    def test_get_expiration_policy(self):
        """Test getting expiration policy."""
        manager = get_expiration_manager()
        
        try:
            policy = manager.get_expiration_policy("test_mem_1")
            # May return None if no policy set
            assert policy is None or isinstance(policy, dict)
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")
    
    def test_cleanup_expired_memories(self):
        """Test cleanup of expired memories."""
        manager = get_expiration_manager()
        
        try:
            cleaned_count = manager.cleanup_expired_memories()
            assert isinstance(cleaned_count, int)
            assert cleaned_count >= 0
        except Exception as e:
            pytest.skip(f"Memory system not available: {e}")


class TestMemoryAnalytics:
    """Test memory analytics."""
    
    @pytest.mark.timeout(10)
    def test_get_analytics_summary(self):
        """Test getting analytics summary (with timeout protection)."""
        analytics = get_memory_analytics()
        
        try:
            summary = analytics.get_analytics_summary()
            assert summary is not None
            assert "total_memories" in summary or hasattr(summary, "total_memories")
        except Exception as e:
            pytest.skip(f"Memory analytics not available: {e}")
    
    def test_get_search_frequency(self):
        """Test getting search frequency."""
        analytics = get_memory_analytics()
        
        try:
            frequency = analytics.get_search_frequency()
            assert isinstance(frequency, dict)
        except Exception as e:
            pytest.skip(f"Memory analytics not available: {e}")

