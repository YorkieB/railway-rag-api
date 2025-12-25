/**
 * Social Media Poster Component
 * 
 * UI for posting to social media platforms
 */

'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './Card';
import { Button } from './Button';

export function SocialMediaPoster() {
  const [platform, setPlatform] = useState('twitter');
  const [content, setContent] = useState('');
  const [mediaUrls, setMediaUrls] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [recentPosts, setRecentPosts] = useState<any[]>([]);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  const handlePost = async () => {
    if (!content.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const mediaList = mediaUrls.split(',').map(url => url.trim()).filter(url => url);
      
      const response = await fetch(`${apiBase}/media/social/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform,
          content,
          media_urls: mediaList.length > 0 ? mediaList : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to post');
      }

      const data = await response.json();
      setResult(data.result);
      setContent('');
      setMediaUrls('');
      loadRecentPosts();
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const loadRecentPosts = async () => {
    try {
      const response = await fetch(`${apiBase}/media/social/posts?platform=${platform}&limit=5`);
      if (response.ok) {
        const data = await response.json();
        setRecentPosts(data.posts || []);
      }
    } catch (err) {
      // Ignore errors
    }
  };

  React.useEffect(() => {
    loadRecentPosts();
  }, [platform]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Social Media Poster</CardTitle>
        <CardDescription>Post to Twitter, Facebook, Instagram, LinkedIn</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Platform
            </label>
            <select
              className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
            >
              <option value="twitter">Twitter/X</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
              <option value="linkedin">LinkedIn</option>
            </select>
          </div>

          {/* Content Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Content
            </label>
            <textarea
              className="w-full p-3 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="What would you like to post?"
              rows={4}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              maxLength={platform === 'twitter' ? 280 : undefined}
            />
            {platform === 'twitter' && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {content.length}/280 characters
              </p>
            )}
          </div>

          {/* Media URLs */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Media URLs (comma-separated, optional)
            </label>
            <input
              type="text"
              className="w-full p-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100"
              placeholder="https://example.com/image1.jpg, https://example.com/image2.jpg"
              value={mediaUrls}
              onChange={(e) => setMediaUrls(e.target.value)}
            />
          </div>

          {/* Post Button */}
          <Button
            variant="primary"
            size="lg"
            isLoading={loading}
            onClick={handlePost}
            disabled={!content.trim()}
            className="w-full"
          >
            Post to {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </Button>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-800 dark:text-red-200">Error: {error}</p>
            </div>
          )}

          {/* Success Result */}
          {result && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200">
                ✅ Posted successfully! ID: {result.id || 'N/A'}
              </p>
            </div>
          )}

          {/* Recent Posts */}
          {recentPosts.length > 0 && (
            <div className="border-t pt-4 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Recent Posts
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {recentPosts.map((post, idx) => (
                  <div
                    key={idx}
                    className="p-2 border rounded dark:border-gray-700 bg-gray-50 dark:bg-gray-800"
                  >
                    <p className="text-sm text-gray-900 dark:text-gray-100">
                      {post.text || post.message || JSON.stringify(post)}
                    </p>
                    {post.created_time && (
                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {new Date(post.created_time).toLocaleString()}
                      </p>
                    )}
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

