"""
Video Live Session (LS1B/LS1C)

Handles video call modes with local camera.
"""
import os
import asyncio
from typing import Optional, Dict
from datetime import datetime
from openai import OpenAI
from cost import CostTracker
from models import LiveSession

# Initialize cost tracker
cost_tracker = CostTracker()


class VideoLiveSession:
    """
    Manages LS1B/LS1C video live session.
    
    LS1B: Audio + optional camera frames (0.5 fps default)
    LS1C: Audio + avatar/presence (waveform visualization)
    """
    
    def __init__(self, session: LiveSession):
        """
        Initialize video live session.
        
        Args:
            session: LiveSession model instance
        """
        self.session = session
        self.openai_client = None
        self.frame_count = 0
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
    
    async def process_video_frame(
        self,
        frame_data: str,  # base64 encoded image
        frame_rate: float = 0.5  # frames per second
    ) -> Dict:
        """
        Process video frame with vision model.
        
        Args:
            frame_data: Base64 encoded frame image
            frame_rate: Frame sampling rate
            
        Returns:
            Dict with analysis and metadata
        """
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        import base64
        
        # Decode frame
        image_data = base64.b64decode(frame_data)
        
        # Analyze with GPT-4 Vision
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe what you see in this video frame."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{frame_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        
        analysis = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Track cost
        cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
        cost_tracker.update_budget(self.session.user_id, cost, "video_frame_analysis")
        
        self.frame_count += 1
        self.session.frames_processed = self.frame_count
        
        return {
            "analysis": analysis,
            "frame_number": self.frame_count,
            "tokens_used": tokens_used,
            "cost": cost
        }

