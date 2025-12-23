"""
Image Generation

Handles image generation using DALL-E 3 and image analysis using GPT-4 Vision.
"""
import os
import io
import base64
from typing import Optional, Dict, List
from openai import OpenAI
from .storage import media_storage
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()


class ImageGenerator:
    """Handles image generation and editing using DALL-E 3"""
    
    def __init__(self):
        """Initialize image generator"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
        user_id: str = "default"
    ) -> Dict:
        """
        Generate image using DALL-E 3.
        
        Args:
            prompt: Text description of the image
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: Image quality (standard, hd)
            style: Image style (vivid, natural)
            n: Number of images (DALL-E 3 only supports n=1)
            user_id: User identifier
            
        Returns:
            Dict with image_id, url, revised_prompt, and cost
        """
        # DALL-E 3 only supports n=1
        if n > 1:
            n = 1
        
        try:
            # Generate image
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            
            # Download image
            import requests
            image_response = requests.get(image_url)
            image_data = image_response.content
            
            # Estimate cost (DALL-E 3 pricing: $0.04 per image standard, $0.08 HD)
            cost = 0.04 if quality == "standard" else 0.08
            
            # Track cost
            cost_tracker.update_budget(user_id, cost, "image_generation")
            
            # Save to storage
            image_id = media_storage.save_image(
                image_data,
                user_id,
                {
                    "prompt": prompt,
                    "revised_prompt": revised_prompt,
                    "size": size,
                    "quality": quality,
                    "style": style,
                    "cost": cost
                }
            )
            
            return {
                "image_id": image_id,
                "url": image_url,
                "revised_prompt": revised_prompt,
                "cost": cost,
                "size": size,
                "quality": quality,
                "style": style
            }
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def edit_image(
        self,
        image_path: str,
        mask_path: Optional[str],
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        user_id: str = "default"
    ) -> Dict:
        """
        Edit image using DALL-E 2 (DALL-E 3 doesn't support editing).
        
        Note: DALL-E 2 editing requires image and optional mask.
        For DALL-E 3, we'll use variations instead.
        
        Args:
            image_path: Path to image file
            mask_path: Optional path to mask file
            prompt: Edit instruction
            size: Image size
            n: Number of variations
            user_id: User identifier
            
        Returns:
            Dict with image_id, url, and cost
        """
        # DALL-E 2 editing (or use variations for DALL-E 3)
        # For now, we'll implement variations which work with DALL-E 3
        return self.create_variations(image_path, n=n, size=size, user_id=user_id)
    
    def create_variations(
        self,
        image_path: str,
        n: int = 1,
        size: str = "1024x1024",
        user_id: str = "default"
    ) -> Dict:
        """
        Create image variations using DALL-E 2.
        
        Args:
            image_path: Path to image file
            n: Number of variations (1-10)
            size: Image size
            user_id: User identifier
            
        Returns:
            Dict with image_ids, urls, and cost
        """
        try:
            with open(image_path, "rb") as image_file:
                # DALL-E 2 supports variations
                response = self.client.images.create_variation(
                    image=image_file,
                    n=min(n, 10),  # Max 10 variations
                    size=size
                )
            
            # Estimate cost (DALL-E 2: $0.02 per image)
            cost = 0.02 * len(response.data)
            cost_tracker.update_budget(user_id, cost, "image_variations")
            
            image_ids = []
            urls = []
            
            for img_data in response.data:
                # Download image
                import requests
                img_response = requests.get(img_data.url)
                img_data_bytes = img_response.content
                
                # Save to storage
                img_id = media_storage.save_image(
                    img_data_bytes,
                    user_id,
                    {
                        "type": "variation",
                        "original_path": image_path,
                        "size": size,
                        "cost": 0.02
                    }
                )
                image_ids.append(img_id)
                urls.append(img_data.url)
            
            return {
                "image_ids": image_ids,
                "urls": urls,
                "cost": cost,
                "count": len(image_ids)
            }
            
        except Exception as e:
            raise Exception(f"Image variation creation failed: {str(e)}")
    
    def analyze_image(
        self,
        image_path: str,
        prompt: Optional[str] = None,
        user_id: str = "default"
    ) -> Dict:
        """
        Analyze image using GPT-4 Vision.
        
        Args:
            image_path: Path to image file
            prompt: Optional analysis prompt (default: "Describe this image in detail")
            user_id: User identifier
            
        Returns:
            Dict with analysis text and cost
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            analysis_prompt = prompt or "Describe this image in detail, including any text, objects, colors, and composition."
            
            # Use GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            analysis_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Estimate cost
            cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
            cost_tracker.update_budget(user_id, cost, "image_analysis")
            
            return {
                "analysis": analysis_text,
                "tokens_used": tokens_used,
                "cost": cost
            }
            
        except Exception as e:
            raise Exception(f"Image analysis failed: {str(e)}")


# Global image generator instance
image_generator = ImageGenerator()

