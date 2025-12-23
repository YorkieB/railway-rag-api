"""
CrewAI Integration
Main entry point for CrewAI multi-agent orchestration.
"""
from typing import Dict, Any, Optional
from crewai import Crew, Task
from .orchestrator import MultiAgentOrchestrator
import os


class CrewAIManager:
    """
    Manages CrewAI crew and agent orchestration.
    """
    
    def __init__(self, llm=None, chromadb_path: Optional[str] = None):
        """
        Initialize CrewAI manager.
        
        Args:
            llm: Optional LLM instance
            chromadb_path: Path to ChromaDB storage
        """
        self.llm = llm
        self.chromadb_path = chromadb_path
        self.orchestrator = MultiAgentOrchestrator(llm=llm, chromadb_path=chromadb_path)
        self.crew = None
    
    def execute_task(
        self,
        task_description: str,
        user_id: str = "default",
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using CrewAI orchestration.
        
        Args:
            task_description: Task to execute
            user_id: User identifier
            project_id: Optional project ID
            
        Returns:
            Dict with execution results
        """
        # Use orchestrator for multi-step tasks
        return self.orchestrator.execute_multi_step_task(
            task_description=task_description,
            user_id=user_id,
            project_id=project_id
        )
    
    def create_crew(self, tasks: list) -> Crew:
        """
        Create a CrewAI crew with tasks.
        
        Args:
            tasks: List of CrewAI Task objects
            
        Returns:
            CrewAI Crew instance
        """
        try:
            from crewai import Crew
            
            agents = [
                self.orchestrator.browser_agent.get_agent(),
                self.orchestrator.os_agent.get_agent(),
                self.orchestrator.rag_agent.get_agent()
            ]
            
            # Filter out None agents (if CrewAI not available)
            agents = [a for a in agents if a is not None]
            
            if not agents:
                raise Exception("No agents available - CrewAI may not be installed")
            
            self.crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=True
            )
            
            return self.crew
        except ImportError:
            raise Exception("CrewAI is not installed. Install with: pip install crewai")


# Global CrewAI manager instance
crewai_manager = None

def get_crewai_manager() -> CrewAIManager:
    """Get or create global CrewAI manager."""
    global crewai_manager
    if crewai_manager is None:
        chromadb_path = os.getenv("CHROMADB_PATH", "./rag_knowledge_base")
        crewai_manager = CrewAIManager(chromadb_path=chromadb_path)
    return crewai_manager

