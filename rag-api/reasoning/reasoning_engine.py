"""
Reasoning Engine

Orchestrates different reasoning methods.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import os

from .models import ReasoningTrace, ReasoningResult
from .chain_of_thought import ChainOfThought
from .reflection import ReflectionReasoning
from .self_consistency import SelfConsistency
from .tree_of_thoughts import TreeOfThoughts
from .react import ReActReasoning


class ReasoningEngine:
    """Main reasoning engine that orchestrates different reasoning methods."""
    
    def __init__(self, api_key: Optional[str] = None, tools: Optional[Dict[str, Any]] = None):
        """
        Initialize reasoning engine.
        
        Args:
            api_key: OpenAI API key
            tools: Tools for ReAct reasoning
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.cot = ChainOfThought(api_key=self.api_key)
        self.reflection = ReflectionReasoning(api_key=self.api_key)
        self.self_consistency = SelfConsistency(api_key=self.api_key)
        self.tot = TreeOfThoughts(api_key=self.api_key)
        self.react = ReActReasoning(api_key=self.api_key, tools=tools)
    
    async def reason(
        self,
        query: str,
        method: str = "cot",
        context: Optional[str] = None,
        **kwargs
    ) -> ReasoningResult:
        """
        Perform reasoning using specified method.
        
        Args:
            query: The question or problem
            method: Reasoning method ("cot", "reflection", "self_consistency", "tot", "react")
            context: Optional context information
            **kwargs: Additional method-specific parameters
        
        Returns:
            ReasoningResult with answer and trace
        """
        trace: Optional[ReasoningTrace] = None
        
        if method == "cot":
            trace = await self.cot.reason(query, context, max_steps=kwargs.get("max_steps", 5))
        elif method == "reflection":
            trace = await self.reflection.reason(query, context, max_iterations=kwargs.get("max_iterations", 3))
        elif method == "self_consistency":
            trace = await self.self_consistency.reason(query, context, num_paths=kwargs.get("num_paths", 5))
        elif method == "tot":
            trace = await self.tot.reason(
                query,
                context,
                max_depth=kwargs.get("max_depth", 3),
                branching_factor=kwargs.get("branching_factor", 3)
            )
        elif method == "react":
            trace = await self.react.reason(query, context, max_iterations=kwargs.get("max_iterations", 10))
        else:
            raise ValueError(f"Unknown reasoning method: {method}")
        
        if not trace:
            raise Exception("Reasoning failed to produce a trace")
        
        return ReasoningResult(
            answer=trace.final_answer or "No answer generated",
            trace=trace,
            confidence=trace.confidence,
            sources=[],
            metadata={"method": method}
        )

