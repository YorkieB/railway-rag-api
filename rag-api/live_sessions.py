"""
Live Session Management for Screen Share Assist (LS3)
Handles frame sampling, secret detection, blur, and vision analysis.
"""
import base64
import re
import os
from typing import Optional, Dict, List
from datetime import datetime
try:
    from PIL import Image, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
import io
from openai import OpenAI

from models import LiveSession
from cost import CostTracker

# Initialize cost tracker for budget enforcement
cost_tracker = CostTracker()

# Secret detection patterns
SECRET_PATTERNS = {
    "api_key": re.compile(r"(sk-|pk_|AIza|Bearer\s+)[A-Za-z0-9_-]{20,}", re.IGNORECASE),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "password": re.compile(r"(password|pwd|passwd)\s*[:=]\s*\S+", re.IGNORECASE),
}


class ScreenShareSession:
    """
    Manages LS3 screen share session with vision analysis.
    """
    
    def __init__(self, session: LiveSession):
        self.session = session
        self.openai_client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client for vision analysis"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.openai_client = OpenAI(api_key=api_key)
    
    def detect_secrets(self, image_bytes: bytes) -> List[Dict]:
        """
        Detect secret patterns in image (before blur).
        Returns list of regions to blur.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            List of dicts with 'type', 'bounds', 'confidence'
        """
        # For MVP: Simple regex-based detection on image metadata
        # Future: OCR + regex on extracted text
        detected = []
        
        # Note: Full OCR-based secret detection would require:
        # 1. Extract text from image using OCR
        # 2. Run regex patterns on text
        # 3. Get bounding boxes for matched text
        # For now, return empty list (blur will be applied to entire image if needed)
        
        return detected
    
    def blur_secrets(self, image_bytes: bytes, regions: List[Dict]) -> bytes:
        """
        Apply Gaussian blur to secret regions in image.
        
        Args:
            image_bytes: Raw image bytes
            regions: List of regions to blur (from detect_secrets)
            
        Returns:
            Blurred image bytes
        """
        if not PIL_AVAILABLE:
            # If PIL not available, return original
            return image_bytes
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_bytes))
            
            if regions:
                # Blur specific regions
                for region in regions:
                    bounds = region.get("bounds", {})
                    x = bounds.get("x", 0)
                    y = bounds.get("y", 0)
                    w = bounds.get("width", image.width)
                    h = bounds.get("height", image.height)
                    
                    # Extract region
                    region_img = image.crop((x, y, x + w, y + h))
                    # Apply blur (10px Gaussian)
                    blurred_region = region_img.filter(ImageFilter.GaussianBlur(radius=10))
                    # Paste back
                    image.paste(blurred_region, (x, y))
            else:
                # If no specific regions, check entire image for secrets
                # For MVP: Skip blur if no regions detected
                pass
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=85)
            return output.getvalue()
            
        except Exception as e:
            print(f"Error blurring secrets: {e}")
            # Return original if blur fails
            return image_bytes
    
    def process_frame(
        self,
        frame_data: str,  # base64 encoded image
        query: Optional[str] = None,
        mode: str = "describe"  # "describe", "guide", "pin"
    ) -> Dict:
        """
        Process a screen share frame with vision analysis.
        
        Args:
            frame_data: Base64 encoded image
            query: Optional text query
            mode: Analysis mode ("describe", "guide", "pin")
            
        Returns:
            Dict with analysis result, tokens used, and metadata
        """
        # Decode image
        try:
            image_bytes = base64.b64decode(frame_data)
        except Exception as e:
            return {
                "error": f"Failed to decode image: {str(e)}",
                "tokens_used": 0
            }
        
        # Detect secrets
        secret_regions = self.detect_secrets(image_bytes)
        
        # Blur secrets before vision analysis
        blurred_image_bytes = self.blur_secrets(image_bytes, secret_regions)
        
        # Encode blurred image back to base64
        blurred_base64 = base64.b64encode(blurred_image_bytes).decode('utf-8')
        
        # Check vision token budget
        user_id = self.session.user_id
        estimated_tokens = 2500  # Rough estimate per frame
        
        budget_status = cost_tracker.get_budget_status(user_id)
        if budget_status:
            # Check if we're at 80% or 100% of vision budget
            vision_tokens_used = self.session.vision_tokens_used
            vision_limit = self.session.daily_vision_tokens_limit
            
            if vision_tokens_used >= vision_limit:
                return {
                    "error": "Daily vision token budget exceeded",
                    "tokens_used": 0,
                    "budget_exceeded": True
                }
            
            if vision_tokens_used + estimated_tokens > vision_limit * 0.8:
                # Warning at 80%
                pass  # Will include warning in response
        
        # Prepare vision prompt based on mode
        if mode == "describe":
            vision_prompt = """Look at this screenshot and describe what you see in detail. 
            Focus on:
            - UI elements and their states
            - Text content
            - Visual layout
            - Any important details or context
            
            Provide a concise but comprehensive description."""
        elif mode == "guide":
            vision_prompt = """Look at this screenshot and provide a step-by-step guide for the user.
            Format your response as a numbered list of clear, actionable steps.
            Each step should be specific and easy to follow.
            
            If the user asked a question, answer it in the context of what you see."""
        else:  # pin or default
            vision_prompt = """Look at this screenshot and describe what you see. 
            Focus on key elements and their current state."""
        
        if query:
            vision_prompt = f"{vision_prompt}\n\nUser question: {query}"
        
        # Call OpenAI Vision API
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{blurred_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                timeout=30.0
            )
            
            analysis = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else estimated_tokens
            
            # Update session metrics
            self.session.frames_processed += 1
            self.session.vision_tokens_used += tokens_used
            self.session.updated_at = datetime.now()
            
            # Check budget warning
            warning = False
            if self.session.vision_tokens_used >= self.session.daily_vision_tokens_limit * 0.8:
                warning = True
            
            return {
                "analysis": analysis,
                "mode": mode,
                "tokens_used": tokens_used,
                "frames_processed": self.session.frames_processed,
                "vision_tokens_used": self.session.vision_tokens_used,
                "vision_tokens_limit": self.session.daily_vision_tokens_limit,
                "warning": warning,
                "secrets_blurred": len(secret_regions)
            }
            
        except Exception as e:
            return {
                "error": f"Vision analysis failed: {str(e)}",
                "tokens_used": 0
            }


# Store active live sessions (in-memory for MVP)
active_live_sessions: Dict[str, ScreenShareSession] = {}

