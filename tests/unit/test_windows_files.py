"""
Unit tests for Windows File Operations
"""
import pytest
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import rag-api modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../rag-api'))
from windows.files import FileManager


class TestFileManager:
    """Test file management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.file_manager = FileManager()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        self.test_content = "Hello, World!"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_is_system_directory(self):
        """Test system directory detection."""
        assert self.file_manager.is_system_directory("C:\\Windows\\System32") is True
        assert self.file_manager.is_system_directory("C:\\Program Files\\Windows") is True
        assert self.file_manager.is_system_directory(self.temp_dir) is False
    
    def test_is_allowed_directory(self):
        """Test allowed directory checking."""
        # User Documents should be allowed
        docs_path = os.path.expanduser("~\\Documents")
        if os.path.exists(docs_path):
            assert self.file_manager.is_allowed_directory(docs_path) is True
        
        # Temp dir should not be in default allow-list
        assert self.file_manager.is_allowed_directory(self.temp_dir) is False
    
    def test_read_file_success(self):
        """Test reading a file successfully."""
        # Create test file
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        # Add temp dir to allow-list
        result = self.file_manager.read_file(self.test_file, allow_list=[self.temp_dir])
        
        assert result["success"] is True
        assert result["content"] == self.test_content
        assert result["size"] == len(self.test_content)
    
    def test_read_file_system_directory(self):
        """Test reading file in system directory (blocked)."""
        result = self.file_manager.read_file("C:\\Windows\\System32\\config\\sam")
        
        assert result["success"] is False
        assert "system directory" in result["error"].lower()
    
    def test_read_file_not_allowed(self):
        """Test reading file not in allow-list."""
        result = self.file_manager.read_file(self.test_file)
        
        assert result["success"] is False
        assert "not in allowed directory" in result["error"].lower()
    
    def test_read_file_not_found(self):
        """Test reading non-existent file."""
        result = self.file_manager.read_file(os.path.join(self.temp_dir, "nonexistent.txt"), allow_list=[self.temp_dir])
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_write_file_requires_approval(self):
        """Test that file write requires approval by default."""
        result = self.file_manager.write_file(self.test_file, self.test_content, require_approval=True)
        
        assert result["success"] is False
        assert result["requires_approval"] is True
        assert "approval" in result["error"].lower()
    
    def test_write_file_with_approval(self):
        """Test writing file when approval is given."""
        result = self.file_manager.write_file(self.test_file, self.test_content, require_approval=False)
        
        assert result["success"] is True
        assert os.path.exists(self.test_file)
        
        # Verify content
        with open(self.test_file, 'r') as f:
            assert f.read() == self.test_content
    
    def test_delete_file_requires_approval(self):
        """Test that file delete requires approval by default."""
        # Create file first
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        result = self.file_manager.delete_file(self.test_file, require_approval=True)
        
        assert result["success"] is False
        assert result["requires_approval"] is True
        assert "approval" in result["error"].lower()
        # File should still exist
        assert os.path.exists(self.test_file)
    
    def test_delete_file_with_approval(self):
        """Test deleting file when approval is given."""
        # Create file first
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        result = self.file_manager.delete_file(self.test_file, require_approval=False)
        
        assert result["success"] is True
        assert not os.path.exists(self.test_file)
    
    def test_list_directory(self):
        """Test listing directory contents."""
        # Create test files
        file1 = os.path.join(self.temp_dir, "file1.txt")
        file2 = os.path.join(self.temp_dir, "file2.txt")
        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")
        
        result = self.file_manager.list_directory(self.temp_dir, allow_list=[self.temp_dir])
        
        assert result["success"] is True
        assert result["count"] >= 2
        assert any(item["name"] == "file1.txt" for item in result["items"])
        assert any(item["name"] == "file2.txt" for item in result["items"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

