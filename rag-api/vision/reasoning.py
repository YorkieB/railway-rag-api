"""
Advanced Vision Reasoning

Multi-step visual reasoning, object tracking, and scene understanding.
"""
import os
from typing import Dict, List, Optional
from openai import OpenAI
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()


class VisionReasoning:
    """Advanced vision reasoning capabilities"""
    
    def __init__(self):
        """Initialize vision reasoning"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    def multi_step_reasoning(
        self,
        images: List[str],  # base64 encoded images
        query: str,
        steps: Optional[List[str]] = None,
        user_id: str = "default"
    ) -> Dict:
        """
        Perform multi-step visual reasoning across multiple images.
        
        Args:
            images: List of base64 encoded images
            query: Reasoning query
            steps: Optional explicit reasoning steps
            user_id: User identifier
            
        Returns:
            Dict with reasoning result and steps
        """
        # Build vision prompt
        if steps:
            prompt = f"""Perform multi-step visual reasoning to answer this query: {query}

Reasoning steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(steps))}

Analyze the images step by step and provide your reasoning."""
        else:
            prompt = f"""Perform multi-step visual reasoning to answer this query: {query}

Analyze the images carefully, break down the reasoning into steps, and provide a comprehensive answer."""
        
        # Prepare image content
        image_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
            for img in images
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *image_content
                    ]
                }
            ],
            max_tokens=1000
        )
        
        reasoning_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Track cost
        cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
        cost_tracker.update_budget(user_id, cost, "vision_reasoning")
        
        return {
            "reasoning": reasoning_text,
            "steps": steps or [],
            "tokens_used": tokens_used,
            "cost": cost,
            "images_analyzed": len(images)
        }
    
    def track_object(
        self,
        images: List[str],  # base64 encoded images (video frames)
        object_description: str,
        user_id: str = "default"
    ) -> Dict:
        """
        Track object across multiple frames.
        
        Args:
            images: List of base64 encoded frames
            object_description: Description of object to track
            user_id: User identifier
            
        Returns:
            Dict with tracking results
        """
        prompt = f"""Track the object described as "{object_description}" across these video frames.

For each frame, identify:
1. Whether the object is present
2. Its approximate location (bounding box coordinates)
3. Any changes in appearance or position

Return a structured analysis of the object's movement and state across frames."""
        
        image_content = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
            for img in images
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *image_content
                    ]
                }
            ],
            max_tokens=1500
        )
        
        tracking_result = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Track cost
        cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
        cost_tracker.update_budget(user_id, cost, "object_tracking")
        
        return {
            "tracking_result": tracking_result,
            "frames_analyzed": len(images),
            "tokens_used": tokens_used,
            "cost": cost
        }
    
    def analyze_scene(
        self,
        image: str,  # base64 encoded image
        analysis_type: str = "comprehensive",  # comprehensive, objects, relationships, actions
        user_id: str = "default"
    ) -> Dict:
        """
        Comprehensive scene analysis.
        
        Args:
            image: Base64 encoded image
            analysis_type: Type of analysis
            user_id: User identifier
            
        Returns:
            Dict with scene analysis
        """
        analysis_prompts = {
            "comprehensive": "Provide a comprehensive scene analysis including objects, relationships, spatial layout, and context.",
            "objects": "Identify and describe all objects in the scene.",
            "relationships": "Analyze relationships and interactions between objects and people.",
            "actions": "Describe actions and activities happening in the scene."
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["comprehensive"])
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800
        )
        
        analysis = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Track cost
        cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
        cost_tracker.update_budget(user_id, cost, "scene_analysis")
        
        return {
            "analysis": analysis,
            "analysis_type": analysis_type,
            "tokens_used": tokens_used,
            "cost": cost
        }


# Global vision reasoning instance
vision_reasoning = VisionReasoning()

