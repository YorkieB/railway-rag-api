"""
Media Integration REST API Router
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from .image_generation import ImageGenerator, get_image_generator
from .spotify_integration import SpotifyClient, get_spotify_client
from .music_creation import MusicCreator, get_music_creator
from .sound_effects import SoundEffectsManager, get_sound_effects_manager
from .social_media import SocialMediaController, get_social_media_controller

router = APIRouter(prefix="/media", tags=["media"])

# ============================================================================
# Image Generation Endpoints
# ============================================================================

class ImageGenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    n: int = 1
    quality: str = "standard"
    style: Optional[str] = None
    provider: Optional[str] = None

@router.post("/images/generate")
async def generate_image(
    request: ImageGenerationRequest,
    generator: ImageGenerator = Depends(lambda: get_image_generator(request.provider))
):
    """Generate images from text prompt."""
    try:
        images = await generator.generate(
            prompt=request.prompt,
            size=request.size,
            n=request.n,
            quality=request.quality,
            style=request.style
        )
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Spotify Endpoints
# ============================================================================

@router.get("/spotify/authorize")
async def spotify_authorize():
    """Get Spotify authorization URL."""
    try:
        client = get_spotify_client()
        url = await client.get_authorization_url()
        return {"authorization_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spotify/callback")
async def spotify_callback(code: str):
    """Handle Spotify OAuth callback."""
    try:
        client = get_spotify_client()
        token_data = await client.exchange_code_for_token(code)
        return {"status": "success", "token_data": token_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spotify/playback")
async def get_playback():
    """Get current playback state."""
    try:
        client = get_spotify_client()
        playback = await client.get_current_playback()
        return {"playback": playback}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PlaybackRequest(BaseModel):
    device_id: Optional[str] = None
    context_uri: Optional[str] = None
    uris: Optional[List[str]] = None

@router.post("/spotify/play")
async def spotify_play(request: PlaybackRequest):
    """Start or resume playback."""
    try:
        client = get_spotify_client()
        await client.play(
            device_id=request.device_id,
            context_uri=request.context_uri,
            uris=request.uris
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spotify/pause")
async def spotify_pause(device_id: Optional[str] = None):
    """Pause playback."""
    try:
        client = get_spotify_client()
        await client.pause(device_id=device_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spotify/next")
async def spotify_next(device_id: Optional[str] = None):
    """Skip to next track."""
    try:
        client = get_spotify_client()
        await client.next_track(device_id=device_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spotify/previous")
async def spotify_previous(device_id: Optional[str] = None):
    """Skip to previous track."""
    try:
        client = get_spotify_client()
        await client.previous_track(device_id=device_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/spotify/volume")
async def spotify_volume(volume_percent: int, device_id: Optional[str] = None):
    """Set playback volume."""
    try:
        client = get_spotify_client()
        await client.set_volume(volume_percent, device_id=device_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SearchRequest(BaseModel):
    query: str
    types: List[str] = ["track"]
    limit: int = 20

@router.post("/spotify/search")
async def spotify_search(request: SearchRequest):
    """Search Spotify."""
    try:
        client = get_spotify_client()
        results = await client.search(request.query, request.types, request.limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spotify/devices")
async def get_devices():
    """Get available devices."""
    try:
        client = get_spotify_client()
        devices = await client.get_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Music Creation Endpoints
# ============================================================================

class MusicCreationRequest(BaseModel):
    prompt: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    duration: Optional[int] = None
    instrumental: bool = False
    provider: Optional[str] = None

@router.post("/music/create")
async def create_music(
    request: MusicCreationRequest,
    creator: MusicCreator = Depends(lambda: get_music_creator(request.provider))
):
    """Create music from text prompt."""
    try:
        result = await creator.create(
            prompt=request.prompt,
            title=request.title,
            tags=request.tags,
            duration=request.duration,
            instrumental=request.instrumental
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/music/status/{track_id}")
async def get_music_status(track_id: str, provider: Optional[str] = None):
    """Get music creation status."""
    try:
        creator = get_music_creator(provider)
        status = await creator.get_status(track_id)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Sound Effects Endpoints
# ============================================================================

@router.post("/sounds/add")
async def add_sound_effect(
    name: str,
    file: UploadFile = File(...),
    category: str = "general",
    tags: Optional[str] = None,
    description: Optional[str] = None
):
    """Add a sound effect to the library."""
    try:
        import tempfile
        import os
        
        manager = get_sound_effects_manager()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Add to library
        tag_list = tags.split(",") if tags else None
        sound = manager.add_sound(name, tmp_path, category, tag_list, description)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {"sound": sound}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SoundSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

@router.post("/sounds/search")
async def search_sounds(request: SoundSearchRequest):
    """Search sound effects."""
    try:
        manager = get_sound_effects_manager()
        results = manager.search(request.query, request.category, request.tags)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sounds/{name}")
async def get_sound(name: str):
    """Get sound effect by name."""
    try:
        manager = get_sound_effects_manager()
        sound = manager.get_sound(name)
        if not sound:
            raise HTTPException(status_code=404, detail="Sound not found")
        return {"sound": sound}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sounds")
async def list_sounds():
    """List all sound effects."""
    try:
        manager = get_sound_effects_manager()
        sounds = manager.list_all()
        return {"sounds": sounds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sounds/{name}")
async def delete_sound(name: str):
    """Delete a sound effect."""
    try:
        manager = get_sound_effects_manager()
        deleted = manager.delete_sound(name)
        if not deleted:
            raise HTTPException(status_code=404, detail="Sound not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Social Media Endpoints
# ============================================================================

class SocialMediaPostRequest(BaseModel):
    content: str
    media_urls: Optional[List[str]] = None
    platform: Optional[str] = None
    page_id: Optional[str] = None
    person_urn: Optional[str] = None

@router.post("/social/post")
async def post_to_social_media(
    request: SocialMediaPostRequest,
    controller: SocialMediaController = Depends(lambda: get_social_media_controller(request.platform))
):
    """Post content to social media."""
    try:
        kwargs = {}
        if request.page_id:
            kwargs["page_id"] = request.page_id
        if request.person_urn:
            kwargs["person_urn"] = request.person_urn
        
        result = await controller.post(
            content=request.content,
            media_urls=request.media_urls,
            **kwargs
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/social/posts")
async def get_social_posts(platform: Optional[str] = None, limit: int = 10):
    """Get recent posts from social media."""
    try:
        controller = get_social_media_controller(platform)
        posts = await controller.get_posts(limit)
        return {"posts": posts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

