"""
Pytest Configuration and Fixtures
"""

import pytest
import os

# Set test environment variables
os.environ.setdefault("MAX_CONTEXT_TOKENS", "100000")
os.environ.setdefault("WARN_THRESHOLD", "0.8")
os.environ.setdefault("RAG_CONFIDENCE_THRESHOLD", "0.6")

