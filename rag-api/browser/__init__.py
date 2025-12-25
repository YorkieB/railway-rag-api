"""
Browser Automation Module

Provides browser automation capabilities using Playwright with:
- Browser session management
- AX Tree extraction
- Safety guardrails
- Action execution
- Plan-Act-Verify-Recover pattern
- Uncertainty protocol
"""

from .browser_session import BrowserSession
from .ax_tree import extract_ax_tree, AXTreeNode
from .safety import SafetyChecker, SafetyViolation
from .actions import ActionExecutor, ActionResult
from .agent_loop import AgentLoop, Plan, AgentStep
from .uncertainty import BrowserUncertaintyChecker, BrowserUncertainResponse

__all__ = [
    "BrowserSession",
    "extract_ax_tree",
    "AXTreeNode",
    "SafetyChecker",
    "SafetyViolation",
    "ActionExecutor",
    "ActionResult",
    "AgentLoop",
    "Plan",
    "AgentStep",
    "BrowserUncertaintyChecker",
    "BrowserUncertainResponse"
]

