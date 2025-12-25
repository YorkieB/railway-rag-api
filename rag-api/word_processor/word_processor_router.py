"""
Word Processor REST API Router
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from .document import Document, DocumentFormat, Paragraph
from .editor import DocumentEditor
from .formatter import DocumentFormatter

router = APIRouter(prefix="/word-processor", tags=["word-processor"])

# In-memory document storage (in production, use database)
_documents: Dict[str, Document] = {}

# ============================================================================
# Document Management
# ============================================================================

class CreateDocumentRequest(BaseModel):
    title: str
    author: Optional[str] = None

@router.post("/documents")
async def create_document(request: CreateDocumentRequest):
    """Create a new document."""
    doc_id = str(uuid.uuid4())
    document = Document(
        id=doc_id,
        title=request.title,
        author=request.author
    )
    _documents[doc_id] = document
    return {"document_id": doc_id, "document": {
        "id": doc.id,
        "title": doc.title,
        "author": doc.author,
        "created_at": doc.created_at.isoformat(),
        "word_count": doc.word_count()
    }}

@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document by ID."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = _documents[document_id]
    return {
        "id": doc.id,
        "title": doc.title,
        "author": doc.author,
        "created_at": doc.created_at.isoformat(),
        "modified_at": doc.modified_at.isoformat(),
        "paragraphs": [
            {
                "text": p.text,
                "style": p.style,
                "alignment": p.alignment,
                "bold": p.bold,
                "italic": p.italic,
                "underline": p.underline
            }
            for p in doc.paragraphs
        ],
        "tables": [
            {
                "rows": t.rows,
                "headers": t.headers
            }
            for t in doc.tables
        ],
        "word_count": doc.word_count()
    }

@router.get("/documents")
async def list_documents():
    """List all documents."""
    return {
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "author": doc.author,
                "created_at": doc.created_at.isoformat(),
                "modified_at": doc.modified_at.isoformat(),
                "word_count": doc.word_count()
            }
            for doc in _documents.values()
        ]
    }

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del _documents[document_id]
    return {"status": "deleted"}

# ============================================================================
# Document Editing
# ============================================================================

class AddParagraphRequest(BaseModel):
    text: str
    style: Optional[str] = None
    alignment: str = "left"
    font_size: Optional[int] = None
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: Optional[str] = None

@router.post("/documents/{document_id}/paragraphs")
async def add_paragraph(document_id: str, request: AddParagraphRequest):
    """Add a paragraph to the document."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = _documents[document_id]
    para = doc.add_paragraph(
        text=request.text,
        style=request.style,
        alignment=request.alignment,
        font_size=request.font_size,
        bold=request.bold,
        italic=request.italic,
        underline=request.underline,
        color=request.color
    )
    
    return {"paragraph": {
        "text": para.text,
        "style": para.style,
        "alignment": para.alignment
    }}

class UpdateParagraphRequest(BaseModel):
    text: Optional[str] = None
    style: Optional[str] = None
    alignment: Optional[str] = None
    font_size: Optional[int] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    color: Optional[str] = None

@router.put("/documents/{document_id}/paragraphs/{index}")
async def update_paragraph(document_id: str, index: int, request: UpdateParagraphRequest):
    """Update a paragraph."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    editor = DocumentEditor(_documents[document_id])
    kwargs = {k: v for k, v in request.dict().items() if v is not None}
    para = editor.update_paragraph(index, **kwargs)
    
    return {"paragraph": {
        "text": para.text,
        "style": para.style,
        "alignment": para.alignment
    }}

@router.delete("/documents/{document_id}/paragraphs/{index}")
async def delete_paragraph(document_id: str, index: int):
    """Delete a paragraph."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    editor = DocumentEditor(_documents[document_id])
    editor.delete_paragraph(index)
    
    return {"status": "deleted"}

class FindReplaceRequest(BaseModel):
    find: str
    replace: str
    case_sensitive: bool = False

@router.post("/documents/{document_id}/find-replace")
async def find_and_replace(document_id: str, request: FindReplaceRequest):
    """Find and replace text in document."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    editor = DocumentEditor(_documents[document_id])
    count = editor.find_and_replace(
        request.find,
        request.replace,
        request.case_sensitive
    )
    
    return {"replacements": count}

# ============================================================================
# Document Export
# ============================================================================

@router.post("/documents/{document_id}/export")
async def export_document(document_id: str, format: str = "docx"):
    """Export document to file format."""
    if document_id not in _documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = _documents[document_id]
    formatter = DocumentFormatter(doc)
    
    import tempfile
    import os
    
    output_dir = os.getenv("WORD_PROCESSOR_EXPORT_DIR", "./exports")
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{doc.title}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        if format == "docx":
            output_path = os.path.join(output_dir, f"{filename}.docx")
            await formatter.to_docx(output_path)
        elif format == "pdf":
            output_path = os.path.join(output_dir, f"{filename}.pdf")
            await formatter.to_pdf(output_path)
        elif format == "html":
            output_path = os.path.join(output_dir, f"{filename}.html")
            await formatter.to_html(output_path)
        elif format == "markdown":
            output_path = os.path.join(output_dir, f"{filename}.md")
            await formatter.to_markdown(output_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        return {
            "format": format,
            "file_path": output_path,
            "filename": os.path.basename(output_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

