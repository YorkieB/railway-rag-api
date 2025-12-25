"""
Safety Guardrails for Browser Automation

Implements safety checks to prevent dangerous or unauthorized actions.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import re


@dataclass
class SafetyViolation:
    """Represents a safety violation."""
    type: str  # "blocked_domain", "payment_detected", "sensitive_site", etc.
    message: str
    severity: str  # "error", "warning"
    url: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SafetyChecker:
    """
    Safety checker for browser automation.
    
    Implements:
    - Domain blocklist (banking, password managers)
    - Payment detection
    - Sensitive site detection
    - Action logging
    """
    
    def __init__(
        self,
        blocked_domains: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        enable_payment_detection: bool = True
    ):
        """
        Initialize safety checker.
        
        Args:
            blocked_domains: List of blocked domain patterns
            allowed_domains: List of allowed domains (whitelist mode)
            enable_payment_detection: Enable payment detection
        """
        # Default blocked domains (banking, password managers, etc.)
        self.default_blocked = [
            r".*\.bank$",
            r".*\.com/banking",
            r".*password.*manager",
            r".*1password\.com",
            r".*lastpass\.com",
            r".*bitwarden\.com",
            r".*dashlane\.com",
            r".*paypal\.com",
            r".*stripe\.com",
            r".*checkout",
            r".*payment",
        ]
        
        self.blocked_domains = (blocked_domains or []) + self.default_blocked
        self.allowed_domains = allowed_domains or []
        self.enable_payment_detection = enable_payment_detection
        
        # Payment keywords
        self.payment_keywords = [
            "credit card", "debit card", "card number", "cvv", "cvc",
            "expiry", "expiration", "billing", "payment", "checkout",
            "pay now", "purchase", "buy now", "add to cart"
        ]
    
    def check_url(self, url: str) -> Optional[SafetyViolation]:
        """
        Check if URL is safe to navigate to.
        
        Args:
            url: URL to check
            
        Returns:
            SafetyViolation if unsafe, None otherwise
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        full_url = url.lower()
        
        # Check whitelist (if enabled)
        if self.allowed_domains:
            is_allowed = any(
                re.match(pattern, domain) or domain.endswith(pattern)
                for pattern in self.allowed_domains
            )
            if not is_allowed:
                return SafetyViolation(
                    type="not_allowed",
                    message=f"Domain {domain} is not in allowed list",
                    severity="error",
                    url=url
                )
        
        # Check blocklist
        for pattern in self.blocked_domains:
            if re.search(pattern, domain) or re.search(pattern, path) or re.search(pattern, full_url):
                return SafetyViolation(
                    type="blocked_domain",
                    message=f"Domain {domain} is blocked (matches pattern: {pattern})",
                    severity="error",
                    url=url
                )
        
        # Check for sensitive patterns
        sensitive_patterns = [
            r"/login",
            r"/signin",
            r"/account",
            r"/settings",
            r"/admin"
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, path):
                return SafetyViolation(
                    type="sensitive_site",
                    message=f"URL contains sensitive path: {path}",
                    severity="warning",
                    url=url
                )
        
        return None
    
    def check_payment(self, page_content: Optional[str] = None, url: Optional[str] = None) -> Optional[SafetyViolation]:
        """
        Check if page contains payment-related content.
        
        Args:
            page_content: Page HTML/text content
            url: Page URL
            
        Returns:
            SafetyViolation if payment detected, None otherwise
        """
        if not self.enable_payment_detection:
            return None
        
        # Check URL
        if url:
            url_lower = url.lower()
            for keyword in self.payment_keywords:
                if keyword in url_lower:
                    return SafetyViolation(
                        type="payment_detected",
                        message=f"Payment-related content detected in URL: {keyword}",
                        severity="error",
                        url=url
                    )
        
        # Check content
        if page_content:
            content_lower = page_content.lower()
            for keyword in self.payment_keywords:
                if keyword in content_lower:
                    return SafetyViolation(
                        type="payment_detected",
                        message=f"Payment-related content detected: {keyword}",
                        severity="error",
                        details={"keyword": keyword}
                    )
        
        return None
    
    def check_action(self, action: str, target: Optional[str] = None) -> Optional[SafetyViolation]:
        """
        Check if action is safe to perform.
        
        Args:
            action: Action type ("click", "type", "navigate", etc.)
            target: Target element or URL
            
        Returns:
            SafetyViolation if unsafe, None otherwise
        """
        # Block dangerous actions
        dangerous_actions = ["download", "file_upload"]
        
        if action in dangerous_actions:
            return SafetyViolation(
                type="dangerous_action",
                message=f"Action '{action}' is not allowed",
                severity="error",
                details={"action": action}
            )
        
        # Check target if provided
        if target and action == "navigate":
            return self.check_url(target)
        
        return None
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """
        Log action for audit trail.
        
        Args:
            action: Action type
            details: Action details
        """
        # In production, write to database or log file
        print(f"[SAFETY LOG] Action: {action}, Details: {details}")


# Global safety checker instance
_default_checker = SafetyChecker()


def get_safety_checker() -> SafetyChecker:
    """Get default safety checker instance."""
    return _default_checker

