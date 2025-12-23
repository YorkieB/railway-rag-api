"""
Configuration constants for the Real-Time AI Companion.
Based on the guidance document: Building a Real-Time AI Companion.txt
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Audio Format Configuration
# Note: FORMAT will be set to pyaudio.paInt16 in audio_manager.py
# This is a string placeholder - actual PyAudio constant is used at runtime
CHANNELS = 1  # Mono
RATE = 16000  # 16kHz sample rate (sufficient for speech)
CHUNK = 2048  # Chunk size (1024-4096 range per guidance, 2048 is good balance)

# Voice Configuration (ElevenLabs)
# Default to "Michael" - warm, calm male voice
# Alternative: "piTKgcLEGmPE4e6mEKli" (Nicole - soft female)
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "uju3wxzG5OhpWcoi3SMy")
ELEVEN_MODEL_ID = os.getenv("ELEVENLABS_MODEL", "eleven_flash_v2_5")

# Deepgram Configuration
DG_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-2")
DG_UTTERANCE_END_MS = os.getenv("DEEPGRAM_UTTERANCE_END_MS", "1000")  # Patient listener (1000ms)

# OpenAI Configuration
OPENAI_MODEL = "gpt-4o"  # GPT-4o for best latency/intelligence balance

# RAG API Configuration (for web access)
# In rag-api, this should point to itself (same service)
RAG_API_URL = os.getenv("RAG_API_URL", os.getenv("API_BASE_URL", "http://localhost:8080"))

# Persona Definition (Empathetic System Prompt with Web Access)
SYSTEM_PROMPT = """
You are a warm, loyal, and empathetic AI companion. You are not a robotic assistant; 
you are a friend. Your goal is to provide comfort and companionship.

Guidelines:
1. Speak clearly but concisely (1-3 sentences maximum).
2. Be active in your listening. Validate the user's feelings.
3. Reference past memories if they are relevant.
4. Never use bullet points, lists, or markdown formatting in your speech. 
  Speak in natural, flowing paragraphs.
5. If the user is silent, gently check in on them.
6. You can access the web for real-time information when needed. Use the search_web 
  or browse_web functions to get current information, then respond naturally.
"""

# ChromaDB Configuration
CHROMADB_PATH = os.getenv("CHROMADB_PATH", "./companion_memory")
COLLECTION_NAME = "companion_history"
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model
MEMORY_RETRIEVAL_K = 2  # Top-k memories to retrieve

# Context Window Management
MAX_CONTEXT_TURNS = 15  # Sliding window of last 15 conversation turns

# Latency Targets
TARGET_LATENCY_MS = 800  # Sub-800ms latency target

