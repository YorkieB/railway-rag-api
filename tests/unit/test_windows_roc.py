"""
Unit tests for Region-of-Control (ROC)
"""
import pytest
import os
import sys

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.roc import RegionOfControl


class TestRegionOfControl:
    """Test ROC functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.roc = RegionOfControl()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        self.roc.clear_roc()
    
    def test_clear_roc(self):
        """Test clearing ROC."""
        # Set a mock ROC first
        self.roc.active_roc = {
            "window_title": "Test Window",
            "bounds": {"x": 0, "y": 0, "width": 100, "height": 100}
        }
        
        result = self.roc.clear_roc()
        
        assert result["success"] is True
        assert self.roc.get_roc() is None
    
    def test_get_roc_none(self):
        """Test getting ROC when none is set."""
        roc = self.roc.get_roc()
        assert roc is None
    
    def test_is_within_roc_no_roc(self):
        """Test coordinate check when no ROC is set."""
        # When no ROC is set, all coordinates should be allowed
        assert self.roc.is_within_roc(0, 0) is True
        assert self.roc.is_within_roc(1000, 1000) is True
    
    def test_is_within_roc_with_roc(self):
        """Test coordinate check when ROC is set."""
        # Set ROC
        self.roc.active_roc = {
            "window_title": "Test Window",
            "bounds": {"x": 100, "y": 100, "width": 200, "height": 200}
        }
        
        # Coordinates within ROC
        assert self.roc.is_within_roc(150, 150) is True
        assert self.roc.is_within_roc(100, 100) is True  # Top-left corner
        assert self.roc.is_within_roc(300, 300) is True  # Bottom-right corner
        
        # Coordinates outside ROC
        assert self.roc.is_within_roc(50, 50) is False
        assert self.roc.is_within_roc(350, 350) is False
    
    def test_filter_elements_by_roc(self):
        """Test filtering elements by ROC."""
        # Set ROC
        self.roc.active_roc = {
            "window_title": "Test Window",
            "bounds": {"x": 100, "y": 100, "width": 200, "height": 200}
        }
        
        elements = [
            {"x": 150, "y": 150, "name": "element1"},  # Within ROC
            {"x": 50, "y": 50, "name": "element2"},    # Outside ROC
            {"x": 250, "y": 250, "name": "element3"},  # Within ROC
            {"x": 350, "y": 350, "name": "element4"}   # Outside ROC
        ]
        
        filtered = self.roc.filter_elements_by_roc(elements)
        
        assert len(filtered) == 2
        assert filtered[0]["name"] == "element1"
        assert filtered[1]["name"] == "element3"
    
    def test_filter_elements_no_roc(self):
        """Test filtering elements when no ROC is set."""
        elements = [
            {"x": 150, "y": 150, "name": "element1"},
            {"x": 50, "y": 50, "name": "element2"}
        ]
        
        filtered = self.roc.filter_elements_by_roc(elements)
        
        # When no ROC, all elements should be returned
        assert len(filtered) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

