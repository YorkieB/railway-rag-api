/**
 * Spotify Player Component
 * 
 * UI for controlling Spotify playback
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Button } from './Button';

interface PlaybackState {
  is_playing: boolean;
  item?: {
    name: string;
    artists: Array<{ name: string }>;
    album: { name: string; images: Array<{ url: string }> };
  };
  progress_ms: number;
  device?: { name: string };
}

export function SpotifyPlayer() {
  const [authorized, setAuthorized] = useState(false);
  const [playback, setPlayback] = useState<PlaybackState | null>(null);
  const [devices, setDevices] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  useEffect(() => {
    checkAuthorization();
    if (authorized) {
      loadPlaybackState();
      loadDevices();
    }
  }, [authorized]);

  const checkAuthorization = async () => {
    try {
      const response = await fetch(`${apiBase}/media/spotify/playback`);
      if (response.ok) {
        setAuthorized(true);
      }
    } catch (err) {
      setAuthorized(false);
    }
  };

  const handleAuthorize = async () => {
    try {
      const response = await fetch(`${apiBase}/media/spotify/authorize`);
      const data = await response.json();
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const loadPlaybackState = async () => {
    try {
      const response = await fetch(`${apiBase}/media/spotify/playback`);
      if (response.ok) {
        const data = await response.json();
        setPlayback(data.playback);
      }
    } catch (err) {
      // Ignore errors
    }
  };

  const loadDevices = async () => {
    try {
      const response = await fetch(`${apiBase}/media/spotify/devices`);
      if (response.ok) {
        const data = await response.json();
        setDevices(data.devices || []);
      }
    } catch (err) {
      // Ignore errors
    }
  };

  const handlePlay = async () => {
    setLoading(true);
    try {
      await fetch(`${apiBase}/media/spotify/play`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      await loadPlaybackState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePause = async () => {
    setLoading(true);
    try {
      await fetch(`${apiBase}/media/spotify/pause`, { method: 'POST' });
      await loadPlaybackState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    setLoading(true);
    try {
      await fetch(`${apiBase}/media/spotify/next`, { method: 'POST' });
      await loadPlaybackState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePrevious = async () => {
    setLoading(true);
    try {
      await fetch(`${apiBase}/media/spotify/previous`, { method: 'POST' });
      await loadPlaybackState();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/media/spotify/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          types: ['track'],
          limit: 20
        })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.results);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!authorized) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Spotify Player</CardTitle>
          <CardDescription>Control your Spotify playback</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Connect your Spotify account to control playback
            </p>
            <Button variant="primary" onClick={handleAuthorize}>
              Authorize Spotify
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Spotify Player</CardTitle>
        <CardDescription>Control your Spotify playback</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Current Playback */}
          {playback && playback.item && (
            <div className="border rounded-lg p-4 dark:border-gray-700">
              <div className="flex items-center gap-4">
                {playback.item.album.images[0] && (
                  <img
                    src={playback.item.album.images[0].url}
                    alt={playback.item.album.name}
                    className="w-16 h-16 rounded"
                  />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                    {playback.item.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {playback.item.artists.map(a => a.name).join(', ')}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-500">
                    {playback.item.album.name}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="flex items-center justify-center gap-2">
            <Button variant="secondary" onClick={handlePrevious} disabled={loading}>
              ⏮
            </Button>
            {playback?.is_playing ? (
              <Button variant="primary" onClick={handlePause} isLoading={loading}>
                ⏸ Pause
              </Button>
            ) : (
              <Button variant="primary" onClick={handlePlay} isLoading={loading}>
                ▶ Play
              </Button>
            )}
            <Button variant="secondary" onClick={handleNext} disabled={loading}>
              ⏭
            </Button>
          </div>

          {/* Search */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Search Tracks
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                className="flex-1 p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                placeholder="Search for tracks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button variant="primary" onClick={handleSearch} isLoading={loading}>
                Search
              </Button>
            </div>
          </div>

          {/* Search Results */}
          {searchResults && (
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900 dark:text-gray-100">Search Results</h4>
              <div className="max-h-64 overflow-y-auto space-y-2">
                {searchResults.tracks?.items?.map((track: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2 border rounded dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                    onClick={async () => {
                      await fetch(`${apiBase}/media/spotify/play`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          uris: [track.uri]
                        })
                      });
                      await loadPlaybackState();
                    }}
                  >
                    <p className="font-medium text-sm text-gray-900 dark:text-gray-100">
                      {track.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {track.artists.map((a: any) => a.name).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">Error: {error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

