#!/usr/bin/env python3
"""
Force re-extract problematic PDFs with better encoding handling.
"""
import os
import pdfplumber
from pathlib import Path

def extract_text_force(pdf_path):
    """Force extract text with better encoding."""
    try:
        text_content = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Try multiple extraction methods
                text = page.extract_text()
                if not text or not text.strip():
                    # Try extracting tables and text separately
                    text = page.extract_text(layout=True)
                if text and text.strip():
                    # Clean up encoding issues
                    text = text.encode('utf-8', errors='ignore').decode('utf-8')
                    text_content.append(f"## Page {page_num}\n\n{text}\n")
        
        return "\n".join(text_content) if text_content else "No text could be extracted from this PDF."
    except Exception as e:
        return f"# Error extracting PDF\n\nError: {str(e)}\n\nThis file appears to be a PDF but could not be extracted."

def force_re_extract():
    """Force re-extract the problematic files."""
    script_dir = Path(__file__).parent
    
    problematic_files = [
        "Lab4_Windows_Companion_Live_Sessions.md",
        "Both_Approach_V1.md",
        "Implementation_Checklist.md",
    ]
    
    converted = []
    errors = []
    
    for filename in problematic_files:
        file_path = script_dir / filename
        if not file_path.exists():
            print(f"[WARNING] File not found: {filename}")
            continue
        
        # Check if file starts with PDF header (might be mixed content)
        try:
            with open(file_path, 'rb') as f:
                first_bytes = f.read(4)
                # If it starts with PDF, it's still a PDF
                if first_bytes == b'%PDF':
                    print(f"[EXTRACT] File is still PDF, extracting: {filename}")
                else:
                    # Check if it's already markdown
                    f.seek(0)
                    try:
                        first_line = f.read(100).decode('utf-8', errors='ignore')
                        if first_line.strip().startswith('#'):
                            print(f"[SKIP] {filename} appears to be markdown already")
                            # But let's force re-extract anyway to fix encoding
                            # Read the original PDF if it exists as backup
                            continue
                    except:
                        pass
        except Exception as e:
            print(f"[WARNING] Error checking {filename}: {e}")
            continue
        
        # Try to find original PDF or re-extract
        # Since the file might be partially converted, let's check if we can read it as PDF
        print(f"[EXTRACT] Attempting extraction: {filename}")
        
        try:
            # Try opening as PDF first
            extracted_text = extract_text_force(file_path)
        except:
            # If that fails, the file might already be text but with encoding issues
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Try to decode
                    text = content.decode('utf-8', errors='ignore')
                    if '## Page' in text or '# ' in text:
                        print(f"[INFO] {filename} appears to be markdown but may have encoding issues")
                        # Clean it up
                        extracted_text = text
                    else:
                        raise Exception("Cannot extract as PDF or text")
            except Exception as e:
                errors.append((filename, f"Cannot extract: {str(e)}"))
                print(f"[ERROR] Cannot extract {filename}: {e}")
                continue
        
        # Create clean markdown content
        if not extracted_text.strip().startswith('#'):
            markdown_content = f"# {filename.replace('.md', '')}\n\n"
            markdown_content += "*Extracted from PDF using pdfplumber*\n\n"
            markdown_content += "---\n\n"
            markdown_content += extracted_text
        else:
            # Already has header, just clean encoding
            markdown_content = extracted_text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Write back with explicit UTF-8 encoding
        try:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(markdown_content)
            converted.append(filename)
            print(f"[SUCCESS] Converted: {filename}")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"[ERROR] Error writing {filename}: {e}")
    
    print("\n" + "="*60)
    print(f"[SUCCESS] Successfully processed: {len(converted)} files")
    if errors:
        print(f"[ERROR] Errors: {len(errors)} files")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    print("="*60)

if __name__ == "__main__":
    force_re_extract()

