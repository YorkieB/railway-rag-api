#!/usr/bin/env python3
"""
Extract text from PDF files using pdfplumber (better for complex PDFs).
"""
import os
import pdfplumber
from pathlib import Path

def extract_text_with_pdfplumber(pdf_path):
    """Extract text from a PDF file using pdfplumber."""
    try:
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    text_content.append(f"## Page {page_num}\n\n{text}\n")
        
        return "\n".join(text_content) if text_content else "No text could be extracted from this PDF."
    except Exception as e:
        return f"# Error extracting PDF\n\nError: {str(e)}\n\nThis file appears to be a PDF but could not be extracted with pdfplumber."

def re_extract_problematic_files():
    """Re-extract files that still appear to be binary."""
    script_dir = Path(__file__).parent
    
    # Files that need re-extraction
    problematic_files = [
        "Lab4_Windows_Companion_Live_Sessions.md",
        "Both_Approach_V1.md",
        "Implementation_Checklist.md",  # Try this one too
    ]
    
    converted = []
    errors = []
    
    for filename in problematic_files:
        file_path = script_dir / filename
        if not file_path.exists():
            print(f"[WARNING] File not found: {filename}")
            continue
        
        # Check if it's actually a PDF by reading first bytes
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(4)
                # If it's already markdown (starts with #), skip
                f.seek(0)
                first_line = f.readline().decode('utf-8', errors='ignore')
                if first_line.strip().startswith('#'):
                    print(f"[SKIP] {filename} is already markdown")
                    continue
                if first_bytes != b'%PDF':
                    print(f"[SKIP] Skipping {filename} - not a PDF")
                    continue
        except Exception as e:
            print(f"[WARNING] Error checking {filename}: {e}")
            continue
        
        print(f"[EXTRACT] Extracting with pdfplumber: {filename}")
        
        # Extract text
        extracted_text = extract_text_with_pdfplumber(file_path)
        
        # Create markdown content with header
        markdown_content = f"# {filename.replace('.md', '')}\n\n"
        markdown_content += "*Extracted from PDF using pdfplumber*\n\n"
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
    re_extract_problematic_files()

