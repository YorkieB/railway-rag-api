"""
Universal Knowledge Indexing & Access Module

Provides capabilities to index and search all types of information:
- Documents (PDF, DOCX, TXT, etc.)
- Code repositories
- Web content
- Media files (images, audio, video)
- Knowledge graph creation
"""

from .models import IndexedDocument, IndexMetadata, SearchResult, DocumentType
from .document_indexer import DocumentIndexer
from .code_indexer import CodeIndexer
from .web_indexer import WebIndexer
from .media_indexer import MediaIndexer
from .knowledge_graph import KnowledgeGraph
from .universal_search import UniversalSearch

__all__ = [
    "IndexedDocument",
    "IndexMetadata",
    "SearchResult",
    "DocumentType",
    "DocumentIndexer",
    "CodeIndexer",
    "WebIndexer",
    "MediaIndexer",
    "KnowledgeGraph",
    "UniversalSearch",
]

