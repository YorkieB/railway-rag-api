"""
Automation Indicator System
Manages always-visible automation status indicators.
"""
import threading
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class AutomationStatus(Enum):
    """Automation status states."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class AutomationIndicator:
    """
    Manages automation status indicators.
    
    Safety Rules (CC3):
    - Always-visible indicator when automation is active
    - Taskbar badge (animated pulse)
    - On-screen banner (for automations > 10 seconds)
    - Automation console endpoint
    - Status updates in real-time
    """
    
    def __init__(self):
        """Initialize automation indicator."""
        self.current_automation: Optional[Dict] = None
        self.automation_history: list = []
        self.status = AutomationStatus.IDLE
        self.lock = threading.Lock()
        self.start_time: Optional[datetime] = None
        
        # Status update callbacks (for Windows app integration)
        self.status_callbacks: list = []
    
    def start_automation(
        self,
        automation_id: str,
        action_description: str,
        total_steps: int = 1
    ) -> bool:
        """
        Start tracking an automation.
        
        Args:
            automation_id: Unique ID for automation
            action_description: Human-readable description
            total_steps: Total number of steps expected
            
        Returns:
            True if started successfully
        """
        with self.lock:
            self.current_automation = {
                "automation_id": automation_id,
                "action_description": action_description,
                "total_steps": total_steps,
                "current_step": 0,
                "started_at": datetime.now(),
                "status": AutomationStatus.ACTIVE.value
            }
            self.status = AutomationStatus.ACTIVE
            self.start_time = datetime.now()
            
            # Notify callbacks
            self._notify_status_change()
        
        return True
    
    def update_step(self, step: int, step_description: Optional[str] = None) -> bool:
        """
        Update current step in automation.
        
        Args:
            step: Current step number (1-indexed)
            step_description: Optional description of current step
            
        Returns:
            True if updated successfully
        """
        with self.lock:
            if self.current_automation:
                self.current_automation["current_step"] = step
                if step_description:
                    self.current_automation["step_description"] = step_description
                self._notify_status_change()
                return True
        return False
    
    def pause_automation(self) -> bool:
        """Pause current automation."""
        with self.lock:
            if self.current_automation:
                self.current_automation["status"] = AutomationStatus.PAUSED.value
                self.status = AutomationStatus.PAUSED
                self._notify_status_change()
                return True
        return False
    
    def resume_automation(self) -> bool:
        """Resume paused automation."""
        with self.lock:
            if self.current_automation and self.status == AutomationStatus.PAUSED:
                self.current_automation["status"] = AutomationStatus.ACTIVE.value
                self.status = AutomationStatus.ACTIVE
                self._notify_status_change()
                return True
        return False
    
    def stop_automation(self, success: bool = True, error: Optional[str] = None) -> bool:
        """
        Stop current automation.
        
        Args:
            success: Whether automation completed successfully
            error: Optional error message if failed
            
        Returns:
            True if stopped successfully
        """
        with self.lock:
            if self.current_automation:
                end_time = datetime.now()
                duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
                
                self.current_automation["ended_at"] = end_time
                self.current_automation["duration_seconds"] = duration
                self.current_automation["success"] = success
                if error:
                    self.current_automation["error"] = error
                    self.current_automation["status"] = AutomationStatus.ERROR.value
                    self.status = AutomationStatus.ERROR
                else:
                    self.current_automation["status"] = AutomationStatus.STOPPED.value
                    self.status = AutomationStatus.STOPPED
                
                # Move to history
                self.automation_history.append(self.current_automation.copy())
                self.current_automation = None
                self.status = AutomationStatus.IDLE
                self.start_time = None
                
                self._notify_status_change()
                return True
        return False
    
    def get_current_status(self) -> Dict:
        """Get current automation status."""
        with self.lock:
            if self.current_automation:
                elapsed = None
                if self.start_time:
                    elapsed = (datetime.now() - self.start_time).total_seconds()
                
                return {
                    "status": self.status.value,
                    "automation": self.current_automation.copy(),
                    "elapsed_seconds": elapsed,
                    "show_banner": elapsed and elapsed > 10.0  # Show banner if > 10 seconds
                }
            else:
                return {
                    "status": AutomationStatus.IDLE.value,
                    "automation": None,
                    "elapsed_seconds": None,
                    "show_banner": False
                }
    
    def get_automation_history(self, limit: int = 10) -> list:
        """Get recent automation history."""
        with self.lock:
            return self.automation_history[-limit:]
    
    def register_status_callback(self, callback: callable) -> bool:
        """
        Register a callback for status changes.
        
        Args:
            callback: Function to call on status change
            
        Returns:
            True if registered successfully
        """
        with self.lock:
            if callback not in self.status_callbacks:
                self.status_callbacks.append(callback)
                return True
        return False
    
    def _notify_status_change(self):
        """Notify all registered callbacks of status change."""
        status = self.get_current_status()
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception:
                pass  # Ignore callback errors


# Global automation indicator instance
automation_indicator = AutomationIndicator()

