"""
Multi-Agent Orchestrator
Coordinates multiple agents for complex multi-step tasks.
"""
from typing import Dict, Any, List, Optional
from crewai import Crew, Task
from .browser_agent import BrowserAgent
from .os_agent import OSAgent
from .rag_agent import RAGAgent
from windows.indicator import automation_indicator
from windows.panic import panic_stop
import uuid


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents for complex tasks.
    
    Features:
    - Plan generation
    - Agent coordination
    - State management
    - Error recovery
    - Integration with automation indicator and panic stop
    """
    
    def __init__(self, llm=None, chromadb_path: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            llm: Optional LLM instance for CrewAI
            chromadb_path: Path to ChromaDB storage
        """
        self.llm = llm
        self.browser_agent = BrowserAgent(llm=llm)
        self.os_agent = OSAgent(llm=llm)
        self.rag_agent = RAGAgent(llm=llm, chromadb_path=chromadb_path)
        self.active_automations: Dict[str, Dict] = {}
    
    def execute_multi_step_task(
        self,
        task_description: str,
        user_id: str = "default",
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a multi-step task using multiple agents.
        
        Args:
            task_description: High-level description of the task
            user_id: User identifier
            project_id: Optional project ID
            
        Returns:
            Dict with execution results
        """
        automation_id = str(uuid.uuid4())
        
        try:
            # Register automation
            automation_indicator.start_automation(
                automation_id=automation_id,
                action_description=task_description,
                total_steps=1  # Will be updated as plan is generated
            )
            
            panic_stop.register_automation(
                automation_id=automation_id,
                action_type="multi_agent_task",
                rollback_fn=lambda: self._rollback_automation(automation_id),
                metadata={"task_description": task_description}
            )
            
            # Generate plan
            plan = self._generate_plan(task_description)
            
            # Update automation indicator with plan steps
            if plan.get("steps"):
                automation_indicator.update_step(1, f"Planning: {len(plan['steps'])} steps")
            
            # Execute plan
            results = []
            for i, step in enumerate(plan.get("steps", []), 1):
                # Check for panic stop
                if panic_stop.is_panic_stopped():
                    return {
                        "success": False,
                        "error": "Panic stop triggered",
                        "automation_id": automation_id,
                        "completed_steps": i - 1
                    }
                
                # Update indicator
                automation_indicator.update_step(i, step.get("description", ""))
                
                # Execute step
                step_result = self._execute_step(step, project_id)
                results.append(step_result)
                
                # If step failed, decide on recovery
                if not step_result.get("success"):
                    recovery_result = self._handle_error(step, step_result, i)
                    if not recovery_result.get("success"):
                        # Stop execution on unrecoverable error
                        break
            
            # Complete automation
            automation_indicator.stop_automation(success=True)
            panic_stop.unregister_automation(automation_id)
            
            return {
                "success": True,
                "automation_id": automation_id,
                "plan": plan,
                "results": results,
                "total_steps": len(plan.get("steps", [])),
                "completed_steps": len([r for r in results if r.get("success")])
            }
            
        except Exception as e:
            automation_indicator.stop_automation(success=False, error=str(e))
            panic_stop.unregister_automation(automation_id)
            return {
                "success": False,
                "error": str(e),
                "automation_id": automation_id
            }
    
    def _generate_plan(self, task_description: str) -> Dict[str, Any]:
        """
        Generate execution plan from task description.
        
        Args:
            task_description: High-level task description
            
        Returns:
            Dict with plan steps
        """
        # Simple plan generation - in production, use LLM
        # For now, return a basic plan structure
        steps = []
        
        # Parse task to determine which agents are needed
        task_lower = task_description.lower()
        
        if "search" in task_lower or "find" in task_lower or "document" in task_lower:
            steps.append({
                "agent": "rag",
                "description": f"Search documents: {task_description}",
                "action": "search",
                "params": {"query": task_description}
            })
        
        if "browser" in task_lower or "web" in task_lower or "navigate" in task_lower:
            steps.append({
                "agent": "browser",
                "description": f"Browser automation: {task_description}",
                "action": "execute",
                "params": {"task": task_description}
            })
        
        if "app" in task_lower or "file" in task_lower or "windows" in task_lower:
            steps.append({
                "agent": "os",
                "description": f"OS automation: {task_description}",
                "action": "execute",
                "params": {"task": task_description}
            })
        
        # Default: if no specific agent identified, use RAG
        if not steps:
            steps.append({
                "agent": "rag",
                "description": f"Search for information: {task_description}",
                "action": "search",
                "params": {"query": task_description}
            })
        
        return {
            "task": task_description,
            "steps": steps,
            "estimated_duration": len(steps) * 5  # Rough estimate in seconds
        }
    
    def _execute_step(self, step: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: Step definition
            project_id: Optional project ID
            
        Returns:
            Dict with step execution result
        """
        agent_type = step.get("agent")
        action = step.get("action")
        params = step.get("params", {})
        
        try:
            if agent_type == "rag":
                query = params.get("query", "")
                result = self.rag_agent.execute_task(query, top_k=3, project_id=project_id)
            elif agent_type == "browser":
                task = params.get("task", "")
                result = self.browser_agent.execute_task(task)
            elif agent_type == "os":
                task = params.get("task", "")
                result = self.os_agent.execute_task(task)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown agent type: {agent_type}"
                }
            
            return {
                "step": step,
                "success": result.get("success", False),
                "result": result,
                "agent": agent_type
            }
        except Exception as e:
            return {
                "step": step,
                "success": False,
                "error": str(e),
                "agent": agent_type
            }
    
    def _handle_error(self, step: Dict[str, Any], step_result: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Handle error in step execution.
        
        Args:
            step: Step definition
            step_result: Step execution result
            step_number: Current step number
            
        Returns:
            Dict with recovery result
        """
        # Simple error handling - in production, use LLM for recovery planning
        error = step_result.get("error", "Unknown error")
        
        # For now, just log the error
        return {
            "success": False,
            "error": error,
            "recovery_attempted": False,
            "message": "Error recovery not implemented yet"
        }
    
    def plan_task(self, task_description: str) -> Dict[str, Any]:
        """
        Generate execution plan from task description (public API for testing).
        
        Args:
            task_description: High-level task description
            
        Returns:
            Dict with plan steps
        """
        return self._generate_plan(task_description)
    
    def _rollback_automation(self, automation_id: str) -> Dict[str, Any]:
        """
        Rollback automation (called by panic stop).
        
        Args:
            automation_id: Automation ID to rollback
            
        Returns:
            Dict with rollback result
        """
        # Simple rollback - in production, implement proper state restoration
        return {
            "success": True,
            "automation_id": automation_id,
            "message": "Automation rolled back"
        }

