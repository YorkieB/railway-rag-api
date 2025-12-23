"""
Panic Stop System
Implements immediate automation cancellation with rollback.
"""
import threading
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
import queue


class PanicStop:
    """
    Manages panic stop functionality for Windows automation.
    
    Safety Rules (CC3):
    - Panic stop must be immediate (< 500ms target, < 100ms ideal)
    - Cancels current action immediately
    - Rolls back partial file operations
    - Closes spawned windows
    - Logs incident
    - Returns UI focus to user
    """
    
    def __init__(self):
        """Initialize panic stop system."""
        self.active_automations: Dict[str, Dict] = {}
        self.panic_flag = threading.Event()
        self.rollback_queue: queue.Queue = queue.Queue()
        self.incident_log: List[Dict] = []
        self.lock = threading.Lock()
        
        # Keyboard hook will be set up by Windows app (not in Python)
        # Python API provides the panic stop logic
    
    def register_automation(
        self,
        automation_id: str,
        action_type: str,
        rollback_fn: Optional[Callable] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Register an active automation for panic stop monitoring.
        
        Args:
            automation_id: Unique ID for this automation
            action_type: Type of action (file_write, file_delete, app_launch, etc.)
            rollback_fn: Optional function to call for rollback
            metadata: Additional metadata about the automation
            
        Returns:
            True if registered successfully
        """
        with self.lock:
            self.active_automations[automation_id] = {
                "action_type": action_type,
                "rollback_fn": rollback_fn,
                "metadata": metadata or {},
                "started_at": datetime.now(),
                "status": "active"
            }
        return True
    
    def unregister_automation(self, automation_id: str) -> bool:
        """
        Unregister an automation (completed successfully).
        
        Args:
            automation_id: ID of automation to unregister
            
        Returns:
            True if unregistered successfully
        """
        with self.lock:
            if automation_id in self.active_automations:
                self.active_automations[automation_id]["status"] = "completed"
                del self.active_automations[automation_id]
                return True
        return False
    
    def trigger_panic_stop(self, automation_id: Optional[str] = None) -> Dict:
        """
        Trigger panic stop for specific automation or all automations.
        
        Args:
            automation_id: Specific automation to stop (None = stop all)
            
        Returns:
            Dict with stop results
        """
        start_time = time.time()
        stopped_automations = []
        rollback_results = []
        
        with self.lock:
            # Set panic flag
            self.panic_flag.set()
            
            # Get automations to stop
            if automation_id:
                automations_to_stop = {
                    k: v for k, v in self.active_automations.items()
                    if k == automation_id
                }
            else:
                automations_to_stop = self.active_automations.copy()
            
            # Stop each automation
            for auto_id, auto_info in automations_to_stop.items():
                stopped_automations.append(auto_id)
                
                # Execute rollback if available
                if auto_info.get("rollback_fn"):
                    try:
                        rollback_result = auto_info["rollback_fn"]()
                        rollback_results.append({
                            "automation_id": auto_id,
                            "success": True,
                            "result": rollback_result
                        })
                    except Exception as e:
                        rollback_results.append({
                            "automation_id": auto_id,
                            "success": False,
                            "error": str(e)
                        })
                
                # Mark as stopped
                auto_info["status"] = "stopped"
                auto_info["stopped_at"] = datetime.now()
        
        # Log incident
        elapsed_ms = (time.time() - start_time) * 1000
        incident = {
            "timestamp": datetime.now(),
            "automation_ids": stopped_automations,
            "elapsed_ms": elapsed_ms,
            "rollback_results": rollback_results
        }
        self.incident_log.append(incident)
        
        # Clear panic flag after a short delay
        threading.Timer(0.1, self.panic_flag.clear).start()
        
        return {
            "success": True,
            "stopped_automations": stopped_automations,
            "rollback_results": rollback_results,
            "elapsed_ms": elapsed_ms,
            "incident_id": len(self.incident_log) - 1
        }
    
    def is_panic_stopped(self) -> bool:
        """Check if panic stop is active."""
        return self.panic_flag.is_set()
    
    def get_active_automations(self) -> List[Dict]:
        """Get list of active automations."""
        with self.lock:
            return [
                {
                    "automation_id": auto_id,
                    "action_type": info["action_type"],
                    "started_at": info["started_at"].isoformat(),
                    "status": info["status"],
                    "metadata": info.get("metadata", {})
                }
                for auto_id, info in self.active_automations.items()
            ]
    
    def get_incident_log(self, limit: int = 10) -> List[Dict]:
        """Get recent panic stop incidents."""
        return self.incident_log[-limit:]
    
    def clear_incident_log(self) -> bool:
        """Clear incident log."""
        self.incident_log.clear()
        return True


# Global panic stop instance
panic_stop = PanicStop()

