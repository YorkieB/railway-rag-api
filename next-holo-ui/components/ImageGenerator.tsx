"use client";

import { useState } from "react";
import { generateImage, analyzeImage, getImageUrl, listUserImages, type ImageGenerationRequest, type ImageGenerationResponse } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

export function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [size, setSize] = useState<"1024x1024" | "1792x1024" | "1024x1792">("1024x1024");
  const [quality, setQuality] = useState<"standard" | "hd">("standard");
  const [style, setStyle] = useState<"vivid" | "natural">("vivid");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<ImageGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [userImages, setUserImages] = useState<any[]>([]);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError("Please enter a prompt");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const request: ImageGenerationRequest = {
        prompt,
        size,
        quality,
        style,
        n: 1,
      };

      const result = await generateImage(API_BASE, request);
      setGeneratedImage(result);
      
      // Refresh user images list
      const images = await listUserImages(API_BASE);
      setUserImages(images.images);
    } catch (err: any) {
      setError(err.message || "Failed to generate image");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleLoadImages = async () => {
    try {
      const images = await listUserImages(API_BASE);
      setUserImages(images.images);
    } catch (err: any) {
      setError(err.message || "Failed to load images");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold">Image Generator</h2>

      {/* Generation Form */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the image you want to generate..."
            className="w-full p-3 border rounded-lg"
            rows={3}
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Size</label>
            <select
              value={size}
              onChange={(e) => setSize(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="1024x1024">1024x1024</option>
              <option value="1792x1024">1792x1024</option>
              <option value="1024x1792">1024x1792</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Quality</label>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="standard">Standard</option>
              <option value="hd">HD</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Style</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="vivid">Vivid</option>
              <option value="natural">Natural</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isGenerating ? "Generating..." : "Generate Image"}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Generated Image */}
      {generatedImage && (
        <div className="space-y-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Generated Image</h3>
            <img
              src={getImageUrl(API_BASE, generatedImage.image_id)}
              alt={generatedImage.revised_prompt}
              className="max-w-full rounded-lg"
            />
            <div className="mt-2 text-sm text-gray-600">
              <p><strong>Revised Prompt:</strong> {generatedImage.revised_prompt}</p>
              <p><strong>Cost:</strong> ${generatedImage.cost.toFixed(4)}</p>
              <p><strong>Size:</strong> {generatedImage.size}</p>
            </div>
          </div>
        </div>
      )}

      {/* User Images Gallery */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-xl font-semibold">Your Images</h3>
          <button
            onClick={handleLoadImages}
            className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            Refresh
          </button>
        </div>

        {userImages.length === 0 ? (
          <p className="text-gray-500">No images generated yet</p>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {userImages.map((img) => (
              <div key={img.id} className="border rounded-lg overflow-hidden">
                <img
                  src={getImageUrl(API_BASE, img.id)}
                  alt={img.prompt || "Generated image"}
                  className="w-full h-48 object-cover"
                />
                <div className="p-2 text-sm">
                  <p className="truncate">{img.prompt || "No prompt"}</p>
                  <p className="text-gray-500 text-xs">{new Date(img.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

