"""
Workflow Recorder

Records browser actions for replay.
"""
from typing import List, Dict, Optional
from datetime import datetime
import json


class WorkflowRecorder:
    """Records and replays browser workflows"""
    
    def __init__(self):
        """Initialize workflow recorder"""
        self.recording = False
        self.workflow_steps: List[Dict] = []
    
    def start_recording(self) -> None:
        """Start recording workflow"""
        self.recording = True
        self.workflow_steps = []
    
    def stop_recording(self) -> Dict:
        """Stop recording and return workflow"""
        self.recording = False
        workflow = {
            "steps": self.workflow_steps.copy(),
            "step_count": len(self.workflow_steps),
            "created_at": datetime.now().isoformat()
        }
        self.workflow_steps = []
        return workflow
    
    def record_action(self, action_type: str, selector: str, value: Optional[str] = None) -> None:
        """
        Record a browser action.
        
        Args:
            action_type: Type of action (click, type, navigate, etc.)
            selector: Element selector or URL
            value: Optional value (for type actions)
        """
        if not self.recording:
            return
        
        step = {
            "action_type": action_type,
            "selector": selector,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        self.workflow_steps.append(step)
    
    def save_workflow(self, workflow: Dict, filename: str) -> None:
        """Save workflow to file"""
        with open(filename, "w") as f:
            json.dump(workflow, f, indent=2)
    
    def load_workflow(self, filename: str) -> Dict:
        """Load workflow from file"""
        with open(filename, "r") as f:
            return json.load(f)

