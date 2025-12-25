"""
Web Indexer

Indexes web content from URLs.
"""

from typing import List, Optional, Dict
from datetime import datetime
import re

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from .models import IndexedDocument, IndexMetadata, DocumentType


class WebIndexer:
    """Indexes web content from URLs."""
    
    def __init__(self):
        """Initialize web indexer."""
        if not HAS_BS4:
            raise ImportError("BeautifulSoup4 is required. Install with: pip install beautifulsoup4")
    
    async def index_url(self, url: str) -> IndexedDocument:
        """
        Index content from a URL.
        
        Args:
            url: URL to index
        
        Returns:
            IndexedDocument
        """
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
            except Exception as e:
                raise Exception(f"Failed to fetch URL: {e}")
        
        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Extract title
        title = soup.title.string if soup.title else url
        
        # Extract metadata
        meta_description = ""
        if soup.find("meta", attrs={"name": "description"}):
            meta_description = soup.find("meta", attrs={"name": "description"}).get("content", "")
        
        # Create chunks
        chunks = self._chunk_text(text)
        
        # Create metadata
        metadata = IndexMetadata(
            document_id=f"web_{hash(url)}",
            document_type=DocumentType.WEB,
            source=url,
            title=title,
            indexed_at=datetime.utcnow(),
            custom_metadata={
                "description": meta_description,
                "url": url
            }
        )
        
        return IndexedDocument(
            id=metadata.document_id,
            content=text,
            metadata=metadata,
            chunks=chunks
        )
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_words + [word]
                current_length = sum(len(w) + 1 for w in current_chunk)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

