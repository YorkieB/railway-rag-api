"""
Quick verification script to check endpoint definitions
"""
import re
import os

def count_endpoints():
    """Count endpoints in app.py"""
    app_path = os.path.join("rag-api", "app.py")
    
    if not os.path.exists(app_path):
        print(f"❌ {app_path} not found")
        return
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count different endpoint types
    decorators = {
        "@app.get": len(re.findall(r'@app\.get\s*\(', content)),
        "@app.post": len(re.findall(r'@app\.post\s*\(', content)),
        "@app.put": len(re.findall(r'@app\.put\s*\(', content)),
        "@app.delete": len(re.findall(r'@app\.delete\s*\(', content)),
        "@app.websocket": len(re.findall(r'@app\.websocket\s*\(', content)),
    }
    
    total = sum(decorators.values())
    
    print("=" * 50)
    print("  ENDPOINT VERIFICATION")
    print("=" * 50)
    print()
    print(f"Total Endpoints: {total}")
    print()
    print("Breakdown:")
    for method, count in decorators.items():
        print(f"  {method}: {count}")
    print()
    
    # Check for V3 endpoints
    v3_patterns = [
        ("Collaboration", r'/collaboration'),
        ("Memory Templates", r'/memory/templates'),
        ("Memory Clustering", r'/memory/cluster'),
        ("Memory Conflicts", r'/memory/conflicts'),
        ("Integrations", r'/integrations'),
        ("Analytics", r'/analytics'),
        ("Document Processing", r'/documents/(ocr|tables|summarize|categorize)'),
        ("Vision Reasoning", r'/vision'),
        ("Agents", r'/agents'),
        ("Voice Cloning", r'/voice'),
    ]
    
    print("V3 Features Check:")
    for name, pattern in v3_patterns:
        matches = len(re.findall(pattern, content))
        status = "[OK]" if matches > 0 else "[--]"
        print(f"  {status} {name}: {matches} endpoint(s)")
    
    print()
    print("=" * 50)

if __name__ == "__main__":
    count_endpoints()

