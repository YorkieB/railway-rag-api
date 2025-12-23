#!/usr/bin/env python3
"""
Extract text from PDF files in .cursor/plans/ and convert to markdown.
"""
import os
import PyPDF2
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"## Page {page_num}\n\n{text}\n")
            
            return "\n".join(text_content)
    except Exception as e:
        return f"# Error extracting PDF\n\nError: {str(e)}\n\nThis file appears to be a PDF but could not be extracted."

def convert_pdfs_to_markdown():
    """Convert all PDF files in .cursor/plans/ to markdown."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    plans_dir = script_dir
    
    # List of files that are PDFs (based on our earlier findings)
    pdf_files = [
        "AI Hallucination Research and Cursor Software.md",
        "Jarvis Master Specs & Governance.md",
        "Research.pdf.md",
        "Research_Assistant_Knowledge_Base_Design.md",
        "Research_Assistant_Knowledge_Base_Design_V2.md",
        "Both_Approach_V1.md",
        "Both_Approach_V2.md",
        "Both_Approach_V3.md",
        "Can_We_Do_Both.md",
        "Continue_Implementation.md",
        "Implementation_Checklist.md",
        "Lab4_Windows_Companion_Live_Sessions.md",
        "rules___cursor_docs.md",
    ]
    
    converted = []
    errors = []
    
    for filename in pdf_files:
        file_path = plans_dir / filename
        if not file_path.exists():
            print(f"[WARNING] File not found: {filename}")
            continue
        
        # Check if it's actually a PDF by reading first bytes
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(4)
                if first_bytes != b'%PDF':
                    print(f"[SKIP] Skipping {filename} - not a PDF")
                    continue
        except Exception as e:
            print(f"[WARNING] Error checking {filename}: {e}")
            continue
        
        print(f"[EXTRACT] Extracting: {filename}")
        
        # Extract text
        extracted_text = extract_text_from_pdf(file_path)
        
        # Create markdown content with header
        markdown_content = f"# {filename.replace('.md', '')}\n\n"
        markdown_content += "*Extracted from PDF*\n\n"
        markdown_content += "---\n\n"
        markdown_content += extracted_text
        
        # Write back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            converted.append(filename)
            print(f"[SUCCESS] Converted: {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"[ERROR] Error writing {filename}: {e}")
    
    print("\n" + "="*60)
    print(f"[SUCCESS] Successfully converted: {len(converted)} files")
    if errors:
        print(f"[ERROR] Errors: {len(errors)} files")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    print("="*60)

if __name__ == "__main__":
    convert_pdfs_to_markdown()

