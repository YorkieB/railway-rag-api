"""
Jarvis RAG API Package

Main package for RAG API with:
- Context budget enforcement
- Memory system
- Uncertainty protocol
- Cost tracking
- Live sessions
- Browser automation
"""

# Core components
from .budget import ContextBudgetEnforcer
from .models import MemoryItem, LiveSession
from .memory_storage import MemoryStorage, ChromaDBMemoryStorage
from .uncertainty import UncertaintyChecker
from .cost import CostTracker

# Browser automation
from .browser import (
    BrowserSession,
    ActionExecutor,
    AgentLoop,
    SafetyChecker,
)

__version__ = "1.0.0"

__all__ = [
    "ContextBudgetEnforcer",
    "MemoryItem",
    "LiveSession",
    "MemoryStorage",
    "ChromaDBMemoryStorage",
    "UncertaintyChecker",
    "CostTracker",
    "BrowserSession",
    "ActionExecutor",
    "AgentLoop",
    "SafetyChecker",
]

