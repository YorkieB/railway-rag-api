"""
Tree of Thoughts (ToT) Reasoning

Explore multiple reasoning branches and select the best path.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from openai import AsyncOpenAI

from .models import ReasoningStep, ReasoningTrace, ReasoningStatus


class TreeOfThoughts:
    """Tree of Thoughts reasoning implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize ToT reasoning."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for reasoning")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    async def reason(
        self,
        query: str,
        context: Optional[str] = None,
        max_depth: int = 3,
        branching_factor: int = 3
    ) -> ReasoningTrace:
        """
        Perform tree-of-thoughts reasoning.
        
        Args:
            query: The question or problem
            context: Optional context
            max_depth: Maximum tree depth
            branching_factor: Number of branches per node
        
        Returns:
            ReasoningTrace with best path
        """
        trace = ReasoningTrace(
            id=f"tot_{datetime.utcnow().timestamp()}",
            query=query,
            method="tree_of_thoughts"
        )
        
        # Build reasoning tree
        root_node = await self._generate_thoughts(query, context, 1)
        trace.steps.append(ReasoningStep(
            step_number=1,
            description="Initial Thoughts",
            reasoning=root_node["thought"],
            status=ReasoningStatus.COMPLETED,
            metadata={"depth": 1, "node": "root"}
        ))
        
        # Expand tree
        current_level = [root_node]
        best_path = [root_node]
        
        for depth in range(2, max_depth + 1):
            next_level = []
            
            for node in current_level:
                # Generate branches from this node
                branches = await self._generate_branches(
                    node["thought"],
                    query,
                    branching_factor
                )
                
                # Evaluate branches
                for branch in branches:
                    evaluation = await self._evaluate_branch(branch, query)
                    branch["score"] = evaluation
                    next_level.append(branch)
                    
                    trace.steps.append(ReasoningStep(
                        step_number=len(trace.steps) + 1,
                        description=f"Branch at Depth {depth}",
                        reasoning=branch["thought"],
                        status=ReasoningStatus.COMPLETED,
                        metadata={"depth": depth, "score": evaluation}
                    ))
            
            # Select best branches for next level
            next_level.sort(key=lambda x: x["score"], reverse=True)
            current_level = next_level[:branching_factor]
            
            # Update best path
            if current_level:
                best_path.append(current_level[0])
        
        # Select final answer from best path
        final_answer = await self._synthesize_answer(best_path, query)
        
        trace.final_answer = final_answer
        trace.confidence = best_path[-1]["score"] if best_path else 0.0
        trace.completed_at = datetime.utcnow()
        
        return trace
    
    async def _generate_thoughts(self, query: str, context: Optional[str], depth: int) -> Dict[str, Any]:
        """Generate initial thoughts."""
        prompt = f"""Think about the following question and provide your initial thoughts.

Question: {query}
{f'Context: {context}' if context else ''}

Provide your initial reasoning:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        
        return {
            "thought": response.choices[0].message.content,
            "score": 0.5,
            "depth": depth
        }
    
    async def _generate_branches(self, current_thought: str, query: str, num_branches: int) -> List[Dict[str, Any]]:
        """Generate branches from current thought."""
        branches = []
        
        for i in range(num_branches):
            prompt = f"""Based on the current reasoning, explore a different approach or perspective.

Question: {query}
Current Reasoning: {current_thought}

Provide an alternative or extended line of reasoning (Branch {i+1}):"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9  # Higher temperature for diversity
            )
            
            branches.append({
                "thought": response.choices[0].message.content,
                "score": 0.0,
                "parent": current_thought
            })
        
        return branches
    
    async def _evaluate_branch(self, branch: Dict[str, Any], query: str) -> float:
        """Evaluate a branch's quality (0.0 to 1.0)."""
        prompt = f"""Evaluate the quality of this reasoning approach for answering the question.
Rate from 0.0 (poor) to 1.0 (excellent). Respond with just a number.

Question: {query}
Reasoning: {branch['thought']}

Rating:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1  # Low temperature for consistent evaluation
        )
        
        try:
            score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, score))  # Clamp to 0-1
        except ValueError:
            return 0.5  # Default score
    
    async def _synthesize_answer(self, best_path: List[Dict[str, Any]], query: str) -> str:
        """Synthesize final answer from best path."""
        path_text = "\n".join([f"Step {i+1}: {node['thought']}" for i, node in enumerate(best_path)])
        
        prompt = f"""Based on the best reasoning path, provide a final answer.

Question: {query}

Best Reasoning Path:
{path_text}

Final Answer:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content

