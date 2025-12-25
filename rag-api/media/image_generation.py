"""
Image Generation

Supports multiple image generation APIs (OpenAI DALL-E, Stability AI, etc.)
"""

from typing import Optional, List, Dict, Any
import os
import base64
from io import BytesIO

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class ImageGenerator:
    """Image generation using various APIs."""
    
    def __init__(self, provider: str = "openai"):
        """
        Initialize image generator.
        
        Args:
            provider: Provider name ("openai", "stability", "replicate")
        """
        self.provider = provider
        
        if provider == "openai" and HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY is required for OpenAI image generation")
            self.client = AsyncOpenAI(api_key=api_key)
        elif provider == "stability":
            self.api_key = os.getenv("STABILITY_API_KEY")
            if not self.api_key:
                raise ValueError("STABILITY_API_KEY is required for Stability AI")
        elif provider == "replicate":
            self.api_key = os.getenv("REPLICATE_API_TOKEN")
            if not self.api_key:
                raise ValueError("REPLICATE_API_TOKEN is required for Replicate")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        quality: str = "standard",
        style: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate images from text prompt.
        
        Args:
            prompt: Text description of the image
            size: Image size (e.g., "1024x1024", "512x512")
            n: Number of images to generate
            quality: Quality setting ("standard" or "hd")
            style: Optional style parameter
        
        Returns:
            List of image dictionaries with 'url' or 'b64_json' and metadata
        """
        if self.provider == "openai":
            return await self._generate_openai(prompt, size, n, quality)
        elif self.provider == "stability":
            return await self._generate_stability(prompt, size, n, style)
        elif self.provider == "replicate":
            return await self._generate_replicate(prompt, size, n)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    async def _generate_openai(
        self,
        prompt: str,
        size: str,
        n: int,
        quality: str
    ) -> List[Dict[str, Any]]:
        """Generate images using OpenAI DALL-E."""
        if not HAS_OPENAI:
            raise ImportError("openai package is required. Install with: pip install openai")
        
        # Map size to OpenAI format
        size_map = {
            "1024x1024": "1024x1024",
            "512x512": "512x512",
            "256x256": "256x256",
            "1792x1024": "1792x1024",
            "1024x1792": "1024x1792"
        }
        openai_size = size_map.get(size, "1024x1024")
        
        response = await self.client.images.generate(
            model="dall-e-3" if size in ["1792x1024", "1024x1792"] else "dall-e-2",
            prompt=prompt,
            n=1 if "dall-e-3" in str(response.model) else n,  # DALL-E 3 only supports n=1
            size=openai_size,
            quality=quality if quality == "hd" else "standard",
            response_format="url"
        )
        
        images = []
        for img in response.data:
            images.append({
                "url": img.url,
                "revised_prompt": getattr(img, "revised_prompt", None),
                "provider": "openai",
                "model": "dall-e-3" if "dall-e-3" in str(response.model) else "dall-e-2"
            })
        
        return images
    
    async def _generate_stability(
        self,
        prompt: str,
        size: str,
        n: int,
        style: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Generate images using Stability AI."""
        if not HAS_REQUESTS:
            raise ImportError("requests package is required. Install with: pip install requests")
        
        import aiohttp
        
        # Map size to Stability format
        width, height = map(int, size.split("x"))
        
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "image/*"
        }
        
        data = {
            "prompt": prompt,
            "output_format": "png",
            "width": width,
            "height": height,
            "samples": n
        }
        
        if style:
            data["style_preset"] = style
        
        images = []
        async with aiohttp.ClientSession() as session:
            for _ in range(n):
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        # Convert to base64
                        b64 = base64.b64encode(image_data).decode()
                        images.append({
                            "b64_json": b64,
                            "provider": "stability",
                            "format": "png"
                        })
                    else:
                        error = await response.text()
                        raise Exception(f"Stability AI error: {error}")
        
        return images
    
    async def _generate_replicate(
        self,
        prompt: str,
        size: str,
        n: int
    ) -> List[Dict[str, Any]]:
        """Generate images using Replicate."""
        if not HAS_REQUESTS:
            raise ImportError("requests package is required. Install with: pip install requests")
        
        import aiohttp
        
        # Use Stable Diffusion model
        model = "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf"
        
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        
        width, height = map(int, size.split("x"))
        
        images = []
        async with aiohttp.ClientSession() as session:
            for _ in range(n):
                payload = {
                    "version": model.split(":")[1] if ":" in model else model,
                    "input": {
                        "prompt": prompt,
                        "width": width,
                        "height": height
                    }
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 201:
                        prediction = await response.json()
                        # Poll for completion
                        prediction_url = prediction.get("urls", {}).get("get")
                        if prediction_url:
                            # Wait for completion (simplified - in production use proper polling)
                            import asyncio
                            await asyncio.sleep(5)
                            
                            async with session.get(prediction_url, headers=headers) as poll_response:
                                result = await poll_response.json()
                                if result.get("status") == "succeeded":
                                    output_url = result.get("output", [""])[0]
                                    images.append({
                                        "url": output_url,
                                        "provider": "replicate",
                                        "model": model
                                    })
                    else:
                        error = await response.text()
                        raise Exception(f"Replicate error: {error}")
        
        return images


# Global instance
_image_generator: Optional[ImageGenerator] = None

def get_image_generator(provider: Optional[str] = None) -> ImageGenerator:
    """Get image generator instance."""
    global _image_generator
    if _image_generator is None or (provider and _image_generator.provider != provider):
        _image_generator = ImageGenerator(provider=provider or os.getenv("IMAGE_GENERATION_PROVIDER", "openai"))
    return _image_generator

