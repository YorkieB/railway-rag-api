#!/bin/bash
# Railway startup script for rag-api

# Install all requirements
pip install -r requirements.txt
pip install -r requirements-ls1a.txt || true
pip install -r requirements-browser.txt || true

# Start the application
python -m uvicorn app:app --host 0.0.0.0 --port $PORT

