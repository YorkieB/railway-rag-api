"""
Media Storage

Handles storage and retrieval of generated media files.
"""
import os
import uuid
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path


class MediaStorage:
    """Manages storage of generated media files"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize media storage.
        
        Args:
            storage_path: Base path for media storage (default: ./media_storage)
        """
        self.storage_path = Path(storage_path or os.getenv("MEDIA_STORAGE_PATH", "./media_storage"))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / "images").mkdir(exist_ok=True)
        (self.storage_path / "videos").mkdir(exist_ok=True)
        (self.storage_path / "charts").mkdir(exist_ok=True)
        
        # In-memory metadata store (future: use database)
        self.metadata: Dict[str, Dict] = {}
    
    def save_image(self, image_data: bytes, user_id: str, metadata: Dict) -> str:
        """
        Save generated image to storage.
        
        Args:
            image_data: Image bytes
            user_id: User identifier
            metadata: Image metadata (prompt, size, etc.)
            
        Returns:
            Image ID
        """
        image_id = str(uuid.uuid4())
        image_path = self.storage_path / "images" / f"{image_id}.png"
        
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        # Store metadata
        self.metadata[image_id] = {
            "id": image_id,
            "type": "image",
            "user_id": user_id,
            "path": str(image_path),
            "created_at": datetime.now().isoformat(),
            **metadata
        }
        
        return image_id
    
    def get_image_path(self, image_id: str) -> Optional[Path]:
        """Get image file path by ID"""
        if image_id not in self.metadata:
            return None
        return Path(self.metadata[image_id]["path"])
    
    def get_image_metadata(self, image_id: str) -> Optional[Dict]:
        """Get image metadata by ID"""
        return self.metadata.get(image_id)
    
    def list_user_images(self, user_id: str) -> List[Dict]:
        """List all images for a user"""
        return [
            meta for meta in self.metadata.values()
            if meta.get("type") == "image" and meta.get("user_id") == user_id
        ]
    
    def save_video(self, video_data: bytes, user_id: str, metadata: Dict) -> str:
        """Save generated video to storage"""
        video_id = str(uuid.uuid4())
        video_path = self.storage_path / "videos" / f"{video_id}.mp4"
        
        with open(video_path, "wb") as f:
            f.write(video_data)
        
        self.metadata[video_id] = {
            "id": video_id,
            "type": "video",
            "user_id": user_id,
            "path": str(video_path),
            "created_at": datetime.now().isoformat(),
            **metadata
        }
        
        return video_id
    
    def save_chart(self, chart_data: bytes, user_id: str, metadata: Dict, format: str = "png") -> str:
        """Save generated chart to storage"""
        chart_id = str(uuid.uuid4())
        chart_path = self.storage_path / "charts" / f"{chart_id}.{format}"
        
        with open(chart_path, "wb") as f:
            f.write(chart_data)
        
        self.metadata[chart_id] = {
            "id": chart_id,
            "type": "chart",
            "user_id": user_id,
            "path": str(chart_path),
            "created_at": datetime.now().isoformat(),
            "format": format,
            **metadata
        }
        
        return chart_id


# Global media storage instance
media_storage = MediaStorage()

