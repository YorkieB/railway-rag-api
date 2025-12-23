"""
PDF Export for Conversations and Query Results
"""
from typing import List, Dict, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io


def export_conversation_to_pdf(
    conversation_history: List[Dict],
    project_name: Optional[str] = None,
    output_path: Optional[str] = None
) -> bytes:
    """
    Export conversation history to PDF.
    
    Args:
        conversation_history: List of message dicts with role, content, sources, etc.
        project_name: Optional project name
        output_path: Optional file path (if None, returns bytes)
        
    Returns:
        PDF bytes if output_path is None, otherwise writes to file
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Conversation Export", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#666666'
    )
    
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    if project_name:
        story.append(Paragraph(f"Project: {project_name}", meta_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Messages
    user_style = ParagraphStyle(
        'User',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#0066cc',
        leftIndent=0.2*inch,
        spaceAfter=12
    )
    
    assistant_style = ParagraphStyle(
        'Assistant',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#333333',
        leftIndent=0.2*inch,
        spaceAfter=12
    )
    
    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=9,
        textColor='#666666',
        leftIndent=0.4*inch,
        spaceAfter=6
    )
    
    for msg in conversation_history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "user":
            story.append(Paragraph(f"<b>User:</b> {content}", user_style))
        elif role == "assistant":
            story.append(Paragraph(f"<b>Assistant:</b> {content}", assistant_style))
            
            # Add sources if available
            sources = msg.get("sources", [])
            if sources:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph("<b>Sources:</b>", source_style))
                for source in sources:
                    source_text = f"• {source.get('document', 'Unknown')} (chunk {source.get('chunk', 'N/A')})"
                    story.append(Paragraph(source_text, source_style))
            
            # Add uncertainty info if present
            if msg.get("uncertain"):
                story.append(Paragraph(
                    f"<i>Note: {msg.get('reason', 'Information uncertain')}</i>",
                    source_style
                ))
        
        story.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    return pdf_bytes


def export_query_results_to_pdf(
    query: str,
    answer: str,
    sources: List[Dict],
    memories_used: Optional[List[Dict]] = None,
    project_name: Optional[str] = None,
    output_path: Optional[str] = None
) -> bytes:
    """
    Export query results to PDF.
    
    Args:
        query: User query
        answer: AI answer
        sources: List of source documents
        memories_used: Optional list of memories used
        project_name: Optional project name
        output_path: Optional file path
        
    Returns:
        PDF bytes if output_path is None, otherwise writes to file
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='#1a1a1a',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Query Results Export", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#666666'
    )
    
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    if project_name:
        story.append(Paragraph(f"Project: {project_name}", meta_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Query
    query_style = ParagraphStyle(
        'Query',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#0066cc',
        spaceAfter=12
    )
    
    story.append(Paragraph(f"<b>Query:</b> {query}", query_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Answer
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#333333',
        spaceAfter=20
    )
    
    story.append(Paragraph(f"<b>Answer:</b>", answer_style))
    story.append(Paragraph(answer, answer_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Sources
    if sources:
        source_header_style = ParagraphStyle(
            'SourceHeader',
            parent=styles['Heading3'],
            fontSize=12,
            textColor='#333333',
            spaceAfter=10
        )
        
        story.append(Paragraph("<b>Sources:</b>", source_header_style))
        
        source_style = ParagraphStyle(
            'Source',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#666666',
            leftIndent=0.2*inch,
            spaceAfter=8
        )
        
        for source in sources:
            source_text = f"• {source.get('document', 'Unknown')} (chunk {source.get('chunk', 'N/A')})"
            if source.get('text'):
                source_text += f": {source['text'][:200]}..."
            story.append(Paragraph(source_text, source_style))
        
        story.append(Spacer(1, 0.2*inch))
    
    # Memories
    if memories_used:
        memory_header_style = ParagraphStyle(
            'MemoryHeader',
            parent=styles['Heading3'],
            fontSize=12,
            textColor='#333333',
            spaceAfter=10
        )
        
        story.append(Paragraph("<b>Memories Used:</b>", memory_header_style))
        
        memory_style = ParagraphStyle(
            'Memory',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#666666',
            leftIndent=0.2*inch,
            spaceAfter=8
        )
        
        for memory in memories_used:
            memory_text = f"• {memory.get('content', '')[:200]}..."
            story.append(Paragraph(memory_text, memory_style))
    
    # Build PDF
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    return pdf_bytes

