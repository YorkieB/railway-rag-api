/**
 * Music Creator Component
 * 
 * UI for creating music using AI (Suno, MusicLM, etc.)
 */

'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Button } from './Button';

export function MusicCreator() {
  const [prompt, setPrompt] = useState('');
  const [title, setTitle] = useState('');
  const [provider, setProvider] = useState('suno');
  const [duration, setDuration] = useState(30);
  const [instrumental, setInstrumental] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  const handleCreate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${apiBase}/media/music/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          title: title || undefined,
          duration,
          instrumental,
          provider
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create music');
      }

      const data = await response.json();
      setResult(data.result);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async (trackId: string) => {
    try {
      const response = await fetch(`${apiBase}/media/music/status/${trackId}?provider=${provider}`);
      if (response.ok) {
        const data = await response.json();
        setResult(data.status);
      }
    } catch (err) {
      // Ignore errors
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Music Creator</CardTitle>
        <CardDescription>Create music using AI (Suno, MusicLM, Replicate)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Music Description
            </label>
            <textarea
              className="w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe the music you want to create (genre, mood, instruments, etc.)..."
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          {/* Settings */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Provider
              </label>
              <select
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
              >
                <option value="suno">Suno</option>
                <option value="replicate">Replicate (MusicLM)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Duration (seconds)
              </label>
              <input
                type="number"
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value) || 30)}
                min={10}
                max={300}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Title (optional)
              </label>
              <input
                type="text"
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Track title"
              />
            </div>
          </div>

          {/* Instrumental Toggle */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="instrumental"
              checked={instrumental}
              onChange={(e) => setInstrumental(e.target.checked)}
              className="w-4 h-4"
            />
            <label htmlFor="instrumental" className="text-sm text-gray-700 dark:text-gray-300">
              Instrumental (no vocals)
            </label>
          </div>

          {/* Create Button */}
          <Button
            variant="primary"
            size="lg"
            isLoading={loading}
            onClick={handleCreate}
            disabled={!prompt.trim()}
            className="w-full"
          >
            Create Music
          </Button>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">Error: {error}</p>
            </div>
          )}

          {/* Result */}
          {result && (
            <div className="border rounded-lg p-4 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">Creation Status</h3>
              <div className="space-y-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Status: <span className="font-medium">{result.status || 'pending'}</span>
                </p>
                {result.track_id && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Track ID: {result.track_id}
                  </p>
                )}
                {result.audio_url && (
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Audio:</p>
                    <audio controls className="w-full">
                      <source src={result.audio_url} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
                {result.status === 'pending' || result.status === 'processing' ? (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => result.track_id && checkStatus(result.track_id)}
                  >
                    Check Status
                  </Button>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

