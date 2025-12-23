"""
Spotify Integration

Handles Spotify API integration for playlist management, search, and playback control.
"""
import os
import base64
from typing import Optional, Dict, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from openai import OpenAI
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:3000/spotify/callback")

# In-memory token storage (future: use database)
spotify_tokens: Dict[str, Dict] = {}


class SpotifyClient:
    """Handles Spotify API interactions"""
    
    def __init__(self, user_id: str = "default"):
        """
        Initialize Spotify client for a user.
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Spotify client with OAuth"""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            return None
        
        token_info = spotify_tokens.get(self.user_id)
        
        if token_info:
            self.client = spotipy.Spotify(auth=token_info["access_token"])
        else:
            # Return None if not authenticated
            self.client = None
    
    def get_auth_url(self) -> str:
        """Get Spotify OAuth authorization URL"""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise Exception("Spotify credentials not configured")
        
        scope = "user-read-private user-read-email playlist-modify-public playlist-modify-private user-read-playback-state user-modify-playback-state"
        
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope
        )
        
        return auth_manager.get_authorize_url()
    
    def handle_callback(self, code: str) -> Dict:
        """Handle OAuth callback and store tokens"""
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
            raise Exception("Spotify credentials not configured")
        
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI
        )
        
        token_info = auth_manager.get_access_token(code)
        spotify_tokens[self.user_id] = token_info
        
        self.client = spotipy.Spotify(auth=token_info["access_token"])
        
        return {
            "success": True,
            "user_id": self.user_id,
            "expires_at": token_info.get("expires_at")
        }
    
    def create_playlist(self, name: str, description: Optional[str] = None, public: bool = False, tracks: List[str] = None) -> Dict:
        """Create a new playlist"""
        if not self.client:
            raise Exception("Not authenticated with Spotify")
        
        user = self.client.current_user()
        user_id = user["id"]
        
        playlist = self.client.user_playlist_create(
            user_id,
            name,
            public=public,
            description=description
        )
        
        if tracks:
            self.client.playlist_add_items(playlist["id"], tracks)
        
        return {
            "playlist_id": playlist["id"],
            "name": playlist["name"],
            "tracks_count": len(tracks) if tracks else 0
        }
    
    def search(self, query: str, type: str = "track", limit: int = 20) -> Dict:
        """Search Spotify"""
        if not self.client:
            raise Exception("Not authenticated with Spotify")
        
        results = self.client.search(q=query, type=type, limit=limit)
        
        return {
            "query": query,
            "results": results,
            "count": len(results.get(f"{type}s", {}).get("items", []))
        }
    
    def smart_create_playlist(
        self,
        description: str,
        track_count: int = 20,
        include_genres: Optional[List[str]] = None,
        exclude_genres: Optional[List[str]] = None,
        user_id: str = "default"
    ) -> Dict:
        """
        Create playlist using AI to interpret natural language description.
        
        Args:
            description: Natural language description (e.g., "energetic workout songs")
            track_count: Number of tracks to include
            include_genres: Optional genres to include
            exclude_genres: Optional genres to exclude
            user_id: User identifier
            
        Returns:
            Dict with playlist_id and tracks
        """
        if not self.client:
            raise Exception("Not authenticated with Spotify")
        
        # Use LLM to interpret description and generate search queries
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        prompt = f"""Given this playlist description: "{description}"

Generate {track_count} specific song search queries that would find appropriate tracks.
Return only a JSON array of search query strings, one per line.
Consider genres: {include_genres or 'any'}
Exclude genres: {exclude_genres or 'none'}
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        search_queries = response.choices[0].message.content.strip().split("\n")
        search_queries = [q.strip().strip('"').strip("'") for q in search_queries if q.strip()]
        
        # Search for tracks
        all_tracks = []
        for query in search_queries[:track_count]:
            try:
                results = self.search(query, type="track", limit=1)
                tracks = results.get("results", {}).get("tracks", {}).get("items", [])
                if tracks:
                    all_tracks.append(tracks[0]["uri"])
            except:
                continue
        
        # Create playlist
        playlist = self.create_playlist(
            name=f"AI Playlist: {description[:50]}",
            description=f"Generated from: {description}",
            public=False,
            tracks=all_tracks
        )
        
        # Estimate cost
        tokens_used = response.usage.total_tokens if response.usage else 0
        cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
        cost_tracker.update_budget(user_id, cost, "spotify_smart_playlist")
        
        return {
            **playlist,
            "tracks_added": len(all_tracks),
            "cost": cost
        }


# Global Spotify client factory
def get_spotify_client(user_id: str = "default") -> Optional[SpotifyClient]:
    """Get or create Spotify client for user"""
    return SpotifyClient(user_id)

