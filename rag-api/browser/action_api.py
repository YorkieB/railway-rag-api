"""
Browser Action REST API

FastAPI endpoints for browser actions (click, type, extract).
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel
from .browser_api import _active_sessions
from .actions import ActionExecutor, ActionResult
from .agent_loop import AgentLoop, Plan
from .uncertainty import BrowserUncertaintyChecker, BrowserUncertainResponse
from .safety import SafetyChecker, get_safety_checker

router = APIRouter(prefix="/browser/sessions", tags=["browser-actions"])


def get_safety_checker_dep() -> SafetyChecker:
    """Dependency for safety checker."""
    return get_safety_checker()


# Request/Response Models
class ClickRequest(BaseModel):
    """Request model for click action."""
    selector: str
    verify: bool = True
    timeout: int = 5000


class TypeRequest(BaseModel):
    """Request model for type action."""
    selector: str
    text: str
    clear_first: bool = True
    verify: bool = True
    timeout: int = 5000


class ExtractRequest(BaseModel):
    """Request model for extract action."""
    selector: str
    timeout: int = 5000


class ActionResponse(BaseModel):
    """Response model for actions."""
    success: bool
    message: str
    element_found: bool = False
    verification_passed: bool = False
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    uncertain: bool = False
    uncertain_response: Optional[Dict[str, Any]] = None


# Endpoints
@router.post("/{session_id}/actions/click", response_model=ActionResponse)
async def click_element(
    session_id: str,
    click_data: ClickRequest,
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Click element by selector.
    
    Returns:
        Action result with verification
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active or not session.page:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Create action executor
    executor = ActionExecutor(session.page, safety_checker)
    
    # Check uncertainty
    uncertainty_checker = BrowserUncertaintyChecker()
    
    # Execute action
    result = await executor.click_element(
        selector=click_data.selector,
        verify=click_data.verify,
        timeout=click_data.timeout
    )
    
    # Check for uncertainty
    uncertain = uncertainty_checker.check_element_found(
        element_found=result.element_found,
        selector=click_data.selector
    )
    
    response = ActionResponse(
        success=result.success,
        message=result.message,
        element_found=result.element_found,
        verification_passed=result.verification_passed,
        error=result.error,
        details=result.details,
        uncertain=uncertain is not None,
        uncertain_response=uncertain.__dict__ if uncertain else None
    )
    
    # Log action
    safety_checker.log_action("click", {
        "session_id": session_id,
        "selector": click_data.selector,
        "success": result.success
    })
    
    return response


@router.post("/{session_id}/actions/type", response_model=ActionResponse)
async def type_text(
    session_id: str,
    type_data: TypeRequest,
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Type text into input element.
    
    Returns:
        Action result with verification
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active or not session.page:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Create action executor
    executor = ActionExecutor(session.page, safety_checker)
    
    # Check uncertainty
    uncertainty_checker = BrowserUncertaintyChecker()
    
    # Execute action
    result = await executor.type_text(
        selector=type_data.selector,
        text=type_data.text,
        clear_first=type_data.clear_first,
        verify=type_data.verify,
        timeout=type_data.timeout
    )
    
    # Check for uncertainty
    uncertain = uncertainty_checker.check_element_found(
        element_found=result.element_found,
        selector=type_data.selector
    )
    
    response = ActionResponse(
        success=result.success,
        message=result.message,
        element_found=result.element_found,
        verification_passed=result.verification_passed,
        error=result.error,
        details=result.details,
        uncertain=uncertain is not None,
        uncertain_response=uncertain.__dict__ if uncertain else None
    )
    
    # Log action
    safety_checker.log_action("type", {
        "session_id": session_id,
        "selector": type_data.selector,
        "text_length": len(type_data.text),
        "success": result.success
    })
    
    return response


@router.post("/{session_id}/actions/extract", response_model=ActionResponse)
async def extract_text(
    session_id: str,
    extract_data: ExtractRequest
):
    """
    Extract text from element.
    
    Returns:
        Extracted text in details
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active or not session.page:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Create action executor
    executor = ActionExecutor(session.page)
    
    # Check uncertainty
    uncertainty_checker = BrowserUncertaintyChecker()
    
    # Execute action
    result = await executor.extract_text(
        selector=extract_data.selector,
        timeout=extract_data.timeout
    )
    
    # Check for uncertainty
    uncertain = uncertainty_checker.check_element_found(
        element_found=result.element_found,
        selector=extract_data.selector
    )
    
    response = ActionResponse(
        success=result.success,
        message=result.message,
        element_found=result.element_found,
        verification_passed=result.verification_passed,
        error=result.error,
        details=result.details,
        uncertain=uncertain is not None,
        uncertain_response=uncertain.__dict__ if uncertain else None
    )
    
    return response


@router.post("/{session_id}/actions/plan", response_model=Dict[str, Any])
async def execute_plan(
    session_id: str,
    plan_data: Dict[str, Any],
    safety_checker: SafetyChecker = Depends(get_safety_checker_dep)
):
    """
    Execute action plan with Plan-Act-Verify-Recover pattern.
    
    Request:
        {
            "action": "click",
            "target": "button#submit",
            "expected_outcome": "Form submitted",
            "max_retries": 3
        }
    
    Returns:
        Execution result with history
    """
    session = _active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    if not session.is_active or not session.page:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Create plan
    plan = Plan(
        action=plan_data.get("action"),
        target=plan_data.get("target"),
        expected_outcome=plan_data.get("expected_outcome", ""),
        max_retries=plan_data.get("max_retries", 3)
    )
    
    # Create agent loop
    executor = ActionExecutor(session.page, safety_checker)
    uncertainty_checker = BrowserUncertaintyChecker()
    agent_loop = AgentLoop(executor, uncertainty_checker)
    
    # Execute plan
    step = await agent_loop.execute_plan(plan)
    
    # Get history
    history = agent_loop.get_history()
    
    return {
        "success": step.result.success if step.result else False,
        "attempts": step.attempts,
        "recovered": step.recovered,
        "result": {
            "success": step.result.success if step.result else False,
            "message": step.result.message if step.result else "No result",
            "error": step.result.error if step.result else None
        },
        "history": history
    }

