#!/usr/bin/env python3
"""
Fix encoding issues in markdown files that appear binary.
"""
from pathlib import Path

def fix_file_encoding(file_path):
    """Fix encoding issues in a file."""
    try:
        # Try reading as binary first, then decode
        with open(file_path, 'rb') as f:
            content_bytes = f.read()
        
        # Try to decode with UTF-8, ignoring errors
        try:
            content = content_bytes.decode('utf-8')
        except:
            # Try other encodings
            try:
                content = content_bytes.decode('latin-1')
            except:
                content = content_bytes.decode('utf-8', errors='ignore')
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Clean up any remaining binary-like characters
        # Keep only printable characters and common whitespace
        cleaned = ''.join(char for char in content if ord(char) < 0x10000 and (char.isprintable() or char in '\n\r\t'))
        
        # Write back with clean UTF-8
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(cleaned)
        
        return True, None
    except Exception as e:
        return False, str(e)

def fix_problematic_files():
    """Fix encoding in files that appear binary."""
    script_dir = Path(__file__).parent
    
    files_to_fix = [
        "Lab4_Windows_Companion_Live_Sessions.md",
        "Both_Approach_V1.md",
        "Implementation_Checklist.md",
    ]
    
    fixed = []
    errors = []
    
    for filename in files_to_fix:
        file_path = script_dir / filename
        if not file_path.exists():
            print(f"[WARNING] File not found: {filename}")
            continue
        
        print(f"[FIX] Fixing encoding: {filename}")
        success, error = fix_file_encoding(file_path)
        
        if success:
            fixed.append(filename)
            print(f"[SUCCESS] Fixed: {filename}")
        else:
            errors.append((filename, error))
            print(f"[ERROR] Failed to fix {filename}: {error}")
    
    print("\n" + "="*60)
    print(f"[SUCCESS] Fixed encoding in: {len(fixed)} files")
    if errors:
        print(f"[ERROR] Errors: {len(errors)} files")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    print("="*60)

if __name__ == "__main__":
    fix_problematic_files()

