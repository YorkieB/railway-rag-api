"""
Browser Session Management

Manages Playwright browser instances and pages for automation.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


class BrowserSession:
    """
    Manages a browser session with Playwright.
    
    Handles:
    - Browser instance lifecycle
    - Page navigation
    - Context management
    - Session state
    """
    
    def __init__(
        self,
        session_id: Optional[str] = None,
        headless: bool = True,
        browser_type: str = "chromium"
    ):
        """
        Initialize browser session.
        
        Args:
            session_id: Optional session ID (generated if not provided)
            headless: Run browser in headless mode
            browser_type: Browser type ("chromium", "firefox", "webkit")
        """
        self.session_id = session_id or str(uuid4())
        self.headless = headless
        self.browser_type = browser_type
        
        # Playwright objects
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Session state
        self.created_at = datetime.utcnow()
        self.current_url: Optional[str] = None
        self.title: Optional[str] = None
        self.is_active = False
    
    async def start(self):
        """Start browser session."""
        if self.is_active:
            return
        
        self.playwright = await async_playwright().start()
        
        # Launch browser
        browser_launcher = getattr(self.playwright, self.browser_type)
        self.browser = await browser_launcher.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]  # Avoid detection
        )
        
        # Create context
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        self.is_active = True
    
    async def navigate(self, url: str, wait_until: str = "networkidle", timeout: int = 30000) -> Dict[str, Any]:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            wait_until: Wait condition ("load", "domcontentloaded", "networkidle", "commit")
            timeout: Navigation timeout in milliseconds
            
        Returns:
            Dictionary with navigation result
        """
        if not self.is_active or not self.page:
            raise RuntimeError("Browser session not started")
        
        try:
            response = await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            
            # Update state
            self.current_url = self.page.url
            self.title = await self.page.title()
            
            return {
                "success": True,
                "url": self.current_url,
                "title": self.title,
                "status": response.status if response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def get_ax_tree(self) -> Dict[str, Any]:
        """
        Get accessibility tree for current page.
        
        Returns:
            Accessibility tree as dictionary
        """
        if not self.is_active or not self.page:
            raise RuntimeError("Browser session not started")
        
        # Use Playwright's accessibility snapshot
        snapshot = await self.page.accessibility.snapshot()
        return snapshot or {}
    
    async def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information.
        
        Returns:
            Dictionary with page info
        """
        if not self.is_active or not self.page:
            return {
                "url": None,
                "title": None,
                "is_active": False
            }
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "is_active": self.is_active,
            "session_id": self.session_id
        }
    
    async def close(self):
        """Close browser session and cleanup."""
        if not self.is_active:
            return
        
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Error closing browser session: {e}")
        finally:
            self.is_active = False
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

