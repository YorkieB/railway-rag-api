import { useState, useEffect } from "react";
import { apiBaseFromEnv, spotifyAuth, listSpotifyPlaylists } from "@/lib/api";

type Props = {
  apiBase: string;
  token: string;
};

export function IntegrationsPanel({ apiBase, token }: Props) {
  const [spotifyConnected, setSpotifyConnected] = useState(false);
  const [spotifyLoading, setSpotifyLoading] = useState(false);
  const [spotifyError, setSpotifyError] = useState<string | null>(null);
  const [playlists, setPlaylists] = useState<any[]>([]);
  const [loadingPlaylists, setLoadingPlaylists] = useState(false);

  useEffect(() => {
    checkSpotifyConnection();
  }, []);

  const checkSpotifyConnection = async () => {
    try {
      setLoadingPlaylists(true);
      const data = await listSpotifyPlaylists(apiBase, "default");
      if (data && data.playlists) {
        setSpotifyConnected(true);
        setPlaylists(data.playlists || []);
      } else {
        setSpotifyConnected(false);
      }
    } catch (error: any) {
      setSpotifyConnected(false);
      setPlaylists([]);
      // Don't show error - just means not connected
    } finally {
      setLoadingPlaylists(false);
    }
  };

  const handleSpotifyAuth = async () => {
    setSpotifyLoading(true);
    setSpotifyError(null);
    try {
      const response = await spotifyAuth(apiBase, "default");
      if (response.auth_url) {
        // Open Spotify OAuth in new window
        window.open(response.auth_url, "spotify-auth", "width=500,height=600");
        // Poll for connection status
        let pollCount = 0;
        const checkInterval = setInterval(async () => {
          pollCount++;
          try {
            await checkSpotifyConnection();
            // Check if connected after refresh
            const data = await listSpotifyPlaylists(apiBase, "default");
            if (data && data.playlists) {
              clearInterval(checkInterval);
            }
          } catch (e) {
            // Continue polling
          }
          // Stop after 30 attempts (60 seconds)
          if (pollCount >= 30) {
            clearInterval(checkInterval);
          }
        }, 2000);
        
        // Stop polling after 60 seconds
        setTimeout(() => clearInterval(checkInterval), 60000);
      }
    } catch (error: any) {
      setSpotifyError(error.message || "Failed to initiate Spotify authentication");
    } finally {
      setSpotifyLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Integrations</h3>
        
        {/* Spotify Integration */}
        <div className="card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Spotify</h4>
              <p className="text-sm text-gray-600 mt-1">
                Connect your Spotify account to create and manage playlists
              </p>
            </div>
            <div className="flex items-center gap-3">
              {spotifyConnected ? (
                <span className="chip bg-green-100 text-green-700">
                  <span className="inline-block h-2 w-2 rounded-full bg-green-500 mr-2" />
                  Connected
                </span>
              ) : (
                <span className="chip bg-gray-100 text-gray-600">
                  <span className="inline-block h-2 w-2 rounded-full bg-gray-400 mr-2" />
                  Not Connected
                </span>
              )}
              <button
                onClick={handleSpotifyAuth}
                disabled={spotifyLoading || spotifyConnected}
                className="btn-primary px-4 py-2 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {spotifyLoading ? "Connecting..." : spotifyConnected ? "Reconnect" : "Connect"}
              </button>
            </div>
          </div>

          {spotifyError && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {spotifyError}
            </div>
          )}

          {spotifyConnected && playlists.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-medium text-gray-700 mb-2">Your Playlists ({playlists.length})</h5>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {playlists.map((playlist: any) => (
                  <div key={playlist.id} className="p-2 bg-gray-50 rounded text-sm">
                    <div className="font-medium text-gray-900">{playlist.name}</div>
                    <div className="text-gray-600 text-xs">
                      {playlist.tracks?.total || 0} tracks
                      {playlist.public !== undefined && (
                        <span className="ml-2">• {playlist.public ? "Public" : "Private"}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {spotifyConnected && playlists.length === 0 && !loadingPlaylists && (
            <div className="text-sm text-gray-600 mt-2">
              No playlists found. Create one in Spotify or use the chat to create playlists.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

