"""
Browser Automation REST API

FastAPI endpoints for browser automation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from .browser_session import BrowserSession
from .ax_tree import extract_ax_tree, AXTreeNode, filter_ax_tree, find_interactive_elements
from .safety import SafetyChecker, SafetyViolation, get_safety_checker
import asyncio

router = APIRouter(prefix="/browser", tags=["browser"])

# Session storage (in-memory for now, can be extended to database)
_active_sessions: Dict[str, BrowserSession] = {}


def get_safety_checker_dep() -> SafetyChecker:
    """Dependency for safety checker."""
    return get_safety_checker()


# Request/Response Models
class BrowserSessionCreate(BaseModel):
    """Request model for creating a browser session."""
    headless: bool = True
    browser_type: str = "chromium"  # "chromium", "firefox", "webkit"


class BrowserSessionResponse(BaseModel):
    """Response model for browser session."""
    session_id: str
    is_active: bool
    current_url: Optional[str] = None
    title: Optional[str] = None


class NavigateRequest(BaseModel):
    """Request model for navigation."""
    url: str
    wait_until: str = "networkidle"  # "load", "domcontentloaded", "networkidle", "commit"
    timeout: int = 30000


class NavigateResponse(BaseModel):
    """Response model for navigation."""
    success: bool
    url: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    error: Optional[str] = None
    safety_violation: Optional[Dict[str, Any]] = None


class AXTreeResponse(BaseModel):
    """Response model for AX tree."""
    session_id: str
    tree: Dict[str, Any]
    interactive_elements: List[Dict[str, Any]]


# Endpoints
@router.post("/sessions", response_model=BrowserSessionResponse, status_code=201)
async def create_session(
    session_data: BrowserSessionCreate,
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Create a new browser session.
    
    Returns:
        Created session information
    """
    session = BrowserSession(
        headless=session_data.headless,
        browser_type=session_data.browser_type
    )
    
    # Start session
    await session.start()
    
    # Store session
    _active_sessions[session.session_id] = session
    
    # Log action
    safety_checker.log_action("create_session", {
        "session_id": session.session_id,
        "browser_type": session_data.browser_type,
        "headless": session_data.headless
    })
    
    return BrowserSessionResponse(
        session_id=session.session_id,
        is_active=session.is_active,
        current_url=session.current_url,
        title=session.title
    )


@router.get("/sessions/{session_id}", response_model=BrowserSessionResponse)
async def get_session(session_id: str):
    """
    Get browser session status.
    
    Returns:
        Session information
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    page_info = await session.get_page_info()
    
    return BrowserSessionResponse(
        session_id=session.session_id,
        is_active=session.is_active,
        current_url=page_info.get("url"),
        title=page_info.get("title")
    )


@router.post("/sessions/{session_id}/navigate", response_model=NavigateResponse)
async def navigate(
    session_id: str,
    navigate_data: NavigateRequest,
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Navigate to URL.
    
    Returns:
        Navigation result with safety check
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Safety check
    violation = safety_checker.check_action("navigate", navigate_data.url)
    if violation:
        safety_checker.log_action("navigate_blocked", {
            "session_id": session_id,
            "url": navigate_data.url,
            "violation": violation.type,
            "message": violation.message
        })
        
        return NavigateResponse(
            success=False,
            error=violation.message,
            safety_violation={
                "type": violation.type,
                "severity": violation.severity,
                "message": violation.message
            }
        )
    
    # Perform navigation
    result = await session.navigate(
        url=navigate_data.url,
        wait_until=navigate_data.wait_until,
        timeout=navigate_data.timeout
    )
    
    # Check for payment content after navigation
    if result.get("success"):
        page_content = None
        if session.page:
            try:
                page_content = await session.page.content()
            except:
                pass
        
        payment_violation = safety_checker.check_payment(
            page_content=page_content,
            url=result.get("url")
        )
        
        if payment_violation:
            result["safety_violation"] = {
                "type": payment_violation.type,
                "severity": payment_violation.severity,
                "message": payment_violation.message
            }
    
    # Log action
    safety_checker.log_action("navigate", {
        "session_id": session_id,
        "url": navigate_data.url,
        "success": result.get("success", False)
    })
    
    return NavigateResponse(**result)


@router.get("/sessions/{session_id}/ax-tree", response_model=AXTreeResponse)
async def get_ax_tree(
    session_id: str,
    include_hidden: bool = Query(False, description="Include hidden elements")
):
    """
    Get accessibility tree for current page.
    
    Returns:
        AX tree and interactive elements
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get AX tree snapshot
    snapshot = await session.get_ax_tree()
    
    # Extract structured tree
    root = extract_ax_tree(snapshot, include_hidden=include_hidden)
    
    # Find interactive elements
    interactive = find_interactive_elements(root) if root else []
    
    return AXTreeResponse(
        session_id=session_id,
        tree=root.to_dict() if root else {},
        interactive_elements=[node.to_dict() for node in interactive]
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def close_session(
    session_id: str,
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Close browser session.
    
    Returns:
        204 No Content on success
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    # Close session
    await session.close()
    
    # Remove from storage
    del _active_sessions[session_id]
    
    # Log action
    safety_checker.log_action("close_session", {
        "session_id": session_id
    })
    
    return None


@router.get("/sessions", response_model=List[BrowserSessionResponse])
async def list_sessions():
    """
    List all active browser sessions.
    
    Returns:
        List of active sessions
    """
    sessions = []
    for session_id, session in _active_sessions.items():
        page_info = await session.get_page_info()
        sessions.append(BrowserSessionResponse(
            session_id=session.session_id,
            is_active=session.is_active,
            current_url=page_info.get("url"),
            title=page_info.get("title")
        ))
    
    return sessions

