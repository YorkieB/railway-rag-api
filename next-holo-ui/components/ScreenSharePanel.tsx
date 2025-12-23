import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { apiBaseFromEnv } from "@/lib/api";

type Props = {
  apiBase: string;
};

type SessionStatus = "idle" | "connecting" | "live" | "paused" | "error";

type AnalysisResult = {
  analysis?: string;
  mode?: string;
  tokens_used?: number;
  frames_processed?: number;
  vision_tokens_used?: number;
  vision_tokens_limit?: number;
  warning?: boolean;
  secrets_blurred?: number;
  error?: string;
};

export function ScreenSharePanel({ apiBase }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<SessionStatus>("idle");
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [frameRate, setFrameRate] = useState<number>(1.0); // fps
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<Array<{ timestamp: number; result: AnalysisResult }>>([]);
  const [mode, setMode] = useState<"describe" | "guide" | "pin">("describe");
  const [query, setQuery] = useState("");
  const [pinnedFrames, setPinnedFrames] = useState<Array<{ id: string; timestamp: number; result: AnalysisResult }>>([]);
  
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const statusChip = {
    idle: { label: "Idle", color: "bg-slate-300" },
    connecting: { label: "Connecting...", color: "bg-amber-300" },
    live: { label: "Live", color: "bg-emerald-400 animate-pulse" },
    paused: { label: "Paused", color: "bg-yellow-400" },
    error: { label: "Error", color: "bg-red-400" }
  }[status];

  const startScreenShare = async () => {
    try {
      setStatus("connecting");
      
      // Request screen share
      const mediaStream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: frameRate, width: 1280, height: 720 },
        audio: false
      });
      
      setStream(mediaStream);
      
      // Create session
      const response = await fetch(`${apiBase}/live-sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "default",
          mode: "LS3",
          recording_consent: false,
          frame_sampling_rate: frameRate
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to create session");
      }
      
      const data = await response.json();
      const sid = data.session_id;
      setSessionId(sid);
      
      // Connect WebSocket
      const wsUrl = apiBase.replace("https://", "wss://").replace("http://", "ws://") + `/live-sessions/ws/${sid}`;
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        setStatus("live");
        setWs(websocket);
        startFrameCapture(mediaStream, websocket);
      };
      
      websocket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "analysis") {
          const result = msg.result as AnalysisResult;
          setCurrentAnalysis(result);
          setAnalysisHistory(prev => [...prev, {
            timestamp: Date.now(),
            result
          }]);
        } else if (msg.type === "error") {
          setStatus("error");
          console.error("WebSocket error:", msg.message);
        }
      };
      
      websocket.onerror = () => {
        setStatus("error");
      };
      
      websocket.onclose = () => {
        setStatus("idle");
        setWs(null);
      };
      
      // Setup video preview
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      
      // Handle stream end
      mediaStream.getVideoTracks()[0].addEventListener("ended", () => {
        stopScreenShare();
      });
      
    } catch (err: any) {
      console.error("Error starting screen share:", err);
      setStatus("error");
    }
  };

  const startFrameCapture = (mediaStream: MediaStream, websocket: WebSocket) => {
    if (!canvasRef.current || !videoRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");
    
    if (!ctx) return;
    
    const captureFrame = () => {
      if (status !== "live" || !video.videoWidth || !video.videoHeight) {
        return;
      }
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);
      
      // Convert to base64
      const base64Image = canvas.toDataURL("image/jpeg", 0.85).split(",")[1];
      
      // Send frame to backend
      websocket.send(JSON.stringify({
        type: "frame",
        frame: base64Image,
        query: query || undefined,
        mode: mode
      }));
    };
    
    // Capture at specified frame rate
    const interval = 1000 / frameRate; // ms between frames
    frameIntervalRef.current = setInterval(captureFrame, interval);
  };

  const stopScreenShare = () => {
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
    
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    
    if (ws) {
      ws.close();
      setWs(null);
    }
    
    if (sessionId) {
      fetch(`${apiBase}/live-sessions/${sessionId}`, { method: "DELETE" });
      setSessionId(null);
    }
    
    setStatus("idle");
    setCurrentAnalysis(null);
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };

  const pauseSession = () => {
    if (ws && sessionId) {
      ws.send(JSON.stringify({ type: "pause" }));
      setStatus("paused");
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
    }
  };

  const resumeSession = () => {
    if (ws && sessionId && stream) {
      ws.send(JSON.stringify({ type: "resume" }));
      setStatus("live");
      startFrameCapture(stream, ws);
    }
  };

  const sendQuery = () => {
    if (ws && query.trim()) {
      // Trigger immediate frame capture with query
      if (canvasRef.current && videoRef.current && stream) {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        const ctx = canvas.getContext("2d");
        
        if (ctx) {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          ctx.drawImage(video, 0, 0);
          const base64Image = canvas.toDataURL("image/jpeg", 0.85).split(",")[1];
          
          ws.send(JSON.stringify({
            type: "frame",
            frame: base64Image,
            query: query,
            mode: mode
          }));
        }
      }
      setQuery("");
    }
  };

  const pinCurrentFrame = () => {
    if (currentAnalysis) {
      setPinnedFrames(prev => [...prev, {
        id: Math.random().toString(36).slice(2),
        timestamp: Date.now(),
        result: currentAnalysis
      }]);
    }
  };

  useEffect(() => {
    return () => {
      stopScreenShare();
    };
  }, []);

  return (
    <div className="glass neon-border p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-xl font-semibold">Screen Share Assist (LS3)</h2>
        <span className="chip">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${statusChip.color}`} aria-hidden="true" />
          {statusChip.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        {status === "idle" ? (
          <button
            onClick={startScreenShare}
            className="glow-button px-4 py-3 text-sm tap-target"
            type="button"
          >
            Start Screen Share
          </button>
        ) : (
          <>
            <button
              onClick={stopScreenShare}
              className="glow-button px-4 py-3 text-sm tap-target bg-red-500/70 hover:bg-red-500/90"
              type="button"
            >
              Stop
            </button>
            {status === "live" ? (
              <button
                onClick={pauseSession}
                className="glow-button px-4 py-3 text-sm tap-target"
                type="button"
              >
                Pause
              </button>
            ) : (
              <button
                onClick={resumeSession}
                className="glow-button px-4 py-3 text-sm tap-target"
                type="button"
              >
                Resume
              </button>
            )}
          </>
        )}
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-200/70">Frame Rate:</label>
          <select
            value={frameRate}
            onChange={(e) => setFrameRate(parseFloat(e.target.value))}
            className="bg-black/40 border border-white/20 rounded px-2 py-1 text-xs text-white"
            disabled={status !== "idle"}
          >
            <option value={0.5}>0.5 fps</option>
            <option value={1.0}>1 fps</option>
            <option value={2.0}>2 fps</option>
          </select>
        </div>
      </div>

      {status !== "idle" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="text-xs text-slate-200/70">Screen Preview</div>
            <div className="relative rounded-lg overflow-hidden border border-white/10 bg-black/40">
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full h-auto max-h-64 object-contain"
              />
              <canvas ref={canvasRef} className="hidden" />
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="text-xs text-slate-200/70">Analysis Mode</div>
            <div className="flex gap-2">
              <button
                onClick={() => setMode("describe")}
                className={`px-3 py-2 text-xs rounded ${mode === "describe" ? "bg-purple-500/30" : "bg-white/5"}`}
                type="button"
              >
                Describe
              </button>
              <button
                onClick={() => setMode("guide")}
                className={`px-3 py-2 text-xs rounded ${mode === "guide" ? "bg-purple-500/30" : "bg-white/5"}`}
                type="button"
              >
                Guide
              </button>
              <button
                onClick={() => setMode("pin")}
                className={`px-3 py-2 text-xs rounded ${mode === "pin" ? "bg-purple-500/30" : "bg-white/5"}`}
                type="button"
              >
                Pin
              </button>
            </div>
            
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about what you see..."
                className="flex-1 bg-black/40 border border-white/20 rounded px-3 py-2 text-sm text-white placeholder-slate-400"
                onKeyPress={(e) => e.key === "Enter" && sendQuery()}
              />
              <button
                onClick={sendQuery}
                className="glow-button px-4 py-2 text-sm"
                type="button"
                disabled={!query.trim()}
              >
                Ask
              </button>
            </div>
            
            {currentAnalysis && (
              <button
                onClick={pinCurrentFrame}
                className="w-full glow-button px-4 py-2 text-sm"
                type="button"
              >
                Pin Current Frame
              </button>
            )}
          </div>
        </div>
      )}

      {currentAnalysis && (
        <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-3 space-y-2">
          <div className="flex items-center justify-between">
            <div className="text-xs font-semibold text-purple-300">Current Analysis</div>
            {currentAnalysis.warning && (
              <span className="text-xs text-amber-400">⚠ Budget Warning</span>
            )}
          </div>
          {currentAnalysis.error ? (
            <div className="text-sm text-red-400">{currentAnalysis.error}</div>
          ) : (
            <div className="text-sm text-slate-200 whitespace-pre-wrap">{currentAnalysis.analysis}</div>
          )}
          {currentAnalysis.secrets_blurred && currentAnalysis.secrets_blurred > 0 && (
            <div className="text-xs text-amber-400">
              ⚠ {currentAnalysis.secrets_blurred} secret region(s) blurred
            </div>
          )}
          {currentAnalysis.vision_tokens_used !== undefined && (
            <div className="text-xs text-slate-400">
              Tokens: {currentAnalysis.vision_tokens_used} / {currentAnalysis.vision_tokens_limit}
            </div>
          )}
        </div>
      )}

      {pinnedFrames.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-200/70">Pinned Frames</div>
          {pinnedFrames.map((frame) => (
            <div key={frame.id} className="rounded-lg border border-white/10 bg-white/5 p-2">
              <div className="text-xs text-slate-400 mb-1">
                {new Date(frame.timestamp).toLocaleTimeString()}
              </div>
              <div className="text-sm text-slate-200 whitespace-pre-wrap">
                {frame.result.analysis}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

