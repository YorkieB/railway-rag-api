"use client";

import { useState, useRef, useEffect } from "react";
import { createLiveSession, buildWsUrl } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

export function AudioLiveSession() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [audioMinutesUsed, setAudioMinutesUsed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const startSession = async () => {
    try {
      const result = await createLiveSession(API_BASE, {
        user_id: "default",
        mode: "LS1A",
        recording_consent: false,
      });
      
      setSessionId(result.session_id);
      
      // Connect WebSocket
      const ws = new WebSocket(buildWsUrl(API_BASE, result.session_id));
      wsRef.current = ws;
      
      ws.onopen = () => {
        setIsConnected(true);
        startAudioCapture();
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "transcript") {
          setTranscript(data.result.transcript || "");
          setAudioMinutesUsed(data.result.audio_minutes_used || 0);
        } else if (data.type === "response") {
          setResponse(data.text || "");
        }
      };
      
      ws.onerror = (err) => {
        setError("WebSocket error");
      };
      
      ws.onclose = () => {
        setIsConnected(false);
      };
    } catch (err: any) {
      setError(err.message || "Failed to start session");
    }
  };

  const startAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Convert to base64 and send
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = (reader.result as string).split(",")[1];
            wsRef.current?.send(JSON.stringify({
              type: "audio_chunk",
              audio: base64
            }));
          };
          reader.readAsDataURL(event.data);
        }
      };
      
      // Send audio chunks every 100ms
      mediaRecorder.start(100);
    } catch (err: any) {
      setError("Failed to access microphone: " + err.message);
    }
  };

  const stopSession = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
    if (wsRef.current) {
      wsRef.current.close();
    }
    setIsConnected(false);
    setSessionId(null);
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Audio Live Session (LS1A)</h2>

      {!isConnected ? (
        <button
          onClick={startSession}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          Start Audio Session
        </button>
      ) : (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-green-600 font-semibold">● Live</span>
            <button
              onClick={stopSession}
              className="px-4 py-2 bg-red-600 text-white rounded-lg"
            >
              Stop Session
            </button>
          </div>

          <div className="border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Transcript</h3>
            <p className="text-gray-700">{transcript || "Listening..."}</p>
          </div>

          {response && (
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold mb-2">Response</h3>
              <p className="text-gray-700">{response}</p>
            </div>
          )}

          <div className="text-sm text-gray-600">
            <p>Audio minutes used: {audioMinutesUsed.toFixed(2)} / 60</p>
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

