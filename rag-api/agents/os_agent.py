"""
OS Agent for CrewAI
Specialized agent for Windows OS automation tasks.
"""
from typing import Dict, Any, Optional
from crewai import Agent
from windows.apps import app_manager
from windows.files import file_manager
from windows.vision import screen_vision
from windows.roc import roc


class OSAgent:
    """
    Windows OS automation agent for CrewAI.
    
    Capabilities:
    - Launch/switch applications
    - File operations (read/write/delete)
    - Screen-based automation
    - Region-of-Control management
    """
    
    def __init__(self, llm=None):
        """
        Initialize OS agent.
        
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
                    role="Windows OS Automation Specialist",
                    goal="Execute Windows OS automation tasks safely with proper guardrails",
                    backstory="""You are an expert at Windows OS automation. You can launch
                    applications, manage files, and interact with the desktop. You always
                    respect safety guardrails - system directories are protected, file
                    operations require approval, and you use Region-of-Control to limit
                    automation scope.""",
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
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute an OS automation task.
        
        Args:
            task_description: Description of the task to perform
            
        Returns:
            Dict with execution results
        """
        try:
            # Parse task description and route to appropriate handler
            task_lower = task_description.lower()
            
            if "launch" in task_lower or "open" in task_lower:
                # Extract app name from description
                # Simple parsing - in production, use LLM to extract intent
                result = self._handle_app_launch(task_description)
            elif "file" in task_lower or "read" in task_lower or "write" in task_lower:
                result = self._handle_file_operation(task_description)
            elif "screenshot" in task_lower or "capture" in task_lower:
                result = self._handle_screenshot(task_description)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown task type: {task_description}"
                }
            
            return {
                "success": result.get("success", False),
                "result": result,
                "agent_type": "os"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_type": "os"
            }
    
    def _handle_app_launch(self, description: str) -> Dict[str, Any]:
        """Handle app launch task."""
        # Simple extraction - in production, use LLM
        # For now, return a placeholder
        return {
            "success": False,
            "error": "App launch requires explicit app path",
            "message": "Please specify the exact application path to launch"
        }
    
    def _handle_file_operation(self, description: str) -> Dict[str, Any]:
        """Handle file operation task."""
        return {
            "success": False,
            "error": "File operation requires explicit file path and approval",
            "message": "Please specify the exact file path and confirm approval"
        }
    
    def _handle_screenshot(self, description: str) -> Dict[str, Any]:
        """Handle screenshot task."""
        screenshot_bytes = screen_vision.capture_screenshot()
        if screenshot_bytes:
            import base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return {
                "success": True,
                "screenshot": screenshot_base64,
                "format": "png"
            }
        else:
            return {
                "success": False,
                "error": "Failed to capture screenshot"
            }
    
    def get_agent(self):
        """Get CrewAI agent instance."""
        return self.agent

