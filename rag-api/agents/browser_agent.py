"""
Browser Agent for CrewAI
Specialized agent for browser automation tasks.
"""
from typing import Dict, Any, Optional
from crewai import Agent, Task
from browser.session import BrowserSession, active_browser_sessions
from browser.actions import ActionExecutor
from browser.agent_loop import BrowserAutomation


class BrowserAgent:
    """
    Browser automation agent for CrewAI.
    
    Capabilities:
    - Navigate to URLs
    - Click elements
    - Fill forms
    - Extract text
    - Take screenshots
    - Plan-Act-Verify-Recover pattern
    """
    
    def __init__(self, llm=None):
        """
        Initialize browser agent.
        
        Args:
            llm: Optional LLM instance for CrewAI
        """
        self.llm = llm
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize CrewAI agent."""
        try:
            from crewai import Agent
            
            # Try to create agent, but handle LLM initialization failures gracefully
            try:
                self.agent = Agent(
                    role="Browser Automation Specialist",
                    goal="Execute browser automation tasks safely and accurately",
                    backstory="""You are an expert at browser automation. You use Playwright
                    to interact with web pages, following the Plan-Act-Verify-Recover pattern.
                    You always verify actions succeeded before proceeding. You use the
                    Accessibility Tree (AX Tree) to find elements reliably.""",
                    verbose=False,  # Set to False to reduce initialization overhead
                    allow_delegation=False,
                    llm=self.llm
                )
            except Exception as e:
                # LLM initialization failed (e.g., missing API key)
                # This is acceptable - agent can still be used for non-LLM tasks
                import warnings
                warnings.warn(f"CrewAI Agent created without LLM: {e}")
                self.agent = None
        except ImportError:
            # CrewAI not available - use fallback
            self.agent = None
    
    def execute_task(self, task_description: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a browser automation task.
        
        Args:
            task_description: Description of the task to perform
            session_id: Optional existing browser session ID
            
        Returns:
            Dict with execution results
        """
        try:
            # Get or create browser session
            if session_id and session_id in active_browser_sessions:
                session = active_browser_sessions[session_id]
            else:
                session = BrowserSession()
                session_id = session.session_id
                active_browser_sessions[session_id] = session
            
            # Use browser automation loop for complex tasks
            automation = BrowserAutomation(session)
            result = automation.execute_task(task_description)
            
            return {
                "success": True,
                "session_id": session_id,
                "result": result,
                "agent_type": "browser"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": "browser"
            }
    
    def get_agent(self):
        """Get CrewAI agent instance."""
        return self.agent

