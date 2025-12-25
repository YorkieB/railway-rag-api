/**
 * Voice Chat Component
 * 
 * Real-time voice conversation with Jarvis using:
 * - Microphone input (STT via Deepgram)
 * - Text-to-Speech output (ElevenLabs)
 * - WebSocket connection to LS1A pipeline
 */

import React, { useState, useRef, useEffect } from "react";
import { Button } from "./Button";
import { Card, CardHeader, CardTitle, CardContent } from "./Card";

interface VoiceChatProps {
  userId: string;
  sessionId?: string;
  apiBase?: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: Date;
  isFinal?: boolean;
}

export function VoiceChat({ 
  userId, 
  sessionId: initialSessionId,
  apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000" 
}: VoiceChatProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [audioMinutesUsed, setAudioMinutesUsed] = useState(0);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<HTMLAudioElement[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Create or get session
  const createSession = async () => {
    try {
      const response = await fetch(`${apiBase}/live-sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          mode: "LS1A"
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create session");
      }

      const data = await response.json();
      setSessionId(data.id);
      return data.id;
    } catch (err) {
      setError(`Failed to create session: ${err instanceof Error ? err.message : "Unknown error"}`);
      return null;
    }
  };

  // Connect to WebSocket
  const connectWebSocket = async (sid: string) => {
    try {
      // Convert HTTP to WebSocket URL
      const wsUrl = apiBase.replace("http://", "ws://").replace("https://", "wss://");
      const ws = new WebSocket(`${wsUrl}/ls1a/ws/${sid}?user_id=${userId}`);

      ws.onopen = () => {
        console.log("[VoiceChat] WebSocket connected");
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = async (event) => {
        try {
          if (event.data instanceof Blob) {
            // Binary audio data
            const audioBlob = new Blob([event.data], { type: "audio/mpeg" });
            await playAudio(audioBlob);
          } else {
            // JSON message
            const data = JSON.parse(event.data);
            await handleWebSocketMessage(data);
          }
        } catch (err) {
          console.error("[VoiceChat] Error handling message:", err);
        }
      };

      ws.onerror = (err) => {
        console.error("[VoiceChat] WebSocket error:", err);
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        console.log("[VoiceChat] WebSocket disconnected");
        setIsConnected(false);
        setIsListening(false);
        setIsSpeaking(false);
      };

      wsRef.current = ws;
    } catch (err) {
      setError(`Failed to connect: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = async (data: any) => {
    switch (data.type) {
      case "ready":
        console.log("[VoiceChat] Pipeline ready");
        break;

      case "transcript":
        // Update transcript
        if (data.is_final) {
          // Final transcript - add to messages
          setMessages((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              role: "user",
              text: data.text,
              timestamp: new Date(),
              isFinal: true,
            },
          ]);
          setCurrentTranscript("");
        } else {
          // Partial transcript
          setCurrentTranscript(data.text);
        }
        break;

      case "audio_chunk":
        // Play audio chunk
        if (data.data) {
          const audioBlob = base64ToBlob(data.data, "audio/mpeg");
          await playAudio(audioBlob);
        }
        break;

      case "session_paused":
        setIsListening(false);
        setIsSpeaking(false);
        setError("Session paused");
        break;

      case "budget_warning":
        setError(`Budget warning: ${data.message}`);
        break;

      case "error":
        setError(data.message);
        break;

      default:
        console.log("[VoiceChat] Unknown message type:", data.type);
    }
  };

  // Play audio chunk
  const playAudio = async (audioBlob: Blob) => {
    try {
      setIsSpeaking(true);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        setIsSpeaking(false);
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
      audioQueueRef.current.push(audio);
    } catch (err) {
      console.error("[VoiceChat] Error playing audio:", err);
      setIsSpeaking(false);
    }
  };

  // Convert base64 to Blob
  const base64ToBlob = (base64: string, mimeType: string): Blob => {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  };

  // Start microphone
  const startMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      streamRef.current = stream;

      // Create AudioContext for processing
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      });
      audioContextRef.current = audioContext;

      // Create MediaRecorder for PCM audio
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=pcm",
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
          // Convert to PCM and send
          sendAudioChunk(event.data);
        }
      };

      // Start recording in chunks
      mediaRecorder.start(100); // 100ms chunks
      mediaRecorderRef.current = mediaRecorder;
      setIsListening(true);
    } catch (err) {
      setError(`Microphone access denied: ${err instanceof Error ? err.message : "Unknown error"}`);
    }
  };

  // Send audio chunk to WebSocket
  const sendAudioChunk = async (audioBlob: Blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        // Convert to PCM format (16-bit, 16kHz, mono)
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioData = new Int16Array(arrayBuffer);
        
        // Send as binary
        wsRef.current.send(audioData.buffer);
      } catch (err) {
        console.error("[VoiceChat] Error sending audio:", err);
      }
    }
  };

  // Stop microphone
  const stopMicrophone = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    setIsListening(false);
  };

  // Connect to voice chat
  const connect = async () => {
    setError(null);
    
    // Create session if needed
    let sid = sessionId;
    if (!sid) {
      sid = await createSession();
      if (!sid) return;
    }

    // Connect WebSocket
    await connectWebSocket(sid);

    // Start microphone
    await startMicrophone();
  };

  // Disconnect
  const disconnect = () => {
    stopMicrophone();
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
    setIsListening(false);
    setIsSpeaking(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div
            className={`w-3 h-3 rounded-full ${
              isConnected ? "bg-green-500" : "bg-gray-400"
            }`}
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>

        {isListening && (
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
            <span className="text-sm text-red-600 dark:text-red-400">Listening...</span>
          </div>
        )}

        {isSpeaking && (
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-sm text-blue-600 dark:text-blue-400">Jarvis speaking...</span>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Control Buttons */}
      <div className="flex gap-2">
        {!isConnected ? (
          <Button
            variant="primary"
            onClick={connect}
            disabled={!userId}
          >
            Start Voice Chat
          </Button>
        ) : (
          <Button
            variant="secondary"
            onClick={disconnect}
          >
            Disconnect
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="space-y-2 max-h-64 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        {messages.length === 0 && !currentTranscript && (
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center">
            {isConnected
              ? "Start speaking to have a conversation with Jarvis..."
              : "Connect to start voice chat"}
          </p>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`p-2 rounded ${
              message.role === "user"
                ? "bg-blue-100 dark:bg-blue-900/20 text-blue-900 dark:text-blue-100"
                : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            }`}
          >
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
              {message.role === "user" ? "You" : "Jarvis"}
            </div>
            <div className="text-sm">{message.text}</div>
          </div>
        ))}

        {currentTranscript && (
          <div className="p-2 rounded bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">You (speaking...)</div>
            <div className="text-sm text-blue-900 dark:text-blue-100 italic">
              {currentTranscript}
            </div>
          </div>
        )}
      </div>

      {/* Session Info */}
      {sessionId && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Session ID: {sessionId}
        </div>
      )}
    </div>
  );
}

