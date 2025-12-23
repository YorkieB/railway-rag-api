import { useCallback, useEffect, useRef, useState } from "react";
import { buildWsUrl } from "@/lib/api";

type LiveEvent =
  | { type: "session_ready"; session_id: string; status?: string }
  | { type: "vision_description"; description: string; timestamp?: number }
  | { type: "audio_response"; status?: string; message?: string }
  | { type: "text_response"; answer: string; sources?: unknown[]; has_vision?: boolean }
  | { type: "error"; message: string }
  | { type: string; [key: string]: unknown };

export function useGeminiLive(apiBase: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<"idle" | "connecting" | "connected" | "error">("idle");
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [lastError, setLastError] = useState<string | null>(null);

  const appendEvent = useCallback((evt: LiveEvent) => {
    setEvents(prev => [...prev, evt]);
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        // ignore
      }
    }
    wsRef.current = null;
    setStatus("idle");
  }, []);

  const connect = useCallback(
    (sessionId: string) => {
      disconnect();
      setStatus("connecting");
      setLastError(null);

      const wsUrl = buildWsUrl(apiBase, sessionId);
      const socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => setStatus("connected");
      socket.onerror = () => {
        setStatus("error");
        setLastError("WebSocket error");
      };
      socket.onclose = () => {
        setStatus("idle");
      };
      socket.onmessage = evt => {
        try {
          const data = JSON.parse(evt.data);
          appendEvent(data);
        } catch (err) {
          appendEvent({ type: "error", message: String(err) });
        }
      };
    },
    [apiBase, appendEvent, disconnect]
  );

  const send = useCallback((payload: unknown) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload));
    }
  }, []);

  const sendText = useCallback(
    (text: string) => send({ type: "text_input", text }),
    [send]
  );

  const sendAudioChunk = useCallback(
    (base64Audio: string, timestamp?: number) =>
      send({ type: "audio_chunk", audio: base64Audio, timestamp }),
    [send]
  );

  const sendVideoFrame = useCallback(
    (base64Image: string, timestamp?: number) =>
      send({ type: "video_frame", image: base64Image, timestamp }),
    [send]
  );

  const sendMultimodal = useCallback(
    (text: string, base64Image?: string) =>
      send({ type: "multimodal_query", text, image: base64Image }),
    [send]
  );

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return {
    status,
    events,
    lastError,
    connect,
    disconnect,
    sendText,
    sendAudioChunk,
    sendVideoFrame,
    sendMultimodal
  };
}

