"""
Plan-Act-Verify-Recover Pattern

Implements the agent loop for browser automation with verification and recovery.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from .actions import ActionExecutor, ActionResult
from .ax_tree import AXTreeNode, extract_ax_tree, find_interactive_elements
from .uncertainty import BrowserUncertaintyChecker, BrowserUncertainResponse


@dataclass
class Plan:
    """Represents an action plan."""
    action: str  # "click", "type", "extract", "navigate"
    target: str  # Selector or URL
    expected_outcome: str  # Description of expected result
    verification: Optional[Callable] = None  # Custom verification function
    max_retries: int = 3


@dataclass
class AgentStep:
    """Represents a step in the agent loop."""
    plan: Plan
    result: Optional[ActionResult] = None
    attempts: int = 0
    recovered: bool = False


class AgentLoop:
    """
    Plan-Act-Verify-Recover agent loop for browser automation.
    
    Pattern:
    1. Plan: Define action and expected outcome
    2. Act: Execute action
    3. Verify: Check if outcome matches expectation
    4. Recover: Retry or adjust if verification fails
    """
    
    def __init__(
        self,
        action_executor: ActionExecutor,
        uncertainty_checker: Optional[BrowserUncertaintyChecker] = None
    ):
        """
        Initialize agent loop.
        
        Args:
            action_executor: ActionExecutor instance
            uncertainty_checker: Optional uncertainty checker
        """
        self.action_executor = action_executor
        self.uncertainty_checker = uncertainty_checker
        self.steps: List[AgentStep] = []
    
    async def execute_plan(self, plan: Plan) -> AgentStep:
        """
        Execute a plan with verification and recovery.
        
        Args:
            plan: Action plan to execute
            
        Returns:
            AgentStep with result
        """
        step = AgentStep(plan=plan)
        self.steps.append(step)
        
        # Retry loop
        for attempt in range(plan.max_retries):
            step.attempts = attempt + 1
            
            # Act: Execute action
            result = await self._act(plan)
            step.result = result
            
            if not result.success:
                # Recovery: Try to recover
                recovered = await self._recover(plan, result, attempt)
                if recovered:
                    step.recovered = True
                    continue
                else:
                    # Failed after recovery attempts
                    break
            
            # Verify: Check outcome
            verification_passed = await self._verify(plan, result)
            if verification_passed:
                # Success
                return step
            else:
                # Verification failed, try recovery
                recovered = await self._recover(plan, result, attempt)
                if recovered:
                    step.recovered = True
                    continue
                else:
                    # Failed verification, retry
                    continue
        
        # All attempts exhausted
        return step
    
    async def _act(self, plan: Plan) -> ActionResult:
        """Execute action based on plan."""
        if plan.action == "click":
            return await self.action_executor.click_element(
                selector=plan.target,
                verify=False  # Verification done separately
            )
        elif plan.action == "type":
            # Extract text from plan if it's in target format "selector:text"
            parts = plan.target.split(":", 1)
            if len(parts) == 2:
                selector, text = parts
            else:
                return ActionResult(
                    success=False,
                    message="Invalid type target format. Expected 'selector:text'",
                    error="Invalid format"
                )
            
            return await self.action_executor.type_text(
                selector=selector,
                text=text,
                verify=False
            )
        elif plan.action == "extract":
            return await self.action_executor.extract_text(selector=plan.target)
        elif plan.action == "navigate":
            # Navigation is handled by BrowserSession
            return ActionResult(
                success=False,
                message="Navigate should be handled by BrowserSession",
                error="Use BrowserSession.navigate() for navigation"
            )
        else:
            return ActionResult(
                success=False,
                message=f"Unknown action: {plan.action}",
                error="Unknown action"
            )
    
    async def _verify(self, plan: Plan, result: ActionResult) -> bool:
        """Verify that action outcome matches expected result."""
        # If custom verification function provided, use it
        if plan.verification:
            try:
                return await plan.verification(result)
            except:
                return False
        
        # Default verification: check if action succeeded
        if not result.success:
            return False
        
        # Check if verification passed (if action executor did verification)
        if hasattr(result, 'verification_passed'):
            return result.verification_passed
        
        # Basic success check
        return result.success
    
    async def _recover(self, plan: Plan, result: ActionResult, attempt: int) -> bool:
        """
        Attempt to recover from failed action.
        
        Args:
            plan: Original plan
            result: Failed result
            attempt: Current attempt number
            
        Returns:
            True if recovery successful, False otherwise
        """
        # Recovery strategies based on error type
        
        # Element not found - try alternative selectors
        if "not found" in result.error.lower() or not result.element_found:
            # Could try alternative selectors here
            # For now, return False (no recovery)
            return False
        
        # Element not visible - wait and retry
        if "not visible" in result.error.lower():
            # Wait for element to become visible
            wait_result = await self.action_executor.wait_for_element(
                selector=plan.target,
                timeout=5000,
                state="visible"
            )
            return wait_result.success
        
        # Timeout - retry with longer timeout
        if "timeout" in result.error.lower():
            # Could retry with longer timeout
            return False
        
        # Default: no recovery
        return False
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return [
            {
                "action": step.plan.action,
                "target": step.plan.target,
                "attempts": step.attempts,
                "success": step.result.success if step.result else False,
                "recovered": step.recovered,
                "error": step.result.error if step.result else None
            }
            for step in self.steps
        ]

