"""
Browser Safety Guardrails
Implements domain blocklists, allow/deny lists, and action restrictions.
"""
from typing import List, Optional, Dict
from urllib.parse import urlparse
from datetime import datetime


# Default domain blocklist (banking, password managers, system tools)
DEFAULT_BLOCKLIST = [
    "bankofamerica.com",
    "chase.com",
    "wellsfargo.com",
    "citi.com",
    "usbank.com",
    "1password.com",
    "lastpass.com",
    "bitwarden.com",
    "dashlane.com",
    "keeper.security",
    "roboform.com"
]

# Default allowlist (empty = allow all except blocklist)
DEFAULT_ALLOWLIST: List[str] = []


class BrowserSafety:
    """
    Manages browser safety rules and domain restrictions.
    """
    
    def __init__(
        self,
        blocklist: Optional[List[str]] = None,
        allowlist: Optional[List[str]] = None
    ):
        self.blocklist = blocklist or DEFAULT_BLOCKLIST.copy()
        self.allowlist = allowlist or DEFAULT_ALLOWLIST.copy()
    
    def check_domain(self, url: str) -> Dict:
        """
        Check if domain is allowed for navigation.
        
        Args:
            url: URL to check
            
        Returns:
            Dict with "allowed" bool and "reason" string
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]
            
            # Remove www. prefix for comparison
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check blocklist first
            for blocked in self.blocklist:
                if blocked.lower() in domain:
                    return {
                        "allowed": False,
                        "reason": f"Domain '{domain}' is in blocklist (category: {blocked})"
                    }
            
            # Check allowlist if not empty
            if self.allowlist:
                allowed = False
                for allowed_domain in self.allowlist:
                    if allowed_domain.lower() in domain:
                        allowed = True
                        break
                
                if not allowed:
                    return {
                        "allowed": False,
                        "reason": f"Domain '{domain}' is not in allowlist"
                    }
            
            return {
                "allowed": True,
                "reason": "Domain allowed"
            }
            
        except Exception as e:
            return {
                "allowed": False,
                "reason": f"Error parsing URL: {str(e)}"
            }
    
    def is_payment_action(self, action: str, element: Dict) -> bool:
        """
        Check if action involves payment (BC4: blocked).
        
        Args:
            action: Action type ("click", "type", etc.)
            element: AX tree element data
            
        Returns:
            True if action involves payment
        """
        # Check element name/role for payment indicators
        name = element.get("name", "").lower()
        role = element.get("role", "").lower()
        
        payment_keywords = [
            "pay", "payment", "checkout", "purchase", "buy now",
            "add to cart", "credit card", "billing", "subscribe"
        ]
        
        if any(keyword in name for keyword in payment_keywords):
            return True
        
        if role in ["button"] and any(keyword in name for keyword in ["pay", "checkout", "buy"]):
            return True
        
        return False
    
    def is_login_action(self, action: str, element: Dict) -> bool:
        """
        Check if action involves login/2FA (BC4: blocked).
        
        Args:
            action: Action type
            element: AX tree element data
            
        Returns:
            True if action involves login
        """
        name = element.get("name", "").lower()
        role = element.get("role", "").lower()
        
        login_keywords = [
            "login", "sign in", "password", "username", "email",
            "authenticate", "2fa", "two factor", "verify"
        ]
        
        if any(keyword in name for keyword in login_keywords):
            return True
        
        if role == "textbox" and ("password" in name or "login" in name):
            return True
        
        return False
    
    def log_action(self, action: str, details: Dict) -> Dict:
        """
        Log browser action for audit trail.
        
        Args:
            action: Action type ("navigate", "click", "type", etc.)
            details: Action details (url, element, etc.)
            
        Returns:
            Log entry dict
        """
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "session_id": details.get("session_id", "unknown")
        }


# Global safety instance
browser_safety = BrowserSafety()

