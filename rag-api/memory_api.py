"""
Memory API Endpoints

REST API endpoints for memory CRUD operations and search.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime

from .models import (
    MemoryItem,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    MemorySearchRequest,
    MemoryListResponse,
    MemorySearchResponse
)
from .memory_storage import MemoryStorage, ChromaDBMemoryStorage


# Initialize router
router = APIRouter(prefix="/memory", tags=["memory"])

# Initialize storage (singleton pattern)
_storage: Optional[MemoryStorage] = None


def get_storage() -> MemoryStorage:
    """
    Get memory storage instance (singleton).
    
    Returns:
        MemoryStorage instance
    """
    global _storage
    if _storage is None:
        _storage = ChromaDBMemoryStorage()
    return _storage


@router.post("", response_model=MemoryItem, status_code=201)
async def create_memory(
    request: MemoryCreateRequest,
    private_session: bool = False,
    storage: MemoryStorage = Depends(get_storage)
) -> MemoryItem:
    """
    Create a new memory item.
    
    Args:
        request: Memory creation request
        private_session: If True, memory creation is blocked (privacy)
        storage: Memory storage instance
        
    Returns:
        Created memory item
        
    Raises:
        HTTPException: 403 if private session, 400 if validation fails
    """
    # Respect private session flag (no writes allowed)
    if private_session:
        raise HTTPException(
            status_code=403,
            detail="Memory creation not allowed in private session"
        )
    
    # Create memory item
    memory = MemoryItem(
        user_id=request.user_id,
        project_id=request.project_id,
        content=request.content,
        memory_type=request.memory_type
    )
    
    # Store in database
    created = storage.create(memory)
    return created


@router.get("", response_model=MemoryListResponse)
async def list_memories(
    user_id: str,
    project_id: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 100,
    storage: MemoryStorage = Depends(get_storage)
) -> MemoryListResponse:
    """
    List memory items for a user.
    
    Args:
        user_id: User ID (required)
        project_id: Optional project filter
        memory_type: Optional type filter
        limit: Maximum number of items (default: 100, max: 1000)
        storage: Memory storage instance
        
    Returns:
        List of memory items with total count
    """
    # Validate limit
    limit = min(limit, 1000)
    
    # Validate memory_type if provided
    if memory_type and memory_type not in ["fact", "preference", "decision"]:
        raise HTTPException(
            status_code=400,
            detail="memory_type must be one of: fact, preference, decision"
        )
    
    # List memories
    memories = storage.list(
        user_id=user_id,
        project_id=project_id,
        memory_type=memory_type,
        limit=limit
    )
    
    return MemoryListResponse(
        memories=memories,
        total=len(memories)
    )


@router.get("/{memory_id}", response_model=MemoryItem)
async def get_memory(
    memory_id: str,
    user_id: str,
    storage: MemoryStorage = Depends(get_storage)
) -> MemoryItem:
    """
    Get a memory item by ID.
    
    Args:
        memory_id: Memory item ID
        user_id: User ID (for ownership validation)
        storage: Memory storage instance
        
    Returns:
        Memory item
        
    Raises:
        HTTPException: 404 if not found or not owned by user
    """
    memory = storage.get(memory_id, user_id)
    
    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found or access denied"
        )
    
    return memory


@router.put("/{memory_id}", response_model=MemoryItem)
async def update_memory(
    memory_id: str,
    user_id: str,
    request: MemoryUpdateRequest,
    private_session: bool = False,
    storage: MemoryStorage = Depends(get_storage)
) -> MemoryItem:
    """
    Update a memory item.
    
    Args:
        memory_id: Memory item ID
        user_id: User ID (for ownership validation)
        request: Update request with fields to update
        private_session: If True, memory update is blocked (privacy)
        storage: Memory storage instance
        
    Returns:
        Updated memory item
        
    Raises:
        HTTPException: 403 if private session, 404 if not found
    """
    # Respect private session flag (no writes allowed)
    if private_session:
        raise HTTPException(
            status_code=403,
            detail="Memory update not allowed in private session"
        )
    
    # Build updates dict (only include provided fields)
    updates = {}
    if request.content is not None:
        updates["content"] = request.content
    if request.memory_type is not None:
        updates["memory_type"] = request.memory_type
    if request.project_id is not None:
        updates["project_id"] = request.project_id
    
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )
    
    # Update memory
    updated = storage.update(memory_id, user_id, updates)
    
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Memory not found or access denied"
        )
    
    return updated


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: str,
    user_id: str,
    private_session: bool = False,
    storage: MemoryStorage = Depends(get_storage)
):
    """
    Delete a memory item.
    
    Args:
        memory_id: Memory item ID
        user_id: User ID (for ownership validation)
        private_session: If True, memory deletion is blocked (privacy)
        storage: Memory storage instance
        
    Raises:
        HTTPException: 403 if private session, 404 if not found
    """
    # Respect private session flag (no writes allowed)
    if private_session:
        raise HTTPException(
            status_code=403,
            detail="Memory deletion not allowed in private session"
        )
    
    # Delete memory
    deleted = storage.delete(memory_id, user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Memory not found or access denied"
        )


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    storage: MemoryStorage = Depends(get_storage)
) -> MemorySearchResponse:
    """
    Search memories using semantic search.
    
    Args:
        request: Search request with query and filters
        storage: Memory storage instance
        
    Returns:
        List of relevant memory items sorted by relevance
    """
    # Validate memory_type if provided
    if request.memory_type and request.memory_type not in ["fact", "preference", "decision"]:
        raise HTTPException(
            status_code=400,
            detail="memory_type must be one of: fact, preference, decision"
        )
    
    # Search memories
    memories = storage.search(
        user_id=request.user_id,
        query=request.query,
        project_id=request.project_id,
        memory_type=request.memory_type,
        limit=request.limit
    )
    
    return MemorySearchResponse(
        memories=memories,
        query=request.query,
        total=len(memories)
    )

