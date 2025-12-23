"""
Memory Clustering

Groups related memories together for better organization.
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
import os


class MemoryClustering:
    """Clusters memories by similarity and relationships"""
    
    def __init__(self):
        """Initialize memory clustering"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
        self.memory_storage = MemoryStorage()
    
    def cluster_memories(
        self,
        user_id: str,
        project_id: Optional[str] = None,
        num_clusters: Optional[int] = None
    ) -> Dict:
        """
        Cluster memories by semantic similarity.
        
        Args:
            user_id: User identifier
            project_id: Optional project identifier
            num_clusters: Optional number of clusters (auto-determined if None)
            
        Returns:
            Dict with clusters and their memories
        """
        # Get all memories
        memories = self.memory_storage.list(user_id, project_id)
        
        if len(memories) < 2:
            return {
                "clusters": [],
                "total_memories": len(memories),
                "num_clusters": 0
            }
        
        # Use LLM to cluster memories by semantic similarity
        memory_texts = [f"{i}. {mem.content} ({mem.memory_type})" for i, mem in enumerate(memories)]
        memory_list = "\n".join(memory_texts)
        
        prompt = f"""Group these memories into clusters based on semantic similarity and related topics.

Memories:
{memory_list}

Return a JSON object with "clusters" array, where each cluster has:
- "cluster_id": unique identifier
- "theme": brief theme description
- "memory_indices": array of memory indices (0-based) in this cluster

Group related memories together. Each memory should be in exactly one cluster."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        
        import json
        clustering_result = json.loads(response.choices[0].message.content)
        
        # Map indices back to actual memories
        clusters = []
        for cluster_data in clustering_result.get("clusters", []):
            cluster_memories = [
                memories[idx] for idx in cluster_data.get("memory_indices", [])
                if 0 <= idx < len(memories)
            ]
            clusters.append({
                "cluster_id": cluster_data.get("cluster_id", ""),
                "theme": cluster_data.get("theme", ""),
                "memories": [
                    {
                        "id": mem.id,
                        "content": mem.content,
                        "type": mem.memory_type
                    }
                    for mem in cluster_memories
                ],
                "count": len(cluster_memories)
            })
        
        return {
            "clusters": clusters,
            "total_memories": len(memories),
            "num_clusters": len(clusters)
        }


# Global memory clustering instance
memory_clustering = MemoryClustering()

