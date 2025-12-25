"""
Indexing REST API Router
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .universal_search import UniversalSearch
from .models import SearchResult, DocumentType

router = APIRouter(prefix="/indexing", tags=["indexing"])

# Initialize universal search (singleton)
_universal_search: Optional[UniversalSearch] = None

def get_universal_search() -> UniversalSearch:
    """Get universal search instance."""
    global _universal_search
    if _universal_search is None:
        _universal_search = UniversalSearch()
    return _universal_search

# Request/Response Models
class IndexRequest(BaseModel):
    file_path: str
    doc_type: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    doc_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int

# Endpoints
@router.post("/index")
async def index_document(request: IndexRequest, search: UniversalSearch = Depends(get_universal_search)):
    """Index a document."""
    try:
        document = await search.index_document(request.file_path, request.doc_type)
        return {
            "document_id": document.id,
            "title": document.metadata.title,
            "type": document.metadata.document_type.value,
            "chunks_count": len(document.chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index/upload")
async def index_uploaded_file(
    file: UploadFile = File(...),
    search: UniversalSearch = Depends(get_universal_search)
):
    """Index an uploaded file."""
    import tempfile
    import os
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Index the file
        document = await search.index_document(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            "document_id": document.id,
            "title": document.metadata.title,
            "type": document.metadata.document_type.value,
            "chunks_count": len(document.chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, search: UniversalSearch = Depends(get_universal_search)):
    """Search across all indexed content."""
    try:
        doc_types = [DocumentType(dt) for dt in request.doc_types] if request.doc_types else None
        results = await search.search(
            query=request.query,
            limit=request.limit,
            doc_types=doc_types,
            filters=request.filters
        )
        
        return SearchResponse(
            results=[
                {
                    "document_id": r.document_id,
                    "document_type": r.document_type.value,
                    "title": r.title,
                    "snippet": r.snippet,
                    "relevance_score": r.relevance_score,
                    "source": r.source,
                    "metadata": r.metadata
                }
                for r in results
            ],
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-graph/search")
async def search_knowledge_graph(
    query: str,
    limit: int = 10,
    search: UniversalSearch = Depends(get_universal_search)
):
    """Search knowledge graph."""
    try:
        results = await search.search_knowledge_graph(query, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-graph")
async def get_knowledge_graph(search: UniversalSearch = Depends(get_universal_search)):
    """Get full knowledge graph."""
    try:
        graph = search.get_knowledge_graph()
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

