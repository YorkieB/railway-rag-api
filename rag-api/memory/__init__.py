"""
Advanced Memory System
Memory relationships, expiration, and analytics.
"""

# Import MemoryStorage from parent memory.py
import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
memory_py_path = os.path.join(parent_dir, 'memory.py')
if os.path.exists(memory_py_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("memory_module", memory_py_path)
    memory_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(memory_module)
    MemoryStorage = memory_module.MemoryStorage
    __all__ = ['MemoryStorage']
