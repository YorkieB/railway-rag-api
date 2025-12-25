"""
Spotify Integration

Control Spotify playback, search, and manage playlists.
"""

from typing import Optional, List, Dict, Any
import os
import base64
import hashlib
import secrets

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


class SpotifyClient:
    """Spotify API client for music control."""
    
    def __init__(self):
        """Initialize Spotify client."""
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/spotify/callback")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are required")
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
    
    async def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Get Spotify authorization URL.
        
        Args:
            state: Optional state parameter for security
        
        Returns:
            Authorization URL
        """
        if not state:
            state = secrets.token_urlsafe(32)
        
        scopes = [
            "user-read-playback-state",
            "user-modify-playback-state",
            "user-read-currently-playing",
            "playlist-read-private",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-library-read",
            "user-library-modify"
        ]
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.spotify.com/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
        
        Returns:
            Token information
        """
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required. Install with: pip install aiohttp")
        
        url = "https://accounts.spotify.com/api/token"
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    self.refresh_token = token_data.get("refresh_token")
                    expires_in = token_data.get("expires_in", 3600)
                    import time
                    self.token_expires_at = time.time() + expires_in
                    return token_data
                else:
                    error = await response.text()
                    raise Exception(f"Failed to exchange token: {error}")
    
    async def _ensure_token(self):
        """Ensure access token is valid."""
        import time
        if not self.access_token or (self.token_expires_at and time.time() >= self.token_expires_at):
            if self.refresh_token:
                await self._refresh_token()
            else:
                raise Exception("No valid access token. Please authorize first.")
    
    async def _refresh_token(self):
        """Refresh access token."""
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        url = "https://accounts.spotify.com/api/token"
        
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    import time
                    self.token_expires_at = time.time() + expires_in
                else:
                    error = await response.text()
                    raise Exception(f"Failed to refresh token: {error}")
    
    async def _api_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request to Spotify."""
        await self._ensure_token()
        
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp is required")
        
        url = f"https://api.spotify.com/v1{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        headers.update(kwargs.pop("headers", {}))
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                if response.status in [200, 201, 204]:
                    if response.status == 204:
                        return {}
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Spotify API error: {error}")
    
    async def get_current_playback(self) -> Optional[Dict[str, Any]]:
        """Get current playback state."""
        try:
            return await self._api_request("GET", "/me/player")
        except Exception:
            return None
    
    async def play(self, device_id: Optional[str] = None, context_uri: Optional[str] = None, uris: Optional[List[str]] = None):
        """Start or resume playback."""
        data = {}
        if context_uri:
            data["context_uri"] = context_uri
        if uris:
            data["uris"] = uris
        
        params = {}
        if device_id:
            params["device_id"] = device_id
        
        await self._api_request("PUT", "/me/player/play", json=data, params=params)
    
    async def pause(self, device_id: Optional[str] = None):
        """Pause playback."""
        params = {}
        if device_id:
            params["device_id"] = device_id
        await self._api_request("PUT", "/me/player/pause", params=params)
    
    async def next_track(self, device_id: Optional[str] = None):
        """Skip to next track."""
        params = {}
        if device_id:
            params["device_id"] = device_id
        await self._api_request("POST", "/me/player/next", params=params)
    
    async def previous_track(self, device_id: Optional[str] = None):
        """Skip to previous track."""
        params = {}
        if device_id:
            params["device_id"] = device_id
        await self._api_request("POST", "/me/player/previous", params=params)
    
    async def set_volume(self, volume_percent: int, device_id: Optional[str] = None):
        """Set playback volume (0-100)."""
        params = {"volume_percent": volume_percent}
        if device_id:
            params["device_id"] = device_id
        await self._api_request("PUT", "/me/player/volume", params=params)
    
    async def search(self, query: str, types: List[str] = ["track"], limit: int = 20) -> Dict[str, Any]:
        """Search for tracks, artists, albums, playlists."""
        params = {
            "q": query,
            "type": ",".join(types),
            "limit": limit
        }
        return await self._api_request("GET", "/search", params=params)
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get available devices."""
        response = await self._api_request("GET", "/me/player/devices")
        return response.get("devices", [])


# Global instance
_spotify_client: Optional[SpotifyClient] = None

def get_spotify_client() -> SpotifyClient:
    """Get Spotify client instance."""
    global _spotify_client
    if _spotify_client is None:
        _spotify_client = SpotifyClient()
    return _spotify_client

