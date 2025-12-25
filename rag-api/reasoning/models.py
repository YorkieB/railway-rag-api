"""
Reasoning data models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class ReasoningStatus(str, Enum):
    """Reasoning step status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReasoningStep:
    """Represents a single reasoning step."""
    step_number: int
    description: str
    reasoning: str
    status: ReasoningStatus = ReasoningStatus.PENDING
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningTrace:
    """Represents a complete reasoning trace."""
    id: str
    query: str
    method: str  # "cot", "reflection", "tot", "react", etc.
    steps: List[ReasoningStep] = field(default_factory=list)
    final_answer: Optional[str] = None
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    """Result of reasoning process."""
    answer: str
    trace: ReasoningTrace
    confidence: float
    sources: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

