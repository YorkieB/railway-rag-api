"""
Uncertainty Protocol for Browser Automation

Handles cases where browser automation cannot proceed with confidence.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .ax_tree import AXTreeNode


@dataclass
class BrowserUncertainResponse:
    """Uncertain response for browser actions."""
    uncertain: bool = True
    message: str = ""
    suggestions: List[str] = None
    reason: str = ""  # "element_not_found", "multiple_matches", "ambiguous", etc.
    details: Optional[Dict[str, Any]] = None


class BrowserUncertaintyChecker:
    """
    Checks for uncertainty in browser automation scenarios.
    
    Uncertainty cases:
    - Element not found
    - Multiple matching elements
    - Ambiguous selectors
    - Page state unclear
    """
    
    def __init__(self):
        """Initialize uncertainty checker."""
        pass
    
    def check_element_found(
        self,
        element_found: bool,
        selector: str
    ) -> Optional[BrowserUncertainResponse]:
        """
        Check if element was found.
        
        Args:
            element_found: Whether element was found
            selector: Selector used
            
        Returns:
            UncertainResponse if uncertain, None otherwise
        """
        if not element_found:
            return BrowserUncertainResponse(
                uncertain=True,
                message=f"Element not found with selector: {selector}",
                suggestions=[
                    "Verify the selector is correct",
                    "Check if element is visible",
                    "Wait for element to load",
                    "Check if page has changed"
                ],
                reason="element_not_found",
                details={"selector": selector}
            )
        
        return None
    
    def check_multiple_matches(
        self,
        match_count: int,
        selector: str
    ) -> Optional[BrowserUncertainResponse]:
        """
        Check if selector matches multiple elements.
        
        Args:
            match_count: Number of matching elements
            selector: Selector used
            
        Returns:
            UncertainResponse if uncertain, None otherwise
        """
        if match_count > 1:
            return BrowserUncertainResponse(
                uncertain=True,
                message=f"Selector matches {match_count} elements: {selector}",
                suggestions=[
                    "Use a more specific selector",
                    "Use index to target specific element",
                    "Use AX tree to find unique identifier"
                ],
                reason="multiple_matches",
                details={"selector": selector, "match_count": match_count}
            )
        
        return None
    
    def check_ambiguous_selector(
        self,
        selector: str,
        ax_tree: Optional[AXTreeNode] = None
    ) -> Optional[BrowserUncertainResponse]:
        """
        Check if selector is ambiguous.
        
        Args:
            selector: Selector to check
            ax_tree: Optional AX tree for context
            
        Returns:
            UncertainResponse if uncertain, None otherwise
        """
        # Check for common ambiguous patterns
        ambiguous_patterns = [
            "button",  # Too generic
            "input",   # Too generic
            "div",     # Too generic
            "[class*=" # Partial class match
        ]
        
        for pattern in ambiguous_patterns:
            if pattern in selector.lower():
                return BrowserUncertainResponse(
                    uncertain=True,
                    message=f"Selector may be ambiguous: {selector}",
                    suggestions=[
                        "Use more specific selector",
                        "Include parent context",
                        "Use AX tree role and name",
                        "Add data-testid or aria-label"
                    ],
                    reason="ambiguous_selector",
                    details={"selector": selector, "pattern": pattern}
                )
        
        return None
    
    def check_page_state(
        self,
        page_loaded: bool,
        expected_elements: List[str]
    ) -> Optional[BrowserUncertainResponse]:
        """
        Check if page is in expected state.
        
        Args:
            page_loaded: Whether page is loaded
            expected_elements: List of selectors for expected elements
            
        Returns:
            UncertainResponse if uncertain, None otherwise
        """
        if not page_loaded:
            return BrowserUncertainResponse(
                uncertain=True,
                message="Page not fully loaded",
                suggestions=[
                    "Wait for page load",
                    "Check network requests",
                    "Verify URL is correct"
                ],
                reason="page_not_loaded"
            )
        
        # Could check for expected elements here
        # For now, just check if page is loaded
        
        return None
    
    def should_return_uncertain(
        self,
        element_found: bool,
        selector: str,
        match_count: int = 1
    ) -> bool:
        """
        Determine if should return uncertain response.
        
        Args:
            element_found: Whether element was found
            selector: Selector used
            match_count: Number of matching elements
            
        Returns:
            True if should return uncertain, False otherwise
        """
        # Check element found
        if not element_found:
            return True
        
        # Check multiple matches
        if match_count > 1:
            return True
        
        # Check ambiguous selector
        uncertain = self.check_ambiguous_selector(selector)
        if uncertain:
            return True
        
        return False
    
    def generate_uncertain_response(
        self,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> BrowserUncertainResponse:
        """
        Generate uncertain response for given reason.
        
        Args:
            reason: Reason for uncertainty
            details: Additional details
            
        Returns:
            BrowserUncertainResponse
        """
        responses = {
            "element_not_found": BrowserUncertainResponse(
                uncertain=True,
                message="Element not found on page",
                suggestions=[
                    "Verify selector is correct",
                    "Check if element is visible",
                    "Wait for element to load"
                ],
                reason="element_not_found",
                details=details
            ),
            "multiple_matches": BrowserUncertainResponse(
                uncertain=True,
                message="Multiple elements match selector",
                suggestions=[
                    "Use more specific selector",
                    "Target element by index",
                    "Use AX tree for unique identifier"
                ],
                reason="multiple_matches",
                details=details
            ),
            "ambiguous_selector": BrowserUncertainResponse(
                uncertain=True,
                message="Selector is too ambiguous",
                suggestions=[
                    "Use more specific selector",
                    "Include parent context",
                    "Use AX tree attributes"
                ],
                reason="ambiguous_selector",
                details=details
            ),
            "page_not_loaded": BrowserUncertainResponse(
                uncertain=True,
                message="Page not in expected state",
                suggestions=[
                    "Wait for page to load",
                    "Check network status",
                    "Verify URL"
                ],
                reason="page_not_loaded",
                details=details
            )
        }
        
        return responses.get(reason, BrowserUncertainResponse(
            uncertain=True,
            message=f"Uncertainty: {reason}",
            suggestions=["Review action and retry"],
            reason=reason,
            details=details
        ))

