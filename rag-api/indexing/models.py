"""
Indexing data models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class DocumentType(str, Enum):
    """Types of documents that can be indexed."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "markdown"
    CODE = "code"
    WEB = "web"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class IndexMetadata:
    """Metadata for an indexed document."""
    document_id: str
    document_type: DocumentType
    source: str  # File path, URL, etc.
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    indexed_at: datetime = field(default_factory=datetime.utcnow)
    size: Optional[int] = None  # Size in bytes
    language: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexedDocument:
    """Represents an indexed document."""
    id: str
    content: str
    metadata: IndexMetadata
    chunks: List[str] = field(default_factory=list)
    embeddings: Optional[List[List[float]]] = None
    summary: Optional[str] = None


@dataclass
class SearchResult:
    """Result from a search query."""
    document_id: str
    document_type: DocumentType
    title: Optional[str]
    snippet: str
    relevance_score: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeNode:
    """Node in knowledge graph."""
    id: str
    label: str
    node_type: str  # "concept", "entity", "document", etc.
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    """Edge in knowledge graph."""
    source_id: str
    target_id: str
    relationship: str  # "references", "contains", "related_to", etc.
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)

