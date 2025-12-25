"""
Universal Search

Provides unified search across all indexed content.
"""

from typing import List, Optional, Dict, Any
import os
import chromadb
from chromadb.config import Settings

from .models import SearchResult, IndexedDocument, DocumentType
from .document_indexer import DocumentIndexer
from .code_indexer import CodeIndexer
from .web_indexer import WebIndexer
from .media_indexer import MediaIndexer
from .knowledge_graph import KnowledgeGraph


class UniversalSearch:
    """Universal search across all indexed content."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize universal search.
        
        Args:
            db_path: Path to ChromaDB storage
        """
        self.db_path = db_path or os.getenv("CHROMADB_INDEX_DIR", "./index_db")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(
            name="universal_index",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize indexers
        self.document_indexer = DocumentIndexer()
        self.code_indexer = CodeIndexer()
        self.web_indexer = WebIndexer()
        self.media_indexer = MediaIndexer()
        
        # Knowledge graph
        self.knowledge_graph = KnowledgeGraph()
    
    async def index_document(self, file_path: str, doc_type: Optional[str] = None) -> IndexedDocument:
        """
        Index a document and add to search index.
        
        Args:
            file_path: Path to document
            doc_type: Optional document type override
        
        Returns:
            IndexedDocument
        """
        # Determine indexer based on file type
        if doc_type == "code" or file_path.endswith((".py", ".js", ".ts", ".java", ".cpp", ".go")):
            document = await self.code_indexer.index_file(file_path)
        elif file_path.startswith("http://") or file_path.startswith("https://"):
            document = await self.web_indexer.index_url(file_path)
        elif file_path.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            document = await self.media_indexer.index_image(file_path)
        elif file_path.endswith((".mp3", ".wav", ".flac", ".ogg")):
            document = await self.media_indexer.index_audio(file_path)
        elif file_path.endswith((".mp4", ".avi", ".mov", ".mkv")):
            document = await self.media_indexer.index_video(file_path)
        else:
            document = await self.document_indexer.index_file(file_path)
        
        # Add to ChromaDB
        await self._add_to_index(document)
        
        # Add to knowledge graph
        self.knowledge_graph.add_document(document)
        
        return document
    
    async def _add_to_index(self, document: IndexedDocument):
        """Add document to ChromaDB index."""
        # Generate embeddings for chunks (simplified - in production use OpenAI embeddings)
        # For now, store chunks as-is
        ids = [f"{document.id}_chunk_{i}" for i in range(len(document.chunks))]
        documents = document.chunks
        metadatas = [
            {
                "document_id": document.id,
                "document_type": document.metadata.document_type.value,
                "source": document.metadata.source,
                "title": document.metadata.title or "",
                "chunk_index": i
            }
            for i in range(len(document.chunks))
        ]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        doc_types: Optional[List[DocumentType]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search across all indexed content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            doc_types: Optional filter by document types
            filters: Additional metadata filters
        
        Returns:
            List of SearchResult
        """
        # Build where clause for filters
        where = {}
        if doc_types:
            where["document_type"] = {"$in": [dt.value for dt in doc_types]}
        if filters:
            where.update(filters)
        
        # Search ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where if where else None
        )
        
        # Convert to SearchResult objects
        search_results = []
        
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                document = results["documents"][0][i] if results["documents"] else ""
                distance = results["distances"][0][i] if "distances" in results and results["distances"] else 0.5
                
                relevance_score = max(0.0, 1.0 - distance)
                
                search_results.append(SearchResult(
                    document_id=metadata.get("document_id", doc_id),
                    document_type=DocumentType(metadata.get("document_type", "unknown")),
                    title=metadata.get("title", ""),
                    snippet=document[:200] + "..." if len(document) > 200 else document,
                    relevance_score=relevance_score,
                    source=metadata.get("source", ""),
                    metadata=metadata
                ))
        
        return search_results
    
    async def search_knowledge_graph(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge graph for related concepts.
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of related nodes and edges
        """
        # Find nodes matching query
        matching_nodes = []
        query_lower = query.lower()
        
        for node in self.knowledge_graph.nodes.values():
            if query_lower in node.label.lower() or any(query_lower in str(v).lower() for v in node.properties.values()):
                matching_nodes.append(node)
        
        # Get neighbors of matching nodes
        results = []
        for node in matching_nodes[:limit]:
            neighbors = self.knowledge_graph.get_neighbors(node.id)
            results.append({
                "node": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type,
                    "properties": node.properties
                },
                "neighbors": [
                    {
                        "id": n.id,
                        "label": n.label,
                        "type": n.node_type
                    }
                    for n in neighbors[:5]
                ]
            })
        
        return results
    
    def get_knowledge_graph(self) -> Dict:
        """Get full knowledge graph representation."""
        return self.knowledge_graph.to_dict()

