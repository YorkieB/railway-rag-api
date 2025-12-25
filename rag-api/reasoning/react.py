"""
ReAct (Reasoning + Acting) Pattern

Integrates reasoning with tool use and action execution.
"""

from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import os
from openai import AsyncOpenAI

from .models import ReasoningStep, ReasoningTrace, ReasoningStatus


class ReActReasoning:
    """ReAct reasoning implementation."""
    
    def __init__(self, api_key: Optional[str] = None, tools: Optional[Dict[str, Callable]] = None):
        """
        Initialize ReAct reasoning.
        
        Args:
            api_key: OpenAI API key
            tools: Dictionary of available tools (name -> function)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for reasoning")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.tools = tools or {}
    
    async def reason(
        self,
        query: str,
        context: Optional[str] = None,
        max_iterations: int = 10
    ) -> ReasoningTrace:
        """
        Perform ReAct reasoning.
        
        Args:
            query: The question or task
            context: Optional context
            max_iterations: Maximum reasoning-action iterations
        
        Returns:
            ReasoningTrace with reasoning and actions
        """
        trace = ReasoningTrace(
            id=f"react_{datetime.utcnow().timestamp()}",
            query=query,
            method="react"
        )
        
        observations = []
        current_state = context or ""
        
        for iteration in range(max_iterations):
            # Think: Reason about next step
            thought = await self._think(query, current_state, observations)
            
            trace.steps.append(ReasoningStep(
                step_number=iteration + 1,
                description=f"Thought {iteration + 1}",
                reasoning=thought,
                status=ReasoningStatus.COMPLETED,
                metadata={"type": "thought", "iteration": iteration + 1}
            ))
            
            # Act: Decide on action
            action = await self._decide_action(thought, query)
            
            if action["type"] == "finish":
                # Final answer
                trace.final_answer = action.get("answer", thought)
                break
            
            trace.steps.append(ReasoningStep(
                step_number=len(trace.steps) + 1,
                description=f"Action {iteration + 1}",
                reasoning=f"Action: {action['type']} - {action.get('tool', 'N/A')}",
                status=ReasoningStatus.COMPLETED,
                metadata={"type": "action", "action": action}
            ))
            
            # Execute action
            observation = await self._execute_action(action)
            observations.append(observation)
            current_state += f"\nObservation: {observation}"
            
            trace.steps.append(ReasoningStep(
                step_number=len(trace.steps) + 1,
                description=f"Observation {iteration + 1}",
                reasoning=observation,
                status=ReasoningStatus.COMPLETED,
                metadata={"type": "observation", "iteration": iteration + 1}
            ))
        
        if not trace.final_answer:
            trace.final_answer = current_state
        
        trace.confidence = 0.8
        trace.completed_at = datetime.utcnow()
        
        return trace
    
    async def _think(self, query: str, state: str, observations: List[str]) -> str:
        """Generate a thought about the next step."""
        obs_text = "\n".join([f"Obs {i+1}: {obs}" for i, obs in enumerate(observations)])
        
        prompt = f"""You are reasoning about how to answer a question or complete a task.

Question/Task: {query}
Current State: {state}
Previous Observations:
{obs_text if observations else "None"}

Think about what to do next. Consider:
1. What information do you need?
2. What actions can you take?
3. What tools are available?

Your thought:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _decide_action(self, thought: str, query: str) -> Dict[str, Any]:
        """Decide on an action based on thought."""
        tools_list = ", ".join(self.tools.keys()) if self.tools else "None"
        
        prompt = f"""Based on your thought, decide on an action.

Thought: {thought}
Question: {query}
Available Tools: {tools_list}

Respond in one of these formats:
1. To use a tool: {{"type": "use_tool", "tool": "tool_name", "args": {{"arg1": "value1"}}}}
2. To finish: {{"type": "finish", "answer": "final answer"}}
3. To continue thinking: {{"type": "think"}}

Action:"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # Parse response (simplified - in production, use structured output)
        action_text = response.choices[0].message.content
        
        # Simple parsing (can be enhanced)
        if "finish" in action_text.lower():
            return {"type": "finish", "answer": action_text}
        elif "use_tool" in action_text.lower() or any(tool in action_text for tool in self.tools.keys()):
            # Extract tool name
            for tool_name in self.tools.keys():
                if tool_name in action_text:
                    return {"type": "use_tool", "tool": tool_name, "args": {}}
        
        return {"type": "think"}
    
    async def _execute_action(self, action: Dict[str, Any]) -> str:
        """Execute an action and return observation."""
        if action["type"] == "use_tool" and action.get("tool") in self.tools:
            tool = self.tools[action["tool"]]
            args = action.get("args", {})
            try:
                if callable(tool):
                    result = tool(**args) if args else tool()
                    return f"Tool {action['tool']} executed successfully. Result: {result}"
                else:
                    return f"Tool {action['tool']} is not callable"
            except Exception as e:
                return f"Tool {action['tool']} failed: {str(e)}"
        elif action["type"] == "finish":
            return "Task completed"
        else:
            return "Continuing to think..."

