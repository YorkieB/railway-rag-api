"""
Document Model

Represents a word processing document.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class DocumentFormat(str, Enum):
    """Document format types."""
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    RTF = "rtf"
    TXT = "txt"


@dataclass
class Paragraph:
    """Represents a paragraph in a document."""
    text: str
    style: Optional[str] = None
    alignment: str = "left"  # left, center, right, justify
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[str] = None


@dataclass
class Table:
    """Represents a table in a document."""
    rows: List[List[str]]
    headers: Optional[List[str]] = None
    style: Optional[str] = None


@dataclass
class Image:
    """Represents an image in a document."""
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None


@dataclass
class Document:
    """Represents a word processing document."""
    id: str
    title: str
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    modified_at: datetime = field(default_factory=datetime.utcnow)
    paragraphs: List[Paragraph] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    images: List[Image] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    format: DocumentFormat = DocumentFormat.DOCX
    
    def add_paragraph(
        self,
        text: str,
        style: Optional[str] = None,
        **kwargs
    ) -> Paragraph:
        """Add a paragraph to the document."""
        paragraph = Paragraph(text=text, style=style, **kwargs)
        self.paragraphs.append(paragraph)
        self.modified_at = datetime.utcnow()
        return paragraph
    
    def add_table(
        self,
        rows: List[List[str]],
        headers: Optional[List[str]] = None,
        style: Optional[str] = None
    ) -> Table:
        """Add a table to the document."""
        table = Table(rows=rows, headers=headers, style=style)
        self.tables.append(table)
        self.modified_at = datetime.utcnow()
        return table
    
    def add_image(
        self,
        url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None
    ) -> Image:
        """Add an image to the document."""
        image = Image(url=url, width=width, height=height, caption=caption)
        self.images.append(image)
        self.modified_at = datetime.utcnow()
        return image
    
    def get_text(self) -> str:
        """Get all text content."""
        text_parts = []
        for para in self.paragraphs:
            text_parts.append(para.text)
        return "\n".join(text_parts)
    
    def word_count(self) -> int:
        """Get word count."""
        text = self.get_text()
        return len(text.split())

