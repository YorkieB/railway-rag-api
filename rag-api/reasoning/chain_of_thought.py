"""
Chain-of-Thought (CoT) Reasoning Implementation

Breaks complex problems into step-by-step reasoning.
"""

from typing import List, Dict, Any, Optional
import os
from openai import AsyncOpenAI

from .models import ReasoningStep, ReasoningTrace, ReasoningStatus


class ChainOfThought:
    """Chain-of-Thought reasoning implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize CoT reasoning."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for reasoning")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    async def reason(
        self,
        query: str,
        context: Optional[str] = None,
        max_steps: int = 5
    ) -> ReasoningTrace:
        """
        Perform chain-of-thought reasoning.
        
        Args:
            query: The question or problem to reason about
            context: Optional context information
            max_steps: Maximum number of reasoning steps
        
        Returns:
            ReasoningTrace with step-by-step reasoning
        """
        trace = ReasoningTrace(
            id=f"cot_{datetime.utcnow().timestamp()}",
            query=query,
            method="cot"
        )
        
        # Build initial prompt with CoT instructions
        system_prompt = """You are a reasoning assistant. Break down complex problems into clear, logical steps.
For each step, explain your reasoning clearly before moving to the next step.
Think step by step."""
        
        user_prompt = query
        if context:
            user_prompt = f"Context: {context}\n\nQuestion: {query}"
        
        # Generate reasoning steps
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        reasoning_text = response.choices[0].message.content
        
        # Parse reasoning into steps (simplified - can be enhanced)
        steps = self._parse_reasoning_steps(reasoning_text, max_steps)
        
        trace.steps = steps
        trace.final_answer = reasoning_text
        trace.confidence = 0.8  # Default confidence
        trace.completed_at = datetime.utcnow()
        
        return trace
    
    def _parse_reasoning_steps(self, reasoning_text: str, max_steps: int) -> List[ReasoningStep]:
        """Parse reasoning text into steps."""
        steps = []
        lines = reasoning_text.split('\n')
        current_step = None
        step_num = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect step markers (Step 1, 1., etc.)
            if any(marker in line.lower() for marker in ['step', '1.', '2.', '3.', 'first', 'second', 'then', 'next']):
                if current_step:
                    steps.append(current_step)
                    step_num += 1
                    if step_num > max_steps:
                        break
                
                current_step = ReasoningStep(
                    step_number=step_num,
                    description=line[:100],  # First 100 chars as description
                    reasoning=line,
                    status=ReasoningStatus.COMPLETED
                )
            elif current_step:
                current_step.reasoning += "\n" + line
            else:
                # First line without step marker
                current_step = ReasoningStep(
                    step_number=step_num,
                    description=line[:100],
                    reasoning=line,
                    status=ReasoningStatus.COMPLETED
                )
        
        if current_step and len(steps) < max_steps:
            steps.append(current_step)
        
        # If no steps were parsed, create a single step
        if not steps:
            steps.append(ReasoningStep(
                step_number=1,
                description=reasoning_text[:100],
                reasoning=reasoning_text,
                status=ReasoningStatus.COMPLETED
            ))
        
        return steps

