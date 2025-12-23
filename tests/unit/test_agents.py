"""
Unit tests for Multi-Agent CrewAI integration.
"""
import pytest
import sys
from pathlib import Path

# Add rag-api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rag-api"))

try:
    from agents.orchestrator import MultiAgentOrchestrator
    from agents.browser_agent import BrowserAgent
    from agents.os_agent import OSAgent
    from agents.rag_agent import RAGAgent
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


class TestMultiAgentOrchestrator:
    """Test multi-agent orchestrator."""
    
    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    @pytest.mark.timeout(10)  # 10 second timeout to prevent hanging
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = MultiAgentOrchestrator()
        assert orchestrator is not None
    
    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    @pytest.mark.timeout(10)  # 10 second timeout to prevent hanging
    def test_plan_generation(self):
        """Test task planning."""
        orchestrator = MultiAgentOrchestrator()
        task = "Search for Python documentation and open browser"
        plan = orchestrator.plan_task(task)
        assert plan is not None
        assert "steps" in plan or "tasks" in plan


class TestBrowserAgent:
    """Test browser agent."""
    
    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    @pytest.mark.timeout(10)  # 10 second timeout to prevent hanging
    def test_agent_initialization(self):
        """Test browser agent can be initialized."""
        agent = BrowserAgent()
        assert agent is not None


class TestOSAgent:
    """Test OS agent."""
    
    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    @pytest.mark.timeout(10)  # 10 second timeout to prevent hanging
    def test_agent_initialization(self):
        """Test OS agent can be initialized."""
        agent = OSAgent()
        assert agent is not None


class TestRAGAgent:
    """Test RAG agent."""
    
    @pytest.mark.skipif(not CREWAI_AVAILABLE, reason="CrewAI not installed")
    @pytest.mark.timeout(10)  # 10 second timeout to prevent hanging
    def test_agent_initialization(self):
        """Test RAG agent can be initialized."""
        agent = RAGAgent()
        assert agent is not None

