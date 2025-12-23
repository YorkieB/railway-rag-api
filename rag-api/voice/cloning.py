"""
Voice Cloning & Custom Voices

Voice cloning and custom voice training.
"""
import os
from typing import Dict, Optional, List
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()


class VoiceCloning:
    """Handles voice cloning and custom voice creation"""
    
    def __init__(self):
        """Initialize voice cloning"""
        if not ELEVENLABS_AVAILABLE:
            raise ValueError("elevenlabs package not installed. Install with: pip install elevenlabs")
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required")
        self.client = ElevenLabs(api_key=api_key)
    
    def clone_voice(
        self,
        voice_name: str,
        audio_samples: List[bytes],  # Audio file bytes
        description: Optional[str] = None,
        user_id: str = "default"
    ) -> Dict:
        """
        Clone voice from audio samples.
        
        Args:
            voice_name: Name for the cloned voice
            audio_samples: List of audio file bytes (MP3, WAV, etc.)
            description: Optional voice description
            user_id: User identifier
            
        Returns:
            Dict with voice_id and details
        """
        try:
            # Upload audio samples and create voice
            # Note: This is a placeholder - actual implementation depends on ElevenLabs API
            # In production, would use: self.client.voices.add(name=voice_name, files=audio_samples)
            
            voice_id = f"voice_{voice_name.lower().replace(' ', '_')}"
            
            # Estimate cost (ElevenLabs voice cloning pricing)
            cost = 0.0  # Would be calculated based on API pricing
            
            cost_tracker.update_budget(user_id, cost, "voice_cloning")
            
            return {
                "voice_id": voice_id,
                "voice_name": voice_name,
                "description": description,
                "status": "created",
                "cost": cost
            }
        except Exception as e:
            raise Exception(f"Voice cloning failed: {str(e)}")
    
    def list_custom_voices(self, user_id: str = "default") -> Dict:
        """List custom voices for user"""
        try:
            # Get voices from ElevenLabs
            voices = self.client.voices.get_all()
            
            custom_voices = [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, "category", "custom")
                }
                for voice in voices.items
                if getattr(voice, "category", "") == "custom"
            ]
            
            return {
                "voices": custom_voices,
                "count": len(custom_voices)
            }
        except Exception as e:
            raise Exception(f"Failed to list custom voices: {str(e)}")


# Global voice cloning instance
voice_cloning = VoiceCloning()

