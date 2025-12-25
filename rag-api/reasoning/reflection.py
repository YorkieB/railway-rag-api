"""
Reflection and Refinement Reasoning

Self-critique and iterative improvement of reasoning.
"""

from typing import List, Optional
from datetime import datetime
import os
from openai import AsyncOpenAI

from .models import ReasoningStep, ReasoningTrace, ReasoningStatus
from .chain_of_thought import ChainOfThought


class ReflectionReasoning:
    """Reflection-based reasoning with self-critique."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize reflection reasoning."""
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
        max_iterations: int = 3
    ) -> ReasoningTrace:
        """
        Perform reflection-based reasoning.
        
        Args:
            query: The question or problem
            context: Optional context
            max_iterations: Maximum refinement iterations
        
        Returns:
            ReasoningTrace with reflection steps
        """
        trace = ReasoningTrace(
            id=f"reflection_{datetime.utcnow().timestamp()}",
            query=query,
            method="reflection"
        )
        
        # Initial reasoning
        initial_trace = await self.cot.reason(query, context)
        trace.steps.extend(initial_trace.steps)
        
        current_answer = initial_trace.final_answer or ""
        
        # Reflection iterations
        for iteration in range(1, max_iterations + 1):
            # Critique current reasoning
            critique = await self._critique(current_answer, query)
            
            trace.steps.append(ReasoningStep(
                step_number=len(trace.steps) + 1,
                description=f"Reflection Iteration {iteration}",
                reasoning=critique,
                status=ReasoningStatus.COMPLETED,
                metadata={"iteration": iteration, "type": "critique"}
            ))
            
            # Refine based on critique
            refined = await self._refine(current_answer, critique, query)
            
            trace.steps.append(ReasoningStep(
                step_number=len(trace.steps) + 1,
                description=f"Refinement Iteration {iteration}",
                reasoning=refined,
                status=ReasoningStatus.COMPLETED,
                metadata={"iteration": iteration, "type": "refinement"}
            ))
            
            current_answer = refined
        
        trace.final_answer = current_answer
        trace.confidence = 0.85  # Reflection improves confidence
        trace.completed_at = datetime.utcnow()
        
        return trace
    
    async def _critique(self, answer: str, query: str) -> str:
        """Critique the current answer."""
        prompt = f"""Review the following answer to the question and identify:
1. Any gaps in reasoning
2. Potential errors or inconsistencies
3. Areas that need clarification
4. Missing information

Question: {query}
Answer: {answer}

Provide constructive criticism:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _refine(self, answer: str, critique: str, query: str) -> str:
        """Refine the answer based on critique."""
        prompt = f"""Based on the critique, improve your answer to the question.

Question: {query}
Original Answer: {answer}
Critique: {critique}

Provide an improved answer:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

