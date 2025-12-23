"""
BrowserSession: Manages Playwright browser instances and sessions.
"""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict
import uuid


class BrowserSession:
    """
    Manages a single browser session with Playwright.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url: Optional[str] = None
    
    async def initialize(self):
        """Initialize Playwright and browser"""
        self.playwright = await async_playwright().start()
        # Use Chromium for consistency
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        self.page = await self.context.new_page()
    
    async def navigate(self, url: str) -> Dict:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Dict with success status and page info
        """
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            self.current_url = self.page.url
            title = await self.page.title()
            
            return {
                "success": True,
                "url": self.current_url,
                "title": title
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_screenshot(self) -> bytes:
        """Get screenshot of current page"""
        if not self.page:
            raise ValueError("Page not initialized")
        return await self.page.screenshot(full_page=False)
    
    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.page is not None and not self.page.is_closed()


# Store active browser sessions (in-memory for MVP)
active_browser_sessions: Dict[str, BrowserSession] = {}

