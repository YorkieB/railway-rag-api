"use client";

import { useState, useEffect } from "react";
import {
  spotifyAuth,
  createSpotifyPlaylist,
  listSpotifyPlaylists,
  searchSpotify,
  smartCreatePlaylist,
  type SpotifyPlaylistCreateRequest,
  type SmartPlaylistRequest,
} from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

export function SpotifyPanel() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [playlists, setPlaylists] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [playlistName, setPlaylistName] = useState("");
  const [playlistDescription, setPlaylistDescription] = useState("");
  const [smartDescription, setSmartDescription] = useState("");
  const [trackCount, setTrackCount] = useState(20);
  const [activeTab, setActiveTab] = useState<"playlists" | "search" | "create" | "smart">("playlists");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkAuth();
    loadPlaylists();
  }, []);

  const checkAuth = async () => {
    try {
      const playlists = await listSpotifyPlaylists(API_BASE);
      setIsAuthenticated(true);
      setPlaylists(playlists.playlists || []);
    } catch {
      setIsAuthenticated(false);
    }
  };

  const loadPlaylists = async () => {
    try {
      const result = await listSpotifyPlaylists(API_BASE);
      setPlaylists(result.playlists || []);
    } catch (err: any) {
      if (err.message?.includes("401") || err.message?.includes("authenticated")) {
        setIsAuthenticated(false);
      } else {
        setError(err.message || "Failed to load playlists");
      }
    }
  };

  const handleAuth = async () => {
    try {
      const result = await spotifyAuth(API_BASE);
      window.location.href = result.auth_url;
    } catch (err: any) {
      setError(err.message || "Failed to initiate auth");
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const result = await searchSpotify(API_BASE, searchQuery, "track", 20);
      setSearchResults(result.results?.tracks?.items || []);
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlaylist = async () => {
    if (!playlistName.trim()) {
      setError("Please enter a playlist name");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const request: SpotifyPlaylistCreateRequest = {
        name: playlistName,
        description: playlistDescription || undefined,
        public: false,
      };

      await createSpotifyPlaylist(API_BASE, request);
      setPlaylistName("");
      setPlaylistDescription("");
      await loadPlaylists();
      setActiveTab("playlists");
    } catch (err: any) {
      setError(err.message || "Failed to create playlist");
    } finally {
      setLoading(false);
    }
  };

  const handleSmartCreate = async () => {
    if (!smartDescription.trim()) {
      setError("Please enter a description");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const request: SmartPlaylistRequest = {
        description: smartDescription,
        track_count: trackCount,
      };

      const result = await smartCreatePlaylist(API_BASE, request);
      setSmartDescription("");
      await loadPlaylists();
      setActiveTab("playlists");
    } catch (err: any) {
      setError(err.message || "Failed to create smart playlist");
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="p-6 space-y-4">
        <h2 className="text-2xl font-bold">Spotify Integration</h2>
        <div className="border rounded-lg p-6 text-center">
          <p className="mb-4">Connect your Spotify account to create and manage playlists</p>
          <button
            onClick={handleAuth}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Connect Spotify
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Spotify Integration</h2>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab("playlists")}
          className={`px-4 py-2 ${activeTab === "playlists" ? "border-b-2 border-blue-600" : ""}`}
        >
          My Playlists
        </button>
        <button
          onClick={() => setActiveTab("search")}
          className={`px-4 py-2 ${activeTab === "search" ? "border-b-2 border-blue-600" : ""}`}
        >
          Search
        </button>
        <button
          onClick={() => setActiveTab("create")}
          className={`px-4 py-2 ${activeTab === "create" ? "border-b-2 border-blue-600" : ""}`}
        >
          Create Playlist
        </button>
        <button
          onClick={() => setActiveTab("smart")}
          className={`px-4 py-2 ${activeTab === "smart" ? "border-b-2 border-blue-600" : ""}`}
        >
          AI Playlist
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Playlists Tab */}
      {activeTab === "playlists" && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold">Your Playlists</h3>
            <button
              onClick={loadPlaylists}
              className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
            >
              Refresh
            </button>
          </div>

          {playlists.length === 0 ? (
            <p className="text-gray-500">No playlists found</p>
          ) : (
            <div className="grid grid-cols-2 gap-4">
              {playlists.map((playlist) => (
                <div key={playlist.id} className="border rounded-lg p-4">
                  <h4 className="font-semibold">{playlist.name}</h4>
                  <p className="text-sm text-gray-600">{playlist.description || "No description"}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {playlist.tracks?.total || 0} tracks
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search Tab */}
      {activeTab === "search" && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search for songs, artists, albums..."
              className="flex-1 p-2 border rounded"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold">Search Results</h3>
              {searchResults.map((track) => (
                <div key={track.id} className="border rounded p-3 flex justify-between items-center">
                  <div>
                    <p className="font-medium">{track.name}</p>
                    <p className="text-sm text-gray-600">
                      {track.artists.map((a: any) => a.name).join(", ")}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">{track.album.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Playlist Tab */}
      {activeTab === "create" && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Playlist Name</label>
            <input
              type="text"
              value={playlistName}
              onChange={(e) => setPlaylistName(e.target.value)}
              placeholder="My New Playlist"
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Description (optional)</label>
            <textarea
              value={playlistDescription}
              onChange={(e) => setPlaylistDescription(e.target.value)}
              placeholder="Playlist description"
              className="w-full p-2 border rounded"
              rows={3}
            />
          </div>

          <button
            onClick={handleCreatePlaylist}
            disabled={loading || !playlistName.trim()}
            className="px-6 py-2 bg-green-600 text-white rounded-lg disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Playlist"}
          </button>
        </div>
      )}

      {/* Smart Playlist Tab */}
      {activeTab === "smart" && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Describe Your Playlist</label>
            <textarea
              value={smartDescription}
              onChange={(e) => setSmartDescription(e.target.value)}
              placeholder="e.g., energetic workout songs from the 90s"
              className="w-full p-3 border rounded-lg"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Number of Tracks</label>
            <input
              type="number"
              value={trackCount}
              onChange={(e) => setTrackCount(parseInt(e.target.value) || 20)}
              min={1}
              max={100}
              className="w-full p-2 border rounded"
            />
          </div>

          <button
            onClick={handleSmartCreate}
            disabled={loading || !smartDescription.trim()}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create AI Playlist"}
          </button>

          <p className="text-sm text-gray-600">
            Jarvis will interpret your description and create a playlist with matching songs.
          </p>
        </div>
      )}
    </div>
  );
}

