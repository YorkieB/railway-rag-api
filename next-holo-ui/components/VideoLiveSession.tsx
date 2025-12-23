"use client";

import { useState, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

async function createLiveSession(apiBase: string, request: any) {
  const res = await fetch(`${apiBase}/live-sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to create session");
  }
  return res.json();
}

function buildWsUrl(apiBase: string, sessionId: string): string {
  const wsBase = apiBase.replace("http://", "ws://").replace("https://", "wss://");
  return `${wsBase}/live-sessions/ws/${sessionId}`;
}

export function VideoLiveSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [mode, setMode] = useState<"LS1B" | "LS1C">("LS1B");
  const [frameAnalysis, setFrameAnalysis] = useState("");
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startSession = async () => {
    try {
      const result = await createLiveSession(API_BASE, {
        user_id: "default",
        mode: mode,
        recording_consent: false,
      });
      
      setSessionId(result.session_id);
      
      // Get camera access
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // Connect WebSocket
      const ws = new WebSocket(buildWsUrl(API_BASE, result.session_id));
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsConnected(true);
        startFrameCapture();
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "frame_analysis") {
          setFrameAnalysis(data.result.analysis || "");
        }
      };
      
      ws.onerror = () => {
        setError("WebSocket error");
      };
      
      ws.onclose = () => {
        setIsConnected(false);
      };
    } catch (err: any) {
      setError(err.message || "Failed to start session");
    }
  };

  const startFrameCapture = () => {
    const canvas = document.createElement("canvas");
    const video = videoRef.current;
    if (!video) return;
    
    const captureFrame = () => {
      if (video.readyState === video.HAVE_ENOUGH_DATA && wsRef.current?.readyState === WebSocket.OPEN) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        if (ctx) {
          ctx.drawImage(video, 0, 0);
          canvas.toBlob((blob) => {
            if (blob) {
              const reader = new FileReader();
              reader.onloadend = () => {
                const base64 = (reader.result as string).split(",")[1];
                wsRef.current?.send(JSON.stringify({
                  type: "video_frame",
                  frame: base64,
                  frame_rate: 0.5  // 0.5 fps default
                }));
              };
              reader.readAsDataURL(blob);
            }
          }, "image/png");
        }
      }
    };
    
    // Capture at 0.5 fps (every 2 seconds)
    const interval = setInterval(captureFrame, 2000);
    
    // Store interval for cleanup
    (wsRef.current as any).frameInterval = interval;
  };

  const stopSession = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (wsRef.current) {
      const interval = (wsRef.current as any).frameInterval;
      if (interval) clearInterval(interval);
      wsRef.current.close();
    }
    setIsConnected(false);
    setSessionId(null);
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Video Live Session (LS1B/LS1C)</h2>

      {!isConnected ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Mode</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as any)}
              className="w-full p-2 border rounded"
            >
              <option value="LS1B">LS1B - Audio + Camera</option>
              <option value="LS1C">LS1C - Audio + Avatar</option>
            </select>
          </div>
          <button
            onClick={startSession}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            Start Video Session
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-green-600 font-semibold">● Live ({mode})</span>
            <button
              onClick={stopSession}
              className="px-4 py-2 bg-red-600 text-white rounded-lg"
            >
              Stop Session
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2">Camera Preview</h3>
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full border rounded-lg"
                style={{ maxHeight: "300px" }}
              />
            </div>

            {frameAnalysis && (
              <div className="border rounded-lg p-4">
                <h3 className="font-semibold mb-2">Frame Analysis</h3>
                <p className="text-sm text-gray-700">{frameAnalysis}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
    </div>
  );
}

