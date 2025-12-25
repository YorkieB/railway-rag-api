"""
Knowledge Graph

Creates and manages a knowledge graph from indexed documents.
"""

from typing import List, Dict, Optional, Set
from datetime import datetime
import re

from .models import KnowledgeNode, KnowledgeEdge, IndexedDocument


class KnowledgeGraph:
    """Knowledge graph builder and manager."""
    
    def __init__(self):
        """Initialize knowledge graph."""
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
    
    def add_document(self, document: IndexedDocument):
        """
        Add a document to the knowledge graph.
        
        Args:
            document: IndexedDocument to add
        """
        # Create document node
        doc_node = KnowledgeNode(
            id=document.id,
            label=document.metadata.title or document.id,
            node_type="document",
            properties={
                "type": document.metadata.document_type.value,
                "source": document.metadata.source,
                "indexed_at": document.metadata.indexed_at.isoformat()
            }
        )
        self.nodes[document.id] = doc_node
        
        # Extract entities and concepts from content
        entities = self._extract_entities(document.content)
        
        # Create entity nodes and edges
        for entity in entities:
            entity_id = f"entity_{hash(entity.lower())}"
            
            if entity_id not in self.nodes:
                entity_node = KnowledgeNode(
                    id=entity_id,
                    label=entity,
                    node_type="entity",
                    properties={}
                )
                self.nodes[entity_id] = entity_node
            
            # Create edge: document -> entity
            edge = KnowledgeEdge(
                source_id=document.id,
                target_id=entity_id,
                relationship="mentions",
                weight=1.0
            )
            self.edges.append(edge)
        
        # Extract relationships between entities
        relationships = self._extract_relationships(document.content, entities)
        for rel in relationships:
            source_id = f"entity_{hash(rel['source'].lower())}"
            target_id = f"entity_{hash(rel['target'].lower())}"
            
            if source_id in self.nodes and target_id in self.nodes:
                edge = KnowledgeEdge(
                    source_id=source_id,
                    target_id=target_id,
                    relationship=rel["type"],
                    weight=rel.get("weight", 1.0)
                )
                self.edges.append(edge)
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (simplified - can use NER)."""
        # Simple approach: extract capitalized phrases and common patterns
        entities = set()
        
        # Capitalized words/phrases
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.update(capitalized)
        
        # Common entity patterns (can be enhanced with NER)
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        entities.update(emails)
        
        # URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        entities.update(urls)
        
        return list(entities)[:50]  # Limit to top 50
    
    def _extract_relationships(self, text: str, entities: List[str]) -> List[Dict]:
        """Extract relationships between entities."""
        relationships = []
        
        # Simple pattern matching for common relationships
        relationship_patterns = [
            (r"(\w+)\s+is\s+(?:a|an)\s+(\w+)", "is_a"),
            (r"(\w+)\s+has\s+(\w+)", "has"),
            (r"(\w+)\s+contains\s+(\w+)", "contains"),
            (r"(\w+)\s+related\s+to\s+(\w+)", "related_to"),
        ]
        
        for pattern, rel_type in relationship_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source = match.group(1)
                target = match.group(2)
                
                if source in entities or target in entities:
                    relationships.append({
                        "source": source,
                        "target": target,
                        "type": rel_type,
                        "weight": 1.0
                    })
        
        return relationships
    
    def get_neighbors(self, node_id: str) -> List[KnowledgeNode]:
        """Get neighboring nodes."""
        neighbors = []
        neighbor_ids = set()
        
        for edge in self.edges:
            if edge.source_id == node_id:
                neighbor_ids.add(edge.target_id)
            elif edge.target_id == node_id:
                neighbor_ids.add(edge.source_id)
        
        for nid in neighbor_ids:
            if nid in self.nodes:
                neighbors.append(self.nodes[nid])
        
        return neighbors
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find path between two nodes using BFS."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        queue = [(source_id, [source_id])]
        visited = {source_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_id == target_id:
                return path
            
            neighbors = self.get_neighbors(current_id)
            for neighbor in neighbors:
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append((neighbor.id, path + [neighbor.id]))
        
        return None
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary representation."""
        return {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type,
                    "properties": node.properties
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "relationship": edge.relationship,
                    "weight": edge.weight
                }
                for edge in self.edges
            ]
        }

