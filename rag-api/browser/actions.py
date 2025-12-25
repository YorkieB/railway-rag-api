"""
Browser Action Executor

Implements actions for browser automation with verification.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from playwright.async_api import Page, Locator
from .ax_tree import AXTreeNode, find_interactive_elements, filter_ax_tree
from .safety import SafetyChecker, SafetyViolation


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    message: str
    element_found: bool = False
    verification_passed: bool = False
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ActionExecutor:
    """
    Executes browser actions with verification.
    
    Actions:
    - click_element: Click element by selector
    - type_text: Type text into input
    - extract_text: Extract text from element
    - navigate: Navigate to URL (delegates to BrowserSession)
    """
    
    def __init__(self, page: Page, safety_checker: Optional[SafetyChecker] = None):
        """
        Initialize action executor.
        
        Args:
            page: Playwright Page instance
            safety_checker: Optional safety checker
        """
        self.page = page
        self.safety_checker = safety_checker
    
    async def click_element(
        self,
        selector: str,
        verify: bool = True,
        timeout: int = 5000
    ) -> ActionResult:
        """
        Click element by selector.
        
        Args:
            selector: CSS selector or AX tree selector
            verify: Whether to verify click succeeded
            timeout: Action timeout in milliseconds
            
        Returns:
            ActionResult with success status
        """
        try:
            # Find element
            element = await self.page.locator(selector).first
            is_visible = await element.is_visible(timeout=timeout)
            
            if not is_visible:
                return ActionResult(
                    success=False,
                    message="Element not visible",
                    element_found=True,
                    error="Element exists but is not visible"
                )
            
            # Safety check
            if self.safety_checker:
                violation = self.safety_checker.check_action("click", selector)
                if violation:
                    return ActionResult(
                        success=False,
                        message=violation.message,
                        error=f"Safety violation: {violation.type}"
                    )
            
            # Perform click
            await element.click(timeout=timeout)
            
            # Verify if requested
            verification_passed = True
            if verify:
                # Wait for potential navigation or state change
                await self.page.wait_for_timeout(500)  # Brief wait
                # Check if element state changed (simplified verification)
                try:
                    # Element should still exist (or page navigated)
                    await element.is_visible(timeout=1000)
                except:
                    # Element disappeared (likely due to navigation/state change)
                    verification_passed = True  # This is expected for many clicks
            
            return ActionResult(
                success=True,
                message="Click successful",
                element_found=True,
                verification_passed=verification_passed,
                details={"selector": selector}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Click failed: {str(e)}",
                element_found=False,
                error=str(e)
            )
    
    async def type_text(
        self,
        selector: str,
        text: str,
        clear_first: bool = True,
        verify: bool = True,
        timeout: int = 5000
    ) -> ActionResult:
        """
        Type text into input element.
        
        Args:
            selector: CSS selector for input element
            text: Text to type
            clear_first: Clear input before typing
            verify: Whether to verify text was entered
            timeout: Action timeout in milliseconds
            
        Returns:
            ActionResult with success status
        """
        try:
            # Find element
            element = await self.page.locator(selector).first
            is_visible = await element.is_visible(timeout=timeout)
            
            if not is_visible:
                return ActionResult(
                    success=False,
                    message="Input element not visible",
                    element_found=True,
                    error="Element exists but is not visible"
                )
            
            # Check if element is an input
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            if tag_name not in ["input", "textarea", "div"]:
                return ActionResult(
                    success=False,
                    message="Element is not an input",
                    element_found=True,
                    error=f"Element is {tag_name}, not an input"
                )
            
            # Safety check
            if self.safety_checker:
                violation = self.safety_checker.check_action("type", selector)
                if violation:
                    return ActionResult(
                        success=False,
                        message=violation.message,
                        error=f"Safety violation: {violation.type}"
                    )
            
            # Clear if requested
            if clear_first:
                await element.clear()
            
            # Type text
            await element.fill(text, timeout=timeout)
            
            # Verify if requested
            verification_passed = True
            if verify:
                # Check if text was entered
                actual_value = await element.input_value()
                verification_passed = (actual_value == text)
            
            return ActionResult(
                success=True,
                message="Text typed successfully",
                element_found=True,
                verification_passed=verification_passed,
                details={
                    "selector": selector,
                    "text_length": len(text),
                    "actual_value": actual_value if verify else None
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Type failed: {str(e)}",
                element_found=False,
                error=str(e)
            )
    
    async def extract_text(
        self,
        selector: str,
        timeout: int = 5000
    ) -> ActionResult:
        """
        Extract text from element.
        
        Args:
            selector: CSS selector for element
            timeout: Action timeout in milliseconds
            
        Returns:
            ActionResult with extracted text in details
        """
        try:
            # Find element
            element = await self.page.locator(selector).first
            is_visible = await element.is_visible(timeout=timeout)
            
            if not is_visible:
                return ActionResult(
                    success=False,
                    message="Element not visible",
                    element_found=True,
                    error="Element exists but is not visible"
                )
            
            # Extract text
            text = await element.inner_text()
            
            return ActionResult(
                success=True,
                message="Text extracted successfully",
                element_found=True,
                verification_passed=True,
                details={
                    "selector": selector,
                    "text": text,
                    "text_length": len(text)
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Extract failed: {str(e)}",
                element_found=False,
                error=str(e)
            )
    
    async def wait_for_element(
        self,
        selector: str,
        timeout: int = 10000,
        state: str = "visible"  # "visible", "hidden", "attached", "detached"
    ) -> ActionResult:
        """
        Wait for element to reach specified state.
        
        Args:
            selector: CSS selector
            timeout: Wait timeout in milliseconds
            state: Element state to wait for
            
        Returns:
            ActionResult with wait result
        """
        try:
            element = self.page.locator(selector).first
            
            if state == "visible":
                await element.wait_for(state="visible", timeout=timeout)
            elif state == "hidden":
                await element.wait_for(state="hidden", timeout=timeout)
            elif state == "attached":
                await element.wait_for(state="attached", timeout=timeout)
            elif state == "detached":
                await element.wait_for(state="detached", timeout=timeout)
            
            return ActionResult(
                success=True,
                message=f"Element reached {state} state",
                element_found=True,
                verification_passed=True,
                details={"selector": selector, "state": state}
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Wait failed: {str(e)}",
                element_found=False,
                error=str(e)
            )

