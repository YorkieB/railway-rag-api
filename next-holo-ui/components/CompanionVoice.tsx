import { useEffect, useMemo, useRef, useState } from "react";
import { CompanionClient, CompanionMessage } from "@/lib/companion-api";
import { companionApiBaseFromEnv } from "@/lib/api";
import { motion } from "framer-motion";

type Props = {
  apiBase: string;
};

export function CompanionVoice({ apiBase: companionApiBase }: Props) {
  const [client, setClient] = useState<CompanionClient | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "connecting" | "connected" | "error">("idle");
  const [transcripts, setTranscripts] = useState<Array<{ role: "user" | "assistant"; text: string; timestamp?: number }>>([]);
  const [currentResponse, setCurrentResponse] = useState("");
  const [latency, setLatency] = useState<{ ttft?: number; total?: number }>({});
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [retrievedMemories, setRetrievedMemories] = useState<string[]>([]);
  const [showMemories, setShowMemories] = useState(false);
  const [memoryCount, setMemoryCount] = useState(0);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioQueueRef = useRef<Array<string>>([]);
  const isPlayingRef = useRef(false);

  const statusChip = useMemo(() => {
    if (status === "connected") return { label: "Connected", color: "bg-green-500 animate-pulse" };
    if (status === "connecting") return { label: "Connecting...", color: "bg-yellow-500" };
    if (status === "error") return { label: "Error", color: "bg-red-500" };
    return { label: "Idle", color: "bg-gray-400" };
  }, [status]);

  const startSession = async () => {
    setStatus("connecting");
    try {
      const apiBase = companionApiBase || companionApiBaseFromEnv();
      const companionClient = new CompanionClient(apiBase);
      const sid = await companionClient.createSession();
      setSessionId(sid);
      
      companionClient.onMessage((msg: CompanionMessage) => {
        handleCompanionMessage(msg);
      });
      
      companionClient.onError((error: Error) => {
        console.error("Companion error:", error);
        setStatus("error");
      });
      
      await companionClient.connect(sid);
      setClient(companionClient);
      setStatus("connected");
    } catch (err) {
      console.error("Error starting session:", err);
      setStatus("error");
    }
  };

  const stopSession = () => {
    if (client) {
      client.disconnect();
      setClient(null);
      setSessionId(null);
      setStatus("idle");
      setTranscripts([]);
      setCurrentResponse("");
      setLatency({});
    }
  };

  const handleCompanionMessage = (msg: CompanionMessage) => {
    switch (msg.type) {
      case "session_ready":
        setStatus("connected");
        break;
      
      case "transcript":
        if (msg.text && msg.role) {
          setTranscripts(prev => [...prev, { 
            role: msg.role!, 
            text: msg.text!,
            timestamp: Date.now()
          }]);
        }
        break;
      
      case "text_chunk":
        if (msg.text) {
          setCurrentResponse(prev => prev + msg.text);
        }
        break;
      
      case "response_start":
        setCurrentResponse("");
        setLatency(prev => ({ ...prev, ttft: msg.ttft_ms }));
        setIsInterrupted(false);
        // Clear previous memories, new ones will come if available
        setRetrievedMemories([]);
        break;
      
      case "memory_context":
        // If backend sends memory context (could be added)
        if (msg.text) {
          setRetrievedMemories(prev => [...prev, msg.text!]);
        }
        break;
      
      case "audio_chunk":
        if (msg.audio) {
          playAudioChunk(msg.audio);
        }
        break;
      
      case "response_complete":
        setLatency(prev => ({ ...prev, total: msg.total_ms }));
        setTranscripts(prev => [...prev, { 
          role: "assistant", 
          text: currentResponse,
          timestamp: Date.now()
        }]);
        setCurrentResponse("");
        break;
      
      case "interrupted":
        setIsInterrupted(true);
        setCurrentResponse("");
        break;
      
      case "error":
        console.error("Companion error:", msg.message);
        setStatus("error");
        break;
    }
  };

  const playAudioChunk = (base64Audio: string) => {
    audioQueueRef.current.push(base64Audio);
    if (!isPlayingRef.current) {
      processAudioQueue();
    }
  };

  const processAudioQueue = async () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      return;
    }
    
    isPlayingRef.current = true;
    const base64Audio = audioQueueRef.current.shift()!;
    
    try {
      const audioBlob = new Blob(
        [Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0))],
        { type: "audio/mpeg" }
      );
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play().then(() => {
          audioRef.current!.onended = () => {
            URL.revokeObjectURL(audioUrl);
            processAudioQueue();
          };
        }).catch(() => {
          URL.revokeObjectURL(audioUrl);
          processAudioQueue();
        });
      } else {
        processAudioQueue();
      }
    } catch (error) {
      console.error("Error playing audio:", error);
      processAudioQueue();
    }
  };

  const sendText = (text: string) => {
    if (client && text.trim()) {
      client.sendText(text.trim());
    }
  };

  const interrupt = () => {
    if (client) {
      client.interrupt();
    }
  };

  // Fetch memory count on session start
  useEffect(() => {
    if (sessionId && status === "connected") {
      fetchMemoryCount();
    }
  }, [sessionId, status]);

  const fetchMemoryCount = async () => {
    try {
      const apiBase = companionApiBase || companionApiBaseFromEnv();
      const response = await fetch(`${apiBase}/companion/memories?session_id=${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setMemoryCount(data.count || 0);
      }
    } catch (err) {
      console.error("Error fetching memories:", err);
    }
  };

  useEffect(() => {
    return () => {
      if (client) {
        client.disconnect();
      }
    };
  }, [client]);

  return (
    <div className="card p-4 md:p-6 space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h2 className="text-xl font-semibold text-gray-900">AI Companion (Real-Time)</h2>
        <span className="chip">
          <span className={`inline-block h-2 w-2 rounded-full ${statusChip.color} mr-2`} aria-hidden="true" />
          {statusChip.label}
        </span>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={status === "connected" ? stopSession : startSession}
          className="btn-primary text-sm tap-target disabled:opacity-60 disabled:cursor-not-allowed"
          disabled={status === "connecting"}
          type="button"
        >
          {status === "connected" ? "Stop Session" : status === "connecting" ? "Connecting..." : "Start Session"}
        </button>
        {status === "connected" && (
          <button
            onClick={interrupt}
            className="btn-secondary text-sm tap-target bg-red-50 text-red-700 border-red-200 hover:bg-red-100"
            type="button"
          >
            Interrupt
          </button>
        )}
        {sessionId && (
          <span className="text-xs text-gray-600 truncate max-w-[220px]">Session: {sessionId}</span>
        )}
      </div>

      <div className="flex items-center justify-between flex-wrap gap-2">
        {latency.ttft && (
          <div className="text-xs text-gray-600">
            <span className={latency.ttft < 800 ? "text-green-600" : latency.ttft < 1200 ? "text-yellow-600" : "text-red-600"}>
              TTFT: {latency.ttft.toFixed(0)}ms
            </span>
            {latency.total && ` • Total: ${latency.total.toFixed(0)}ms`}
          </div>
        )}
        {status === "connected" && (
          <button
            onClick={() => setShowMemories(!showMemories)}
            className="text-xs text-gray-600 hover:text-gray-900 underline transition-colors"
            type="button"
          >
            {showMemories ? "Hide" : "Show"} Memories ({memoryCount})
          </button>
        )}
      </div>

      {isInterrupted && (
        <div className="text-xs text-yellow-700 animate-pulse flex items-center gap-2 bg-yellow-50 border border-yellow-200 rounded px-2 py-1">
          <span>⚠️</span>
          <span>AI response interrupted</span>
        </div>
      )}

      {showMemories && retrievedMemories.length > 0 && (
        <div className="rounded-lg border border-primary/30 bg-primary-light p-3 space-y-2">
          <div className="text-xs font-semibold text-primary">Retrieved Context:</div>
          {retrievedMemories.map((mem, idx) => (
            <div key={idx} className="text-xs text-gray-700 italic border-l-2 border-primary/50 pl-2">
              {mem}
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          className="rounded-lg border border-gray-200 bg-gray-50 p-3 max-h-64 overflow-y-auto space-y-2"
          role="log"
          aria-live="polite"
        >
          {transcripts.length === 0 && (
            <div className="text-sm text-gray-500 italic">Conversation will appear here...</div>
          )}
          {transcripts.map((t, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className={`text-sm rounded-lg p-2 ${
                t.role === "user" 
                  ? "bg-blue-50 text-blue-900 border border-blue-200" 
                  : "bg-primary-light text-primary border border-primary/20"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <span className="text-xs uppercase font-semibold mr-2 opacity-70">{t.role}:</span>
                  <span className="whitespace-pre-wrap">{t.text}</span>
                </div>
                {t.timestamp && (
                  <span className="text-xs opacity-50 text-gray-600">
                    {new Date(t.timestamp).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </motion.div>
          ))}
          {currentResponse && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-primary bg-primary-light border border-primary/20 rounded-lg p-2"
            >
              <span className="text-xs uppercase font-semibold mr-2 opacity-70">assistant:</span>
              <span className="whitespace-pre-wrap">{currentResponse}</span>
              <span className="animate-pulse ml-1">▋</span>
            </motion.div>
          )}
        </div>
        <div className="rounded-lg border border-gray-200 bg-gray-100 p-2 flex flex-col gap-2">
          <div className="text-xs text-gray-600 mb-2">Audio Playback</div>
          <div className="flex-1 flex items-center justify-center">
            {status === "connected" ? (
              <div className="text-xs text-green-600 animate-pulse">● Streaming</div>
            ) : (
              <div className="text-xs text-gray-500">Idle</div>
            )}
          </div>
          <audio ref={audioRef} className="w-full" controls />
        </div>
        </div>
    </div>
  );
}

