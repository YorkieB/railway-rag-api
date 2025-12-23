"""
Browser Action Executor
Implements click, type, extract actions with state verification.
"""
from playwright.async_api import Page
from typing import Optional, Dict
from browser.ax_tree import find_element_by_ax, extract_ax_tree
from browser.safety import browser_safety
import base64


class ActionExecutor:
    """
    Executes browser actions with verification.
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    async def click_element(
        self,
        ax_tree: list,
        role: Optional[str] = None,
        name: Optional[str] = None,
        exact_name: bool = False
    ) -> Dict:
        """
        Click element by AX Tree properties.
        
        Args:
            ax_tree: Accessibility tree
            role: Element role (e.g., "button")
            name: Element name
            exact_name: Exact name match
            
        Returns:
            Dict with success status and verification result
        """
        # Find element in AX tree
        element = find_element_by_ax(ax_tree, role=role, name=name, exact_name=exact_name)
        
        if not element:
            return {
                "success": False,
                "uncertain": True,
                "reason": "element_not_found",
                "message": "I couldn't find that element on the page."
            }
        
        # Check safety (no payments, no login)
        if browser_safety.is_payment_action("click", element):
            return {
                "success": False,
                "blocked": True,
                "reason": "payment_action",
                "message": "Payment actions are blocked for safety."
            }
        
        if browser_safety.is_login_action("click", element):
            return {
                "success": False,
                "blocked": True,
                "reason": "login_action",
                "message": "Login/2FA actions are blocked. Please enter credentials manually."
            }
        
        try:
            # Get element by accessible name
            element_name = element.get("name", "")
            
            # Click using Playwright's accessible name locator
            await self.page.get_by_role(element.get("role", "button"), name=element_name).click(timeout=5000)
            
            # Verify state change (screenshot)
            screenshot_before = await self.page.screenshot()
            
            # Wait a bit for state to update
            await self.page.wait_for_timeout(500)
            
            screenshot_after = await self.page.screenshot()
            
            # Simple verification: check if screenshots differ
            verified = screenshot_before != screenshot_after
            
            return {
                "success": True,
                "uncertain": False,
                "element": {
                    "role": element.get("role"),
                    "name": element.get("name")
                },
                "verified": verified
            }
            
        except Exception as e:
            return {
                "success": False,
                "uncertain": False,
                "error": str(e),
                "message": f"Failed to click element: {str(e)}"
            }
    
    async def type_text(
        self,
        ax_tree: list,
        text: str,
        role: Optional[str] = None,
        name: Optional[str] = None
    ) -> Dict:
        """
        Type text into input field.
        
        Args:
            ax_tree: Accessibility tree
            text: Text to type
            role: Element role (e.g., "textbox")
            name: Element name
            
        Returns:
            Dict with success status
        """
        # Find element
        element = find_element_by_ax(ax_tree, role=role or "textbox", name=name)
        
        if not element:
            return {
                "success": False,
                "uncertain": True,
                "reason": "element_not_found",
                "message": "I couldn't find that input field on the page."
            }
        
        # Check safety
        if browser_safety.is_login_action("type", element):
            return {
                "success": False,
                "blocked": True,
                "reason": "login_action",
                "message": "Login fields are blocked. Please enter credentials manually."
            }
        
        try:
            element_name = element.get("name", "")
            await self.page.get_by_role("textbox", name=element_name).fill(text)
            
            # Verify
            value = await self.page.get_by_role("textbox", name=element_name).input_value()
            verified = text in value
            
            return {
                "success": True,
                "uncertain": False,
                "element": {
                    "role": element.get("role"),
                    "name": element.get("name")
                },
                "verified": verified,
                "value": value
            }
            
        except Exception as e:
            return {
                "success": False,
                "uncertain": False,
                "error": str(e),
                "message": f"Failed to type text: {str(e)}"
            }
    
    async def extract_text(
        self,
        ax_tree: list,
        role: Optional[str] = None,
        name: Optional[str] = None
    ) -> Dict:
        """
        Extract text from element.
        
        Args:
            ax_tree: Accessibility tree
            role: Element role
            name: Element name
            
        Returns:
            Dict with extracted text
        """
        element = find_element_by_ax(ax_tree, role=role, name=name)
        
        if not element:
            return {
                "success": False,
                "uncertain": True,
                "reason": "element_not_found",
                "message": "I couldn't find that element on the page."
            }
        
        try:
            element_name = element.get("name", "")
            element_role = element.get("role", "")
            
            # Extract text based on role
            if element_role == "textbox":
                text = await self.page.get_by_role("textbox", name=element_name).input_value()
            else:
                # For other elements, try to get text content
                locator = self.page.get_by_role(element_role, name=element_name)
                text = await locator.text_content()
            
            return {
                "success": True,
                "uncertain": False,
                "element": {
                    "role": element.get("role"),
                    "name": element.get("name")
                },
                "text": text or ""
            }
            
        except Exception as e:
            return {
                "success": False,
                "uncertain": False,
                "error": str(e),
                "message": f"Failed to extract text: {str(e)}"
            }

