# Browser Automation Integration Guide

**Sprint 2.2: Browser Automation Foundation**

This guide explains how to integrate browser automation into your FastAPI application.

---

## Overview

The browser automation module provides:
- **Playwright integration** for browser control
- **AX Tree extraction** for accessibility-first automation
- **Safety guardrails** to prevent dangerous actions
- **Session management** for multiple browser instances

---

## Components

### 1. BrowserSession (`rag-api/browser/browser_session.py`)
- Manages Playwright browser instances
- Handles navigation and page management
- Provides AX tree extraction

### 2. AX Tree (`rag-api/browser/ax_tree.py`)
- Extracts accessibility tree from pages
- Filters and searches tree nodes
- Finds interactive elements

### 3. Safety Checker (`rag-api/browser/safety.py`)
- Domain blocklist (banking, password managers)
- Payment detection
- Action logging

### 4. Browser API (`rag-api/browser/browser_api.py`)
- REST endpoints for browser automation
- Session management
- Navigation and AX tree access

---

## Integration Steps

### Step 1: Install Dependencies

```bash
pip install -r rag-api/requirements-browser.txt
playwright install chromium
```

### Step 2: Include Router in app.py

```python
from fastapi import FastAPI
from rag_api.browser.browser_api import router as browser_router

app = FastAPI()

# Include browser router
app.include_router(browser_router)
```

### Step 3: Configure Safety (Optional)

```python
from rag_api.browser.safety import SafetyChecker

# Custom safety checker
custom_checker = SafetyChecker(
    blocked_domains=["example.com"],
    allowed_domains=None,  # None = use blocklist mode
    enable_payment_detection=True
)

# Override dependency
from rag_api.browser.browser_api import get_safety_checker_dep
app.dependency_overrides[get_safety_checker_dep] = lambda: custom_checker
```

---

## API Endpoints

### POST `/browser/sessions`
Create a new browser session.

**Request:**
```json
{
  "headless": true,
  "browser_type": "chromium"
}
```

**Response:**
```json
{
  "session_id": "session-uuid",
  "is_active": true,
  "current_url": null,
  "title": null
}
```

### GET `/browser/sessions/{session_id}`
Get session status.

### POST `/browser/sessions/{session_id}/navigate`
Navigate to URL.

**Request:**
```json
{
  "url": "https://example.com",
  "wait_until": "networkidle",
  "timeout": 30000
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com",
  "title": "Example Domain",
  "status": 200,
  "error": null,
  "safety_violation": null
}
```

**Safety Violation Response:**
```json
{
  "success": false,
  "error": "Domain example.com is blocked",
  "safety_violation": {
    "type": "blocked_domain",
    "severity": "error",
    "message": "Domain example.com is blocked"
  }
}
```

### GET `/browser/sessions/{session_id}/ax-tree`
Get accessibility tree.

**Query Parameters:**
- `include_hidden` (bool): Include hidden elements (default: false)

**Response:**
```json
{
  "session_id": "session-uuid",
  "tree": {
    "role": "WebArea",
    "name": "Example Domain",
    "children": [
      {
        "role": "button",
        "name": "Click me",
        "selector": "[aria-label=\"Click me\"]",
        "state": {"disabled": false}
      }
    ]
  },
  "interactive_elements": [
    {
      "role": "button",
      "name": "Click me",
      "selector": "[aria-label=\"Click me\"]"
    }
  ]
}
```

### DELETE `/browser/sessions/{session_id}`
Close session.

### GET `/browser/sessions`
List all active sessions.

---

## Usage Examples

### Python Client

```python
import httpx

async with httpx.AsyncClient() as client:
    # Create session
    response = await client.post(
        "http://localhost:8000/browser/sessions",
        json={"headless": True, "browser_type": "chromium"}
    )
    session = response.json()
    session_id = session["session_id"]
    
    # Navigate
    response = await client.post(
        f"http://localhost:8000/browser/sessions/{session_id}/navigate",
        json={"url": "https://example.com"}
    )
    nav_result = response.json()
    
    if nav_result["success"]:
        # Get AX tree
        response = await client.get(
            f"http://localhost:8000/browser/sessions/{session_id}/ax-tree"
        )
        ax_tree = response.json()
        
        # Find interactive elements
        buttons = [
            elem for elem in ax_tree["interactive_elements"]
            if elem["role"] == "button"
        ]
    
    # Close session
    await client.delete(
        f"http://localhost:8000/browser/sessions/{session_id}"
    )
```

### JavaScript/TypeScript Client

```typescript
// Create session
const sessionResponse = await fetch('http://localhost:8000/browser/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ headless: true, browser_type: 'chromium' })
});
const session = await sessionResponse.json();
const sessionId = session.session_id;

// Navigate
const navResponse = await fetch(`http://localhost:8000/browser/sessions/${sessionId}/navigate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://example.com' })
});
const navResult = await navResponse.json();

if (navResult.success) {
  // Get AX tree
  const axResponse = await fetch(
    `http://localhost:8000/browser/sessions/${sessionId}/ax-tree`
  );
  const axTree = await axResponse.json();
  
  // Find buttons
  const buttons = axTree.interactive_elements.filter(
    (elem: any) => elem.role === 'button'
  );
}

// Close session
await fetch(`http://localhost:8000/browser/sessions/${sessionId}`, {
  method: 'DELETE'
});
```

---

## Safety Features

### Blocked Domains

Default blocked patterns:
- `.*\.bank$` - Banking sites
- `.*password.*manager` - Password managers
- `.*paypal\.com` - Payment processors
- `.*checkout` - Checkout pages
- `.*payment` - Payment pages

### Payment Detection

Automatically detects payment-related content:
- Keywords: "credit card", "debit card", "cvv", "billing", etc.
- URL patterns: `/checkout`, `/payment`, etc.

### Action Logging

All actions are logged for audit trail:
- Session creation
- Navigation
- Safety violations
- Session closure

---

## Next Steps

1. **Sprint 2.3: Browser Actions**
   - Click, type, extract actions
   - Plan-Act-Verify-Recover pattern
   - Uncertainty protocol

2. **Production Enhancements**
   - Database session storage
   - Session persistence
   - Enhanced safety rules
   - Metrics collection

---

**Status:** ✅ Ready for integration

