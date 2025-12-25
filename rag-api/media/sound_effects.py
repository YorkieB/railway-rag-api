"""
Sound Effects Manager

Manages sound effects library and playback.
"""

from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import json


class SoundEffectsManager:
    """Manages sound effects library."""
    
    def __init__(self, library_path: Optional[str] = None):
        """
        Initialize sound effects manager.
        
        Args:
            library_path: Path to sound effects library directory
        """
        self.library_path = Path(library_path or os.getenv("SOUND_EFFECTS_LIBRARY", "./sound_effects"))
        self.library_path.mkdir(parents=True, exist_ok=True)
        
        # Load library index
        self.index_file = self.library_path / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load sound effects index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {"sounds": {}, "categories": []}
        return {"sounds": {}, "categories": []}
    
    def _save_index(self):
        """Save sound effects index."""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)
    
    def add_sound(
        self,
        name: str,
        file_path: str,
        category: str = "general",
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a sound effect to the library.
        
        Args:
            name: Sound name/ID
            file_path: Path to sound file
            category: Category name
            tags: Optional tags
            description: Optional description
        
        Returns:
            Sound metadata
        """
        sound_path = Path(file_path)
        if not sound_path.exists():
            raise FileNotFoundError(f"Sound file not found: {file_path}")
        
        # Copy to library
        library_file = self.library_path / f"{name}{sound_path.suffix}"
        import shutil
        shutil.copy2(sound_path, library_file)
        
        # Add to index
        sound_data = {
            "name": name,
            "file": str(library_file.name),
            "category": category,
            "tags": tags or [],
            "description": description,
            "duration": self._get_duration(library_file)
        }
        
        self.index["sounds"][name] = sound_data
        
        # Update categories
        if category not in self.index["categories"]:
            self.index["categories"].append(category)
        
        self._save_index()
        
        return sound_data
    
    def _get_duration(self, file_path: Path) -> Optional[float]:
        """Get audio file duration."""
        try:
            import mutagen
            audio_file = mutagen.File(str(file_path))
            if audio_file:
                return audio_file.info.length if hasattr(audio_file.info, "length") else None
        except ImportError:
            pass
        except Exception:
            pass
        return None
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search sound effects.
        
        Args:
            query: Text query to search in name/description
            category: Filter by category
            tags: Filter by tags
        
        Returns:
            List of matching sounds
        """
        results = []
        
        for name, sound in self.index["sounds"].items():
            # Category filter
            if category and sound["category"] != category:
                continue
            
            # Tags filter
            if tags:
                if not any(tag in sound.get("tags", []) for tag in tags):
                    continue
            
            # Query filter
            if query:
                query_lower = query.lower()
                if (query_lower not in name.lower() and
                    query_lower not in sound.get("description", "").lower()):
                    continue
            
            results.append(sound)
        
        return results
    
    def get_sound(self, name: str) -> Optional[Dict[str, Any]]:
        """Get sound by name."""
        return self.index["sounds"].get(name)
    
    def get_sound_path(self, name: str) -> Optional[Path]:
        """Get file path for sound."""
        sound = self.get_sound(name)
        if sound:
            return self.library_path / sound["file"]
        return None
    
    def list_categories(self) -> List[str]:
        """List all categories."""
        return self.index.get("categories", [])
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all sounds."""
        return list(self.index["sounds"].values())
    
    def delete_sound(self, name: str) -> bool:
        """
        Delete a sound from the library.
        
        Args:
            name: Sound name
        
        Returns:
            True if deleted, False if not found
        """
        if name not in self.index["sounds"]:
            return False
        
        sound = self.index["sounds"][name]
        file_path = self.library_path / sound["file"]
        
        # Delete file
        if file_path.exists():
            file_path.unlink()
        
        # Remove from index
        del self.index["sounds"][name]
        self._save_index()
        
        return True


# Global instance
_sound_effects_manager: Optional[SoundEffectsManager] = None

def get_sound_effects_manager() -> SoundEffectsManager:
    """Get sound effects manager instance."""
    global _sound_effects_manager
    if _sound_effects_manager is None:
        _sound_effects_manager = SoundEffectsManager()
    return _sound_effects_manager

