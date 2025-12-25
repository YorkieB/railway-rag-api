"""
Media Integration Module

Provides:
- Image Generation
- Music Creation
- Sound Effects
- Spotify Integration
"""

from .image_generation import ImageGenerator, get_image_generator
from .spotify_integration import SpotifyClient, get_spotify_client
from .music_creation import MusicCreator, get_music_creator
from .sound_effects import SoundEffectsManager, get_sound_effects_manager
from .social_media import SocialMediaController, get_social_media_controller

__all__ = [
    "ImageGenerator",
    "get_image_generator",
    "SpotifyClient",
    "get_spotify_client",
    "MusicCreator",
    "get_music_creator",
    "SoundEffectsManager",
    "get_sound_effects_manager",
    "SocialMediaController",
    "get_social_media_controller",
]

