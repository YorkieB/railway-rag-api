/**
 * Image Generator Component
 * 
 * UI for generating images using various AI providers
 */

'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Button } from './Button';

interface ImageResult {
  url?: string;
  b64_json?: string;
  provider: string;
  model?: string;
  revised_prompt?: string;
}

export function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [size, setSize] = useState('1024x1024');
  const [provider, setProvider] = useState('openai');
  const [quality, setQuality] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState<ImageResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setImages([]);

    try {
      const response = await fetch(`${apiBase}/media/images/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          size,
          n: 1,
          quality,
          provider
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate image');
      }

      const data = await response.json();
      setImages(data.images || []);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Generation</CardTitle>
        <CardDescription>Generate images using AI (DALL-E, Stability AI, Replicate)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Prompt
            </label>
            <textarea
              className="w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe the image you want to generate..."
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
                <option value="openai">OpenAI DALL-E</option>
                <option value="stability">Stability AI</option>
                <option value="replicate">Replicate</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Size
              </label>
              <select
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={size}
                onChange={(e) => setSize(e.target.value)}
              >
                <option value="256x256">256x256</option>
                <option value="512x512">512x512</option>
                <option value="1024x1024">1024x1024</option>
                <option value="1792x1024">1792x1024</option>
                <option value="1024x1792">1024x1792</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quality
              </label>
              <select
                className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                disabled={provider !== 'openai'}
              >
                <option value="standard">Standard</option>
                <option value="hd">HD</option>
              </select>
            </div>
          </div>

          {/* Generate Button */}
          <Button
            variant="primary"
            size="lg"
            isLoading={loading}
            onClick={handleGenerate}
            disabled={!prompt.trim()}
            className="w-full"
          >
            Generate Image
          </Button>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">Error: {error}</p>
            </div>
          )}

          {/* Generated Images */}
          {images.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Generated Images</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {images.map((image, idx) => (
                  <div key={idx} className="border rounded-lg overflow-hidden dark:border-gray-700">
                    {image.url ? (
                      <img
                        src={image.url}
                        alt={`Generated image ${idx + 1}`}
                        className="w-full h-auto"
                      />
                    ) : image.b64_json ? (
                      <img
                        src={`data:image/png;base64,${image.b64_json}`}
                        alt={`Generated image ${idx + 1}`}
                        className="w-full h-auto"
                      />
                    ) : null}
                    <div className="p-3 bg-gray-50 dark:bg-gray-800">
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        Provider: {image.provider} {image.model && `(${image.model})`}
                      </p>
                      {image.revised_prompt && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          Revised: {image.revised_prompt}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

