import { useEffect, useMemo, useRef, useState } from "react";
import Head from "next/head";
import { Hero } from "@/components/Hero";
import { ChatPanel } from "@/components/ChatPanel";
import { ArtifactPanel } from "@/components/ArtifactPanel";
import { VoiceVideo } from "@/components/VoiceVideo";
import { CompanionVoice } from "@/components/CompanionVoice";
import { ScreenSharePanel } from "@/components/ScreenSharePanel";
import { BrowserPanel } from "@/components/BrowserPanel";
import { ExportPanel } from "@/components/ExportPanel";
import { DevicePairing } from "@/components/DevicePairing";
import { OSAutomationPanel } from "@/components/OSAutomationPanel";
import { PanicStop } from "@/components/PanicStop";
import { AgentOrchestration } from "@/components/AgentOrchestration";
import { AdvancedMemoryPanel } from "@/components/AdvancedMemoryPanel";
import { EvaluationDashboard } from "@/components/EvaluationDashboard";
import { Avatar } from "@/components/Avatar";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import { StatusBar } from "@/components/StatusBar";
import { ImageGenerator } from "@/components/ImageGenerator";
import { VideoGenerator } from "@/components/VideoGenerator";
import { ChartGenerator } from "@/components/ChartGenerator";
import { SpotifyPanel } from "@/components/SpotifyPanel";
import { AudioLiveSession } from "@/components/AudioLiveSession";
import { VideoLiveSession } from "@/components/VideoLiveSession";
import { Login } from "@/components/Login";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { apiBaseFromEnv, companionApiBaseFromEnv, queryApi, uploadDocument, speakWithElevenLabs } from "@/lib/api";
import { Artifact, Message } from "@/types";

const defaultApi = apiBaseFromEnv();
const defaultVoice = "6twLzp3s6IkvvMSxk3oD";

export default function Home() {
  const [apiBaseStored, setApiBaseStored, apiReady] = useLocalStorage("holo-api-base", defaultApi);
  const [geminiKey, setGeminiKey] = useLocalStorage("holo-gemini-key", "");
  const [elevenKey, setElevenKey] = useLocalStorage("holo-eleven-key", "");
  const [elevenVoice, setElevenVoice] = useLocalStorage("holo-eleven-voice", defaultVoice);
  const [openAiKey, setOpenAiKey] = useLocalStorage("holo-openai-key", "");
  const [ttsEnabledRaw, setTtsEnabledRaw] = useLocalStorage("holo-tts-enabled", "true");

  const [apiBase, setApiBase] = useState(defaultApi);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<string>("unknown");

  const chatRef = useRef<HTMLDivElement | null>(null);

  const ttsEnabled = ttsEnabledRaw === "true";

  useEffect(() => {
    if (apiReady) {
      setApiBase(apiBaseStored || defaultApi);
    }
  }, [apiReady, apiBaseStored]);

  const statusText = useMemo(
    () => `API: ${apiBase} • Messages: ${messages.length} • Artifacts: ${artifacts.length}`,
    [apiBase, artifacts.length, messages.length]
  );

  const handleSend = async (text: string) => {
    const userMsg: Message = { id: newId(), role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setSending(true);
    try {
      const res = await queryApi(apiBase, text, {
        user_id: "default", // TODO: Get from auth/session
        project_id: undefined, // TODO: Get from project selector
        private_session: false // TODO: Get from settings
      });
      const assistantMsg: Message = {
        id: newId(),
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        uncertain: res.uncertain,
        reason: res.reason,
        suggestions: res.suggestions,
        memories_used: res.memories_used
      };
      setMessages(prev => [...prev, assistantMsg]);
      if (ttsEnabled && elevenKey && elevenVoice) {
        void speakWithElevenLabs(res.answer, elevenKey, elevenVoice);
      }
      setArtifacts(prev => [
        ...prev,
        {
          id: newId(),
          title: "Answer artifact",
          content: res.answer,
          type: "text"
        }
      ]);
    } catch (err: any) {
      const assistantMsg: Message = {
        id: newId(),
        role: "assistant",
        content: `Error: ${err?.message || "Unknown error"}`
      };
      setMessages(prev => [...prev, assistantMsg]);
    } finally {
      setSending(false);
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(apiBase, file, file.name);
      setArtifacts(prev => [
        ...prev,
        { id: newId(), title: `Uploaded ${file.name}`, content: "Document ingested into knowledge base." }
      ]);
    } catch (err: any) {
      setArtifacts(prev => [
        ...prev,
        { id: newId(), title: "Upload failed", content: err?.message || "Unknown error" }
      ]);
    } finally {
      setUploading(false);
    }
  };

  const scrollToChat = () => {
    chatRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // simple health check
    const check = async () => {
      try {
        const res = await fetch(`${apiBase}/health`);
        if (!res.ok) throw new Error("health failed");
        const body = await res.json();
        setBackendStatus(body.status || "ok");
      } catch {
        setBackendStatus("unreachable");
      }
    };
    check();
  }, [apiBase]);

  return (
    <>
      <Head>
        <title>Jarvis Holo UI</title>
        <meta name="description" content="Touch-friendly holographic UI for Jarvis RAG + Gemini Live with chat, artifacts, and real-time voice/video." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <main className="min-h-screen relative">
        <div className="grid-overlay" />
        <div className="absolute inset-0 bg-gradient-to-b from-white/5 via-transparent to-black/60 pointer-events-none" />
        <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 py-10 space-y-8">
          <Hero onGenerate={scrollToChat} statusText={statusText} />
          <StatusBar apiBase={apiBase} backendStatus={backendStatus} />

          <div ref={chatRef} className="grid grid-cols-1 xl:grid-cols-2 gap-4 lg:gap-6">
            <ChatPanel messages={messages} onSend={handleSend} sending={sending || uploading} onFileSelected={handleUpload} />
            <ArtifactPanel
              artifacts={artifacts}
              onClear={() => setArtifacts([])}
              onRemove={id => setArtifacts(prev => prev.filter(a => a.id !== id))}
            />
          </div>

          <VoiceVideo apiBase={apiBase} elevenLabsKey={elevenKey} elevenLabsVoice={elevenVoice} ttsEnabled={ttsEnabled} />

          <CompanionVoice apiBase={companionApiBaseFromEnv()} />

          <ScreenSharePanel apiBase={apiBase} />

          <BrowserPanel apiBase={apiBase} />

          <ExportPanel apiBase={apiBase} messages={messages} />

          <DevicePairing apiBase={apiBase} />

          <OSAutomationPanel apiBase={apiBase} />

          <PanicStop />

          <AgentOrchestration />

          <AdvancedMemoryPanel />

          <EvaluationDashboard />

          <Avatar />

          <ImageGenerator />

          <VideoGenerator />

          <ChartGenerator />

          <SpotifyPanel />

          <AudioLiveSession />

          <VideoLiveSession />

          <Login />

          <div className="flex items-center flex-wrap gap-3">
            <button className="text-sm underline underline-offset-4 text-slate-200/80 hover:text-white" onClick={() => setSettingsOpen(true)}>
              Settings
            </button>
            <div className="text-xs text-slate-200/60">Touch-optimized; drag/scroll works on large panels.</div>
          </div>
        </div>
      </main>

      <SettingsDrawer
        open={settingsOpen}
        onClose={() => {
          setSettingsOpen(false);
          setApiBaseStored(apiBase);
        }}
        apiBase={apiBase}
        onApiBaseChange={setApiBase}
        geminiKey={geminiKey}
        onGeminiKeyChange={setGeminiKey}
        elevenLabsKey={elevenKey}
        onElevenLabsKeyChange={setElevenKey}
        elevenLabsVoice={elevenVoice}
        onElevenLabsVoiceChange={setElevenVoice}
        openAiKey={openAiKey}
        onOpenAiKeyChange={setOpenAiKey}
        ttsEnabled={ttsEnabled}
        onTtsEnabledChange={val => setTtsEnabledRaw(val ? "true" : "false")}
      />
    </>
  );
}

function newId() {
  return Math.random().toString(36).slice(2);
}

