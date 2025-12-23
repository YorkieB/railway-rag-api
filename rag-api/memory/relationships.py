"""
Memory Relationships
Manages relationships between memories (related, contradicts, updates).
"""
from typing import Dict, List, Optional, Set
from datetime import datetime
import uuid


class MemoryRelationship:
    """Represents a relationship between two memories."""
    
    def __init__(
        self,
        from_memory_id: str,
        to_memory_id: str,
        relationship_type: str,  # "related", "contradicts", "updates"
        strength: float = 1.0,  # 0.0 to 1.0
        metadata: Optional[Dict] = None
    ):
        self.id = str(uuid.uuid4())
        self.from_memory_id = from_memory_id
        self.to_memory_id = to_memory_id
        self.relationship_type = relationship_type
        self.strength = strength
        self.metadata = metadata or {}
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "from_memory_id": self.from_memory_id,
            "to_memory_id": self.to_memory_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class MemoryRelationshipManager:
    """
    Manages relationships between memories.
    
    Relationship Types:
    - "related": Memories are related to each other
    - "contradicts": One memory contradicts another
    - "updates": One memory updates/replaces another
    """
    
    def __init__(self, chromadb_path: Optional[str] = None):
        """
        Initialize relationship manager.
        
        Args:
            chromadb_path: Path to ChromaDB storage (for persistence)
        """
        self.chromadb_path = chromadb_path
        # In-memory storage for MVP (can be moved to ChromaDB later)
        self.relationships: Dict[str, MemoryRelationship] = {}
        self.memory_relationships: Dict[str, Set[str]] = {}  # memory_id -> set of relationship IDs
    
    def create_relationship(
        self,
        from_memory_id: str,
        to_memory_id: str,
        relationship_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict] = None
    ) -> MemoryRelationship:
        """
        Create a relationship between two memories.
        
        Args:
            from_memory_id: Source memory ID
            to_memory_id: Target memory ID
            relationship_type: Type of relationship ("related", "contradicts", "updates")
            strength: Relationship strength (0.0 to 1.0)
            metadata: Optional metadata
            
        Returns:
            Created relationship
        """
        # Validate relationship type
        if relationship_type not in ["related", "contradicts", "updates"]:
            raise ValueError(f"Invalid relationship type: {relationship_type}")
        
        # Validate strength
        if not 0.0 <= strength <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")
        
        # Create relationship
        relationship = MemoryRelationship(
            from_memory_id=from_memory_id,
            to_memory_id=to_memory_id,
            relationship_type=relationship_type,
            strength=strength,
            metadata=metadata
        )
        
        # Store relationship
        self.relationships[relationship.id] = relationship
        
        # Update memory relationship indices
        if from_memory_id not in self.memory_relationships:
            self.memory_relationships[from_memory_id] = set()
        if to_memory_id not in self.memory_relationships:
            self.memory_relationships[to_memory_id] = set()
        
        self.memory_relationships[from_memory_id].add(relationship.id)
        self.memory_relationships[to_memory_id].add(relationship.id)
        
        return relationship
    
    def get_relationships(
        self,
        memory_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both"  # "from", "to", "both"
    ) -> List[MemoryRelationship]:
        """
        Get relationships for a memory.
        
        Args:
            memory_id: Memory ID
            relationship_type: Optional filter by type
            direction: "from" (outgoing), "to" (incoming), "both"
            
        Returns:
            List of relationships
        """
        relationship_ids = self.memory_relationships.get(memory_id, set())
        relationships = [self.relationships[rel_id] for rel_id in relationship_ids]
        
        # Filter by direction
        if direction == "from":
            relationships = [r for r in relationships if r.from_memory_id == memory_id]
        elif direction == "to":
            relationships = [r for r in relationships if r.to_memory_id == memory_id]
        # "both" includes all relationships
        
        # Filter by type if specified
        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]
        
        return relationships
    
    def get_related_memories(
        self,
        memory_id: str,
        relationship_type: Optional[str] = None,
        min_strength: float = 0.0
    ) -> List[str]:
        """
        Get IDs of related memories.
        
        Args:
            memory_id: Memory ID
            relationship_type: Optional filter by type
            min_strength: Minimum relationship strength
            
        Returns:
            List of related memory IDs
        """
        relationships = self.get_relationships(memory_id, relationship_type, direction="both")
        
        related_ids = set()
        for rel in relationships:
            if rel.strength >= min_strength:
                if rel.from_memory_id == memory_id:
                    related_ids.add(rel.to_memory_id)
                else:
                    related_ids.add(rel.from_memory_id)
        
        return list(related_ids)
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """
        Delete a relationship.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            True if deleted successfully
        """
        if relationship_id not in self.relationships:
            return False
        
        relationship = self.relationships[relationship_id]
        
        # Remove from indices
        if relationship.from_memory_id in self.memory_relationships:
            self.memory_relationships[relationship.from_memory_id].discard(relationship_id)
        if relationship.to_memory_id in self.memory_relationships:
            self.memory_relationships[relationship.to_memory_id].discard(relationship_id)
        
        # Delete relationship
        del self.relationships[relationship_id]
        
        return True
    
    def get_relationship_graph(self, memory_id: str, max_depth: int = 2) -> Dict:
        """
        Get relationship graph starting from a memory.
        
        Args:
            memory_id: Starting memory ID
            max_depth: Maximum depth to traverse
            
        Returns:
            Dict with graph structure
        """
        visited = set()
        graph = {
            "root": memory_id,
            "nodes": {},
            "edges": []
        }
        
        def traverse(mem_id: str, depth: int):
            if depth > max_depth or mem_id in visited:
                return
            
            visited.add(mem_id)
            graph["nodes"][mem_id] = {"depth": depth}
            
            relationships = self.get_relationships(mem_id, direction="both")
            for rel in relationships:
                target_id = rel.to_memory_id if rel.from_memory_id == mem_id else rel.from_memory_id
                
                graph["edges"].append({
                    "from": rel.from_memory_id,
                    "to": rel.to_memory_id,
                    "type": rel.relationship_type,
                    "strength": rel.strength
                })
                
                if target_id not in visited:
                    traverse(target_id, depth + 1)
        
        traverse(memory_id, 0)
        return graph


# Global relationship manager instance
relationship_manager = None

def get_relationship_manager(chromadb_path: Optional[str] = None) -> MemoryRelationshipManager:
    """Get or create global relationship manager."""
    global relationship_manager
    if relationship_manager is None:
        relationship_manager = MemoryRelationshipManager(chromadb_path=chromadb_path)
    return relationship_manager

