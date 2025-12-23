"""
File Operations
Handles Windows file operations with safety guardrails.
"""
import os
import shutil
from typing import Optional, List, Dict
from pathlib import Path


class FileManager:
    """
    Manages Windows file operations with safety guardrails.
    
    Safety Rules (CC2):
    - File Read: ✅ Allowed (except system dirs)
    - File Write/Delete: ❌ Blocked (requires approval)
    - System directories always blocked
    - Folder allow-list required for reads
    """
    
    def __init__(self):
        """Initialize file manager."""
        # System directories that are always blocked
        self.system_dirs = [
            "C:\\Windows",
            "C:\\System32",
            "C:\\Program Files\\Windows",
            "C:\\ProgramData",
            "C:\\$Recycle.Bin"
        ]
        
        # Default allow-list for file reads (user directories)
        self.default_allow_list = [
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Music")
        ]
    
    def is_system_directory(self, path: str) -> bool:
        """
        Check if path is in a system directory.
        
        Args:
            path: File or directory path
            
        Returns:
            True if path is in system directory
        """
        path_normalized = os.path.normpath(path).lower()
        for sys_dir in self.system_dirs:
            if path_normalized.startswith(sys_dir.lower()):
                return True
        return False
    
    def is_allowed_directory(self, path: str, allow_list: Optional[List[str]] = None) -> bool:
        """
        Check if path is in allowed directory list.
        
        Args:
            path: File or directory path
            allow_list: Optional custom allow-list (defaults to default_allow_list)
            
        Returns:
            True if path is in allowed directory
        """
        if allow_list is None:
            allow_list = self.default_allow_list
        
        path_normalized = os.path.normpath(path)
        for allowed_dir in allow_list:
            allowed_normalized = os.path.normpath(allowed_dir)
            if path_normalized.startswith(allowed_normalized):
                return True
        return False
    
    def read_file(self, file_path: str, allow_list: Optional[List[str]] = None) -> Dict:
        """
        Read file content.
        
        Args:
            file_path: Path to file
            allow_list: Optional custom allow-list
            
        Returns:
            Dict with file content or error
        """
        # Check system directory
        if self.is_system_directory(file_path):
            return {
                "success": False,
                "error": "Access denied: System directory",
                "file_path": file_path
            }
        
        # Check allow-list
        if not self.is_allowed_directory(file_path, allow_list):
            return {
                "success": False,
                "error": "Access denied: File not in allowed directory",
                "file_path": file_path,
                "allowed_directories": allow_list or self.default_allow_list
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found",
                "file_path": file_path
            }
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": "Path is a directory, not a file",
                "file_path": file_path
            }
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": len(content),
                "message": "File read successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
                "file_path": file_path
            }
    
    def write_file(
        self,
        file_path: str,
        content: str,
        require_approval: bool = True
    ) -> Dict:
        """
        Write file (requires approval by default).
        
        Args:
            file_path: Path to file
            content: Content to write
            require_approval: Whether approval is required (default: True)
            
        Returns:
            Dict with write result or approval request
        """
        # Check system directory
        if self.is_system_directory(file_path):
            return {
                "success": False,
                "error": "Access denied: System directory",
                "file_path": file_path,
                "requires_approval": False
            }
        
        # Check if approval is required
        if require_approval:
            return {
                "success": False,
                "error": "File write requires approval",
                "file_path": file_path,
                "requires_approval": True,
                "action": "write",
                "file_size": len(content),
                "message": "User approval required before writing file"
            }
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "size": len(content),
                "message": "File written successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to write file: {str(e)}",
                "file_path": file_path
            }
    
    def delete_file(
        self,
        file_path: str,
        require_approval: bool = True
    ) -> Dict:
        """
        Delete file (requires approval by default).
        
        Args:
            file_path: Path to file
            require_approval: Whether approval is required (default: True)
            
        Returns:
            Dict with delete result or approval request
        """
        # Check system directory
        if self.is_system_directory(file_path):
            return {
                "success": False,
                "error": "Access denied: System directory",
                "file_path": file_path,
                "requires_approval": False
            }
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found",
                "file_path": file_path
            }
        
        # Get file size for approval message
        file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
        
        # Check if approval is required
        if require_approval:
            return {
                "success": False,
                "error": "File delete requires approval",
                "file_path": file_path,
                "requires_approval": True,
                "action": "delete",
                "file_size": file_size,
                "message": f"User approval required before deleting file ({file_size} bytes)"
            }
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "message": "File deleted successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}",
                "file_path": file_path
            }
    
    def list_directory(self, dir_path: str, allow_list: Optional[List[str]] = None) -> Dict:
        """
        List directory contents.
        
        Args:
            dir_path: Path to directory
            allow_list: Optional custom allow-list
            
        Returns:
            Dict with directory listing
        """
        # Check system directory
        if self.is_system_directory(dir_path):
            return {
                "success": False,
                "error": "Access denied: System directory",
                "dir_path": dir_path
            }
        
        # Check allow-list
        if not self.is_allowed_directory(dir_path, allow_list):
            return {
                "success": False,
                "error": "Access denied: Directory not in allowed list",
                "dir_path": dir_path
            }
        
        # Check if directory exists
        if not os.path.exists(dir_path):
            return {
                "success": False,
                "error": "Directory not found",
                "dir_path": dir_path
            }
        
        if not os.path.isdir(dir_path):
            return {
                "success": False,
                "error": "Path is not a directory",
                "dir_path": dir_path
            }
        
        try:
            items = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                items.append({
                    "name": item,
                    "path": item_path,
                    "is_file": os.path.isfile(item_path),
                    "is_dir": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            return {
                "success": True,
                "dir_path": dir_path,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list directory: {str(e)}",
                "dir_path": dir_path
            }


# Global file manager instance
file_manager = FileManager()

