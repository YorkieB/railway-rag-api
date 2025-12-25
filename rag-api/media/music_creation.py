"""
Music Creation

Integration with music generation services (Suno, MusicLM, etc.)
"""

from typing import Optional, Dict, Any, List
import os

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class MusicCreator:
    """Music creation using various APIs."""
    
    def __init__(self, provider: str = "suno"):
        """
        Initialize music creator.
        
        Args:
            provider: Provider name ("suno", "musiclm", "replicate")
        """
        self.provider = provider
        
        if provider == "suno":
            self.api_key = os.getenv("SUNO_API_KEY")
            if not self.api_key:
                raise ValueError("SUNO_API_KEY is required for Suno music creation")
        elif provider == "musiclm":
            # MusicLM might use different auth
            self.api_key = os.getenv("MUSICLM_API_KEY")
        elif provider == "replicate":
            self.api_key = os.getenv("REPLICATE_API_TOKEN")
            if not self.api_key:
                raise ValueError("REPLICATE_API_TOKEN is required for Replicate")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def create(
        self,
        prompt: str,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        duration: Optional[int] = None,
        instrumental: bool = False
    ) -> Dict[str, Any]:
        """
        Create music from text prompt.
        
        Args:
            prompt: Text description of the music
            title: Optional title for the track
            tags: Optional tags (genre, mood, etc.)
            duration: Duration in seconds (if supported)
            instrumental: Whether to create instrumental music
        
        Returns:
            Dictionary with track information and URLs
        """
        if self.provider == "suno":
            return await self._create_suno(prompt, title, tags, duration, instrumental)
        elif self.provider == "replicate":
            return await self._create_replicate(prompt, duration)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _create_suno(
        self,
        prompt: str,
        title: Optional[str],
        tags: Optional[List[str]],
        duration: Optional[int],
        instrumental: bool
    ) -> Dict[str, Any]:
        """Create music using Suno API."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required. Install with: pip install aiohttp")
        
        url = "https://api.suno.ai/v1/generate"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "make_instrumental": instrumental
        }
        
        if title:
            payload["title"] = title
        if tags:
            payload["tags"] = ",".join(tags)
        if duration:
            payload["duration"] = duration
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "provider": "suno",
                        "track_id": data.get("id"),
                        "status": data.get("status", "pending"),
                        "audio_url": data.get("audio_url"),
                        "metadata": data
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Suno API error: {error}")
    
    async def _create_replicate(
        self,
        prompt: str,
        duration: Optional[int]
    ) -> Dict[str, Any]:
        """Create music using Replicate (MusicLM or similar)."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        # Example using MusicLM model on Replicate
        model = "meta/musicgen:671ac645ce5e552cc63a54c2ddb09c0fd96606ad"
        
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": model.split(":")[1] if ":" in model else model,
            "input": {
                "prompt": prompt,
                "duration": duration or 10
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    prediction = await response.json()
                    return {
                        "provider": "replicate",
                        "prediction_id": prediction.get("id"),
                        "status": prediction.get("status", "starting"),
                        "urls": prediction.get("urls", {}),
                        "metadata": prediction
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Replicate API error: {error}")
    
    async def get_status(self, track_id: str) -> Dict[str, Any]:
        """
        Get status of music creation job.
        
        Args:
            track_id: Track or job ID
        
        Returns:
            Status information
        """
        if self.provider == "suno":
            return await self._get_suno_status(track_id)
        elif self.provider == "replicate":
            return await self._get_replicate_status(track_id)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _get_suno_status(self, track_id: str) -> Dict[str, Any]:
        """Get Suno track status."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        url = f"https://api.suno.ai/v1/tracks/{track_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Suno API error: {error}")
    
    async def _get_replicate_status(self, prediction_id: str) -> Dict[str, Any]:
        """Get Replicate prediction status."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        headers = {
            "Authorization": f"Token {self.api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Replicate API error: {error}")


# Global instance
_music_creator: Optional[MusicCreator] = None

def get_music_creator(provider: Optional[str] = None) -> MusicCreator:
    """Get music creator instance."""
    global _music_creator
    if _music_creator is None or (provider and _music_creator.provider != provider):
        _music_creator = MusicCreator(provider=provider or os.getenv("MUSIC_CREATION_PROVIDER", "suno"))
    return _music_creator

