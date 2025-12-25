"""
Code Indexer

Indexes code repositories and files.
"""

from typing import List, Optional, Dict
from datetime import datetime
from pathlib import Path
import ast
import re

from .models import IndexedDocument, IndexMetadata, DocumentType


class CodeIndexer:
    """Indexes code files and repositories."""
    
    def __init__(self):
        """Initialize code indexer."""
        self.supported_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h",
            ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".sh",
            ".sql", ".html", ".css", ".json", ".yaml", ".yml", ".xml"
        }
    
    async def index_file(self, file_path: str) -> IndexedDocument:
        """
        Index a code file.
        
        Args:
            file_path: Path to the code file
        
        Returns:
            IndexedDocument
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Extract code structure
        structure = self._extract_structure(file_path, content)
        
        # Create chunks (functions, classes, etc.)
        chunks = self._chunk_code(content, structure)
        
        # Create metadata
        metadata = IndexMetadata(
            document_id=f"code_{path.stem}_{path.stat().st_mtime}",
            document_type=DocumentType.CODE,
            source=str(path.absolute()),
            title=path.name,
            size=path.stat().st_size,
            language=self._detect_language(file_path),
            indexed_at=datetime.utcnow()
        )
        
        return IndexedDocument(
            id=metadata.document_id,
            content=content,
            metadata=metadata,
            chunks=chunks
        )
    
    async def index_repository(self, repo_path: str, exclude_patterns: Optional[List[str]] = None) -> List[IndexedDocument]:
        """
        Index an entire code repository.
        
        Args:
            repo_path: Path to repository root
            exclude_patterns: Patterns to exclude (e.g., ["node_modules", "*.pyc"])
        
        Returns:
            List of IndexedDocument
        """
        if exclude_patterns is None:
            exclude_patterns = ["node_modules", "__pycache__", ".git", "*.pyc", "*.pyo"]
        
        repo_path_obj = Path(repo_path)
        documents = []
        
        for file_path in repo_path_obj.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                # Check if file should be excluded
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                
                try:
                    doc = await self.index_file(str(file_path))
                    documents.append(doc)
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
                    continue
        
        return documents
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".sh": "bash",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml"
        }
        
        return lang_map.get(ext, "unknown")
    
    def _extract_structure(self, file_path: str, content: str) -> Dict:
        """Extract code structure (functions, classes, etc.)."""
        structure = {
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext == ".py":
            # Python AST parsing
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        structure["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args]
                        })
                    elif isinstance(node, ast.ClassDef):
                        structure["classes"].append({
                            "name": node.name,
                            "line": node.lineno
                        })
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        structure["imports"].append(ast.unparse(node))
            except SyntaxError:
                pass
        else:
            # Simple regex-based extraction for other languages
            # Functions
            func_pattern = r"(?:function|def|fn)\s+(\w+)\s*\("
            for match in re.finditer(func_pattern, content):
                structure["functions"].append({
                    "name": match.group(1),
                    "line": content[:match.start()].count("\n") + 1
                })
            
            # Classes
            class_pattern = r"class\s+(\w+)"
            for match in re.finditer(class_pattern, content):
                structure["classes"].append({
                    "name": match.group(1),
                    "line": content[:match.start()].count("\n") + 1
                })
        
        return structure
    
    def _chunk_code(self, content: str, structure: Dict) -> List[str]:
        """Chunk code by functions/classes."""
        chunks = []
        lines = content.split("\n")
        
        # Add full file as first chunk
        chunks.append(content)
        
        # Add individual functions/classes as chunks
        for func in structure.get("functions", []):
            start_line = func["line"] - 1
            # Find end of function (simplified - can be enhanced)
            end_line = min(start_line + 50, len(lines))
            func_chunk = "\n".join(lines[start_line:end_line])
            chunks.append(f"Function: {func['name']}\n{func_chunk}")
        
        for cls in structure.get("classes", []):
            start_line = cls["line"] - 1
            end_line = min(start_line + 100, len(lines))
            cls_chunk = "\n".join(lines[start_line:end_line])
            chunks.append(f"Class: {cls['name']}\n{cls_chunk}")
        
        return chunks

