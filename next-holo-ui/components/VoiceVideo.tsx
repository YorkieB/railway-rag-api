import { useEffect, useMemo, useRef, useState } from "react";
import { createGeminiSession, speakWithElevenLabs } from "@/lib/api";
import { useGeminiLive } from "@/hooks/useGeminiLive";

type Props = {
  apiBase: string;
  elevenLabsKey: string;
  elevenLabsVoice: string;
  ttsEnabled: boolean;
};

export function VoiceVideo({ apiBase, elevenLabsKey, elevenLabsVoice, ttsEnabled }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const videoLoopRef = useRef<number | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  const [micEnabled, setMicEnabled] = useState(true);
  const [camEnabled, setCamEnabled] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [liveText, setLiveText] = useState("");

  const {
    status,
    events,
    lastError,
    connect,
    disconnect,
    sendText,
    sendAudioChunk,
    sendVideoFrame
  } = useGeminiLive(apiBase);

  const sessionReady = status === "connected";
  const lastTtsIndex = useRef(0);

  const startSession = async () => {
    setConnecting(true);
    try {
      const session = await createGeminiSession(apiBase, {});
      setSessionId(session.session_id);
      connect(session.session_id);
      await startMedia();
    } catch (err) {
      console.error(err);
    } finally {
      setConnecting(false);
    }
  };

  const stopSession = () => {
    stopMedia();
    disconnect();
    setSessionId(null);
  };

  const startMedia = async () => {
    if (typeof navigator === "undefined") return;
    const constraints: MediaStreamConstraints = {
      audio: micEnabled,
      video: camEnabled ? { width: 640, height: 360 } : false
    };
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    setMediaStream(stream);
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(() => null);
    }
    startAudioRecorder(stream);
    startVideoLoop(stream);
  };

  const stopMedia = () => {
    if (recorderRef.current && recorderRef.current.state !== "inactive") {
      recorderRef.current.stop();
    }
    if (videoLoopRef.current) {
      cancelAnimationFrame(videoLoopRef.current);
      videoLoopRef.current = null;
    }
    mediaStream?.getTracks().forEach(t => t.stop());
    setMediaStream(null);
  };

  const startAudioRecorder = (stream: MediaStream) => {
    if (!micEnabled) return;
    try {
      const rec = new MediaRecorder(stream, { mimeType: "audio/webm" });
      recorderRef.current = rec;
      rec.ondataavailable = async evt => {
        if (evt.data.size > 0) {
          const base64 = await blobToBase64(evt.data);
          sendAudioChunk(base64, Date.now());
        }
      };
      rec.start(1200); // emit chunks every ~1.2s
    } catch (err) {
      console.error("Recorder error", err);
    }
  };

  const startVideoLoop = (stream: MediaStream) => {
    if (!camEnabled) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    const ctx = canvas.getContext("2d");
    const draw = () => {
      if (!ctx) return;
      const { videoWidth, videoHeight } = video;
      if (videoWidth && videoHeight) {
        canvas.width = videoWidth;
        canvas.height = videoHeight;
        ctx.drawImage(video, 0, 0, videoWidth, videoHeight);
        canvas.toBlob(
          async blob => {
            if (blob) {
              const base64 = await blobToBase64(blob, "image/jpeg");
              sendVideoFrame(base64, Date.now());
            }
          },
          "image/jpeg",
          0.6
        );
      }
      videoLoopRef.current = requestAnimationFrame(draw);
    };
    draw();
  };

  useEffect(() => {
    return () => stopSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // React to camera toggle even after session start.
  useEffect(() => {
    const applyCameraState = async () => {
      if (!mediaStream) return;
      if (!camEnabled) {
        if (videoLoopRef.current) {
          cancelAnimationFrame(videoLoopRef.current);
          videoLoopRef.current = null;
        }
        mediaStream.getVideoTracks().forEach(t => t.stop());
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
        return;
      }
      try {
        const hasVideo = mediaStream.getVideoTracks().length > 0;
        if (!hasVideo && typeof navigator !== "undefined") {
          const vStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 360 }, audio: false });
          const track = vStream.getVideoTracks()[0];
          if (track) {
            mediaStream.addTrack(track);
          }
        }
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          videoRef.current.play().catch(() => null);
        }
        startVideoLoop(mediaStream);
      } catch (err) {
        console.error("Camera toggle error", err);
        setCamEnabled(false);
      }
    };
    applyCameraState();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [camEnabled, mediaStream]);

  // TTS playback for incoming events
  useEffect(() => {
    if (!ttsEnabled || !elevenLabsKey || !elevenLabsVoice) {
      lastTtsIndex.current = events.length;
      return;
    }
    const slice = events.slice(lastTtsIndex.current);
    slice.forEach(evt => {
      if (evt.type === "text_response" && typeof evt.answer === "string") {
        void speakWithElevenLabs(evt.answer, elevenLabsKey, elevenLabsVoice);
      } else if (evt.type === "audio_response" && typeof evt.message === "string") {
        void speakWithElevenLabs(evt.message, elevenLabsKey, elevenLabsVoice);
      }
    });
    lastTtsIndex.current = events.length;
  }, [events, elevenLabsKey, elevenLabsVoice, ttsEnabled]);

  const statusChip = useMemo(() => {
    if (status === "connected") return { label: "Connected", color: "bg-emerald-400 animate-pulse" };
    if (status === "connecting") return { label: "Connecting...", color: "bg-amber-300" };
    if (status === "error") return { label: "Error", color: "bg-red-500" };
    return { label: "Idle", color: "bg-gray-400" };
  }, [status]);

  return (
    <div className="card p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-xl font-semibold text-gray-900">Gemini Live (Voice + Vision)</h2>
        <span className="chip">
          <span className={`inline-block h-2 w-2 rounded-full ${statusChip.color} mr-2`} aria-hidden="true" />
          {statusChip.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={sessionReady ? stopSession : startSession}
          className="btn-primary text-sm tap-target disabled:opacity-60 disabled:cursor-not-allowed"
          disabled={connecting}
          aria-label={sessionReady ? "Stop session" : "Start session"}
          type="button"
        >
          {sessionReady ? "Stop Session" : connecting ? "Starting..." : "Start Session"}
        </button>
        {sessionReady && (
          <button
            onClick={stopSession}
            className="btn-secondary text-sm tap-target bg-red-50 text-red-700 border-red-200 hover:bg-red-100"
            aria-label="End call"
            type="button"
          >
            End Call
          </button>
        )}
        <label className="flex items-center gap-2 text-sm tap-target select-none text-gray-700">
          <input
            type="checkbox"
            className="h-4 w-4 accent-primary rounded"
            checked={micEnabled}
            onChange={e => setMicEnabled(e.target.checked)}
            aria-label="Toggle microphone"
          />
          Mic
        </label>
        <label className="flex items-center gap-2 text-sm tap-target select-none text-gray-700">
          <input
            type="checkbox"
            className="h-4 w-4 accent-primary rounded"
            checked={camEnabled}
            onChange={e => setCamEnabled(e.target.checked)}
            aria-label="Toggle camera"
          />
          Camera
        </label>
        {sessionId && (
          <span className="text-xs text-gray-600 truncate max-w-[220px]">Session: {sessionId}</span>
        )}
      </div>

      <div className="flex gap-2">
        <input
          value={liveText}
          onChange={e => setLiveText(e.target.value)}
          className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-gray-400"
          placeholder="Send text into the live session"
          aria-label="Send text to live session"
        />
        <button
          onClick={() => {
            if (liveText.trim()) {
              sendText(liveText.trim());
              setLiveText("");
            }
          }}
          disabled={!sessionReady}
          className="btn-primary text-sm disabled:opacity-60 tap-target"
          aria-label="Send text event to live session"
        >
          Send
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="rounded-lg border border-gray-200 bg-gray-100 p-2 flex flex-col gap-2">
          <video ref={videoRef} className="w-full rounded-lg bg-black aspect-video" muted playsInline />
          <canvas ref={canvasRef} className="hidden" />
          <div className="text-xs text-gray-600">Live preview (muted locally)</div>
        </div>
        <div
          className="rounded-lg border border-gray-200 bg-gray-50 p-3 max-h-64 overflow-y-auto space-y-2"
          role="log"
          aria-live="polite"
          aria-relevant="additions text"
        >
          {events.length === 0 && (
            <div className="text-sm text-gray-500">Responses and vision descriptions will appear here.</div>
          )}
          {events.map((evt, idx) => (
            <div key={idx} className="text-sm text-gray-900">
              <span className="text-xs text-primary uppercase mr-2 font-medium">{evt.type}</span>
              {renderEvent(evt)}
            </div>
          ))}
          {lastError && <div className="text-xs text-red-600">Error: {lastError}</div>}
        </div>
      </div>
    </div>
  );
}

function renderEvent(evt: any) {
  if (evt.type === "vision_description") return <span>{evt.description}</span>;
  if (evt.type === "text_response") return <span>{evt.answer}</span>;
  if (evt.type === "audio_response") return <span>{evt.message || "Audio acknowledged"}</span>;
  if (evt.type === "error") return <span className="text-red-300">{evt.message}</span>;
  return <span>{JSON.stringify(evt)}</span>;
}

async function blobToBase64(blob: Blob, fallbackType?: string): Promise<string> {
  const typed = blob.type || fallbackType || "application/octet-stream";
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(reader.error);
    reader.onloadend = () => {
      const res = typeof reader.result === "string" ? reader.result : "";
      const base64 = res.split(",")[1] || "";
      resolve(base64);
    };
    reader.readAsDataURL(new Blob([blob], { type: typed }));
  });
}

