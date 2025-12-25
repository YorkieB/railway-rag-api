"""
Document Editor

Provides editing capabilities for documents.
"""

from typing import Optional, List
from datetime import datetime
from .document import Document, Paragraph, Table, Image


class DocumentEditor:
    """Editor for word processing documents."""
    
    def __init__(self, document: Document):
        """
        Initialize document editor.
        
        Args:
            document: Document to edit
        """
        self.document = document
    
    def insert_paragraph(
        self,
        index: int,
        text: str,
        **kwargs
    ) -> Paragraph:
        """
        Insert paragraph at index.
        
        Args:
            index: Insert position
            text: Paragraph text
            **kwargs: Paragraph formatting options
        
        Returns:
            Created paragraph
        """
        paragraph = Paragraph(text=text, **kwargs)
        self.document.paragraphs.insert(index, paragraph)
        self.document.modified_at = datetime.utcnow()
        return paragraph
    
    def update_paragraph(
        self,
        index: int,
        text: Optional[str] = None,
        **kwargs
    ) -> Paragraph:
        """
        Update paragraph at index.
        
        Args:
            index: Paragraph index
            text: New text (if provided)
            **kwargs: Formatting updates
        
        Returns:
            Updated paragraph
        """
        if index >= len(self.document.paragraphs):
            raise IndexError(f"Paragraph index {index} out of range")
        
        para = self.document.paragraphs[index]
        if text is not None:
            para.text = text
        
        # Update formatting
        for key, value in kwargs.items():
            if hasattr(para, key):
                setattr(para, key, value)
        
        self.document.modified_at = datetime.utcnow()
        return para
    
    def delete_paragraph(self, index: int):
        """Delete paragraph at index."""
        if index >= len(self.document.paragraphs):
            raise IndexError(f"Paragraph index {index} out of range")
        
        del self.document.paragraphs[index]
        self.document.modified_at = datetime.utcnow()
    
    def move_paragraph(self, from_index: int, to_index: int):
        """Move paragraph from one position to another."""
        if from_index >= len(self.document.paragraphs):
            raise IndexError(f"Paragraph index {from_index} out of range")
        
        para = self.document.paragraphs.pop(from_index)
        self.document.paragraphs.insert(to_index, para)
        self.document.modified_at = datetime.utcnow()
    
    def find_and_replace(self, find: str, replace: str, case_sensitive: bool = False) -> int:
        """
        Find and replace text in all paragraphs.
        
        Args:
            find: Text to find
            replace: Replacement text
            case_sensitive: Whether search is case sensitive
        
        Returns:
            Number of replacements made
        """
        count = 0
        
        if not case_sensitive:
            find = find.lower()
        
        for para in self.document.paragraphs:
            text = para.text if case_sensitive else para.text.lower()
            if find in text:
                if not case_sensitive:
                    # Preserve original case
                    import re
                    para.text = re.sub(re.escape(find), replace, para.text, flags=re.IGNORECASE)
                else:
                    para.text = para.text.replace(find, replace)
                count += para.text.count(replace) if case_sensitive else len(re.findall(re.escape(find), para.text, re.IGNORECASE))
        
        if count > 0:
            self.document.modified_at = datetime.utcnow()
        
        return count
    
    def apply_style(self, style_name: str, paragraph_indices: Optional[List[int]] = None):
        """
        Apply style to paragraphs.
        
        Args:
            style_name: Style name
            paragraph_indices: List of paragraph indices (None for all)
        """
        indices = paragraph_indices if paragraph_indices is not None else range(len(self.document.paragraphs))
        
        for idx in indices:
            if idx < len(self.document.paragraphs):
                self.document.paragraphs[idx].style = style_name
        
        self.document.modified_at = datetime.utcnow()

