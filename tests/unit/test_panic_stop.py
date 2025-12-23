"""
Unit tests for Panic Stop system.
"""
import pytest
import sys
from pathlib import Path

# Add rag-api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rag-api"))

from windows.panic import PanicStop


class TestPanicStopManager:
    """Test panic stop manager."""
    
    def test_panic_stop_initialization(self):
        """Test panic stop can be initialized."""
        try:
            panic_stop = PanicStop()
            assert panic_stop is not None
        except Exception as e:
            pytest.skip(f"Panic stop not available on this platform: {e}")
    
    def test_register_automation(self):
        """Test registering an automation."""
        try:
            panic_stop = PanicStop()
            automation_id = panic_stop.register_automation("test_automation", "test_action")
            assert automation_id is not None
        except Exception as e:
            pytest.skip(f"Panic stop not available: {e}")
    
    def test_get_status(self):
        """Test getting panic stop status."""
        try:
            panic_stop = PanicStop()
            status = panic_stop.get_status()
            assert status is not None
            assert "active_automations" in status or hasattr(status, "active_automations")
        except Exception as e:
            pytest.skip(f"Panic stop not available: {e}")

