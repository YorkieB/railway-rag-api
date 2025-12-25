"""
Self-Consistency Reasoning

Generate multiple reasoning paths and select the most consistent answer.
"""

from typing import List, Optional
from datetime import datetime
from collections import Counter
import os
from openai import AsyncOpenAI

from .models import ReasoningStep, ReasoningTrace, ReasoningStatus
from .chain_of_thought import ChainOfThought


class SelfConsistency:
    """Self-consistency reasoning implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize self-consistency reasoning."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for reasoning")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.cot = ChainOfThought(api_key=self.api_key)
    
    async def reason(
        self,
        query: str,
        context: Optional[str] = None,
        num_paths: int = 5
    ) -> ReasoningTrace:
        """
        Perform self-consistency reasoning.
        
        Args:
            query: The question or problem
            context: Optional context
            num_paths: Number of reasoning paths to generate
        
        Returns:
            ReasoningTrace with consensus answer
        """
        trace = ReasoningTrace(
            id=f"self_consistency_{datetime.utcnow().timestamp()}",
            query=query,
            method="self_consistency"
        )
        
        # Generate multiple reasoning paths
        paths = []
        for i in range(num_paths):
            path_trace = await self.cot.reason(query, context)
            paths.append(path_trace.final_answer or "")
            
            trace.steps.append(ReasoningStep(
                step_number=i + 1,
                description=f"Reasoning Path {i + 1}",
                reasoning=path_trace.final_answer or "",
                status=ReasoningStatus.COMPLETED,
                metadata={"path": i + 1}
            ))
        
        # Find consensus answer
        consensus = await self._find_consensus(paths, query)
        
        trace.steps.append(ReasoningStep(
            step_number=num_paths + 1,
            description="Consensus Selection",
            reasoning=consensus,
            status=ReasoningStatus.COMPLETED,
            metadata={"type": "consensus"}
        ))
        
        trace.final_answer = consensus
        trace.confidence = self._calculate_consensus_confidence(paths, consensus)
        trace.completed_at = datetime.utcnow()
        
        return trace
    
    async def _find_consensus(self, paths: List[str], query: str) -> str:
        """Find consensus answer from multiple paths."""
        # Simple approach: Use LLM to find common themes
        prompt = f"""Given multiple reasoning paths for the same question, identify the consensus answer.

Question: {query}

Reasoning Paths:
{chr(10).join(f"Path {i+1}: {path}" for i, path in enumerate(paths))}

Provide the consensus answer that best represents the common conclusion:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Lower temperature for more consistent consensus
        )
        
        return response.choices[0].message.content
    
    def _calculate_consensus_confidence(self, paths: List[str], consensus: str) -> float:
        """Calculate confidence based on path similarity."""
        # Simple similarity check (can be enhanced with embeddings)
        # Higher confidence if paths are similar
        if not paths:
            return 0.0
        
        # Count how many paths contain key phrases from consensus
        consensus_words = set(consensus.lower().split())
        matches = 0
        
        for path in paths:
            path_words = set(path.lower().split())
            overlap = len(consensus_words & path_words)
            if overlap > len(consensus_words) * 0.3:  # 30% overlap threshold
                matches += 1
        
        confidence = matches / len(paths)
        return min(confidence, 0.95)  # Cap at 0.95

