"""
Memory Conflict Detection

Detects conflicting or contradictory memories.
"""
from typing import List, Dict, Optional
import sys
import os
# Import MemoryStorage from parent directory's memory.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# Import directly from memory.py file
import importlib.util
memory_path = os.path.join(parent_dir, 'memory.py')
spec = importlib.util.spec_from_file_location("memory_module", memory_path)
memory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_module)
MemoryStorage = memory_module.MemoryStorage
from openai import OpenAI


class MemoryConflictDetector:
    """Detects conflicts and contradictions in memories"""
    
    def __init__(self):
        """Initialize conflict detector"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.memory_storage = MemoryStorage()
    
    def detect_conflicts(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Detect conflicting memories.
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier
            
        Returns:
            Dict with detected conflicts
        """
        memories = self.memory_storage.list(user_id, project_id)
        
        if len(memories) < 2:
            return {
                "conflicts": [],
                "total_memories": len(memories),
                "conflict_count": 0
            }
        
        # Use LLM to detect conflicts
        memory_texts = [f"{i}. {mem.content} ({mem.memory_type})" for i, mem in enumerate(memories)]
        memory_list = "\n".join(memory_texts)
        
        prompt = f"""Analyze these memories and identify any conflicts or contradictions.

Memories:
{memory_list}

Return a JSON object with "conflicts" array, where each conflict has:
- "conflict_id": unique identifier
- "memory_indices": array of indices of conflicting memories (0-based)
- "conflict_type": type of conflict (contradiction, inconsistency, etc.)
- "description": description of the conflict
- "severity": severity level (low, medium, high)

Only report actual conflicts, not just differences."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        import json
        conflict_result = json.loads(response.choices[0].message.content)
        
        # Map indices back to actual memories
        conflicts = []
        for conflict_data in conflict_result.get("conflicts", []):
            conflict_memories = [
                {
                    "id": memories[idx].id,
                    "content": memories[idx].content,
                    "type": memories[idx].memory_type
                }
                for idx in conflict_data.get("memory_indices", [])
                if 0 <= idx < len(memories)
            ]
            conflicts.append({
                "conflict_id": conflict_data.get("conflict_id", ""),
                "memories": conflict_memories,
                "conflict_type": conflict_data.get("conflict_type", ""),
                "description": conflict_data.get("description", ""),
                "severity": conflict_data.get("severity", "medium")
            })
        
        return {
            "conflicts": conflicts,
            "total_memories": len(memories),
            "conflict_count": len(conflicts)
        }


# Global conflict detector instance
memory_conflict_detector = MemoryConflictDetector()

