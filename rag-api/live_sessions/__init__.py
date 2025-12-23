"""
Live Sessions Module

Handles different live session modes: LS1A (audio), LS1B/LS1C (video), LS3 (screen share).
"""

from typing import Dict
from .screen_share import ScreenShareSession

# Store active live sessions (in-memory for MVP)
active_live_sessions: Dict[str, ScreenShareSession] = {}

__all__ = ['ScreenShareSession', 'active_live_sessions']

