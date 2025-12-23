"""
Agentic Autonomy

Self-improving agents with learning capabilities.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class AutonomousAgent:
    """Autonomous agent with self-improvement capabilities"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize autonomous agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (browser, os, rag, etc.)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.performance_history: List[Dict] = []
        self.learned_patterns: List[Dict] = []
        self.success_rate = 1.0
        self.total_tasks = 0
        self.successful_tasks = 0
    
    def record_task_result(
        self,
        task_description: str,
        success: bool,
        feedback: Optional[str] = None,
        execution_time: Optional[float] = None
    ):
        """Record task execution result for learning"""
        self.total_tasks += 1
        if success:
            self.successful_tasks += 1
        
        self.success_rate = self.successful_tasks / self.total_tasks if self.total_tasks > 0 else 1.0
        
        record = {
            "task": task_description,
            "success": success,
            "feedback": feedback,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.performance_history.append(record)
        
        # Keep only last 100 records
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    def learn_from_feedback(self, feedback: str, pattern: Dict):
        """Learn from user feedback and extract patterns"""
        self.learned_patterns.append({
            "feedback": feedback,
            "pattern": pattern,
            "learned_at": datetime.now().isoformat()
        })
    
    def get_improvement_suggestions(self) -> List[str]:
        """Generate improvement suggestions based on performance"""
        suggestions = []
        
        if self.success_rate < 0.7:
            suggestions.append("Success rate is below 70%. Consider reviewing recent failures.")
        
        if len(self.performance_history) > 0:
            recent_failures = [
                r for r in self.performance_history[-10:]
                if not r.get("success", True)
            ]
            if len(recent_failures) > 3:
                suggestions.append("Multiple recent failures detected. Review error patterns.")
        
        return suggestions


# In-memory agent storage
autonomous_agents: Dict[str, AutonomousAgent] = {}


class AgentAutonomyManager:
    """Manages autonomous agents"""
    
    def get_or_create_agent(self, agent_id: str, agent_type: str) -> AutonomousAgent:
        """Get or create autonomous agent"""
        if agent_id not in autonomous_agents:
            autonomous_agents[agent_id] = AutonomousAgent(agent_id, agent_type)
        return autonomous_agents[agent_id]
    
    def list_agents(self) -> List[Dict]:
        """List all autonomous agents"""
        return [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "success_rate": agent.success_rate,
                "total_tasks": agent.total_tasks,
                "learned_patterns_count": len(agent.learned_patterns)
            }
            for agent in autonomous_agents.values()
        ]


# Global agent autonomy manager
agent_autonomy_manager = AgentAutonomyManager()

