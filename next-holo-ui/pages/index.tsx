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
import { Sidebar, type PanelId } from "@/components/Sidebar";
import { useLocalStorage } from "@/hooks/useLocalStorage";
import { apiBaseFromEnv, companionApiBaseFromEnv, queryApi, uploadDocument, speakWithElevenLabs } from "@/lib/api";
import { diagnostics } from "@/lib/diagnostics";
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
  const [jarvisEnabledRaw, setJarvisEnabledRaw] = useLocalStorage("holo-jarvis-enabled", "false");

  const [apiBase, setApiBase] = useState(defaultApi);
  const [messages, setMessages] = useState<Message[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [sending, setSending] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState<string>("unknown");
  const [activePanel, setActivePanel] = useState<PanelId>("home");

  const chatRef = useRef<HTMLDivElement | null>(null);

  const ttsEnabled = ttsEnabledRaw === "true";
  const jarvisEnabled = jarvisEnabledRaw === "true";

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
      diagnostics.logApiError("/query", err, { query: text });
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
      diagnostics.logApiError("/upload", err, { filename: file.name });
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

  const renderActivePanel = () => {
    switch (activePanel) {
      case "home":
        return (
          <div ref={chatRef} className="grid grid-cols-1 xl:grid-cols-2 gap-4 lg:gap-6">
            <ChatPanel messages={messages} onSend={handleSend} sending={sending || uploading} onFileSelected={handleUpload} />
            <ArtifactPanel
              artifacts={artifacts}
              onClear={() => setArtifacts([])}
              onRemove={id => setArtifacts(prev => prev.filter(a => a.id !== id))}
            />
          </div>
        );
      case "companion-voice":
        return <CompanionVoice apiBase={apiBase} jarvisEnabled={jarvisEnabled} />;
      case "voice-video":
        return <VoiceVideo apiBase={apiBase} elevenLabsKey={elevenKey} elevenLabsVoice={elevenVoice} ttsEnabled={ttsEnabled} />;
      case "screen-share":
        return <ScreenSharePanel apiBase={apiBase} />;
      case "browser":
        return <BrowserPanel apiBase={apiBase} />;
      case "os-automation":
        return <OSAutomationPanel apiBase={apiBase} />;
      case "device-pairing":
        return <DevicePairing apiBase={apiBase} />;
      case "panic-stop":
        return <PanicStop />;
      case "agent-orchestration":
        return <AgentOrchestration />;
      case "memory":
        return <AdvancedMemoryPanel />;
      case "evaluation":
        return <EvaluationDashboard />;
      case "avatar":
        return <Avatar />;
      case "image-gen":
        return <ImageGenerator />;
      case "video-gen":
        return <VideoGenerator />;
      case "chart-gen":
        return <ChartGenerator />;
      case "spotify":
        return <SpotifyPanel />;
      case "audio-live":
        return <AudioLiveSession />;
      case "video-live":
        return <VideoLiveSession />;
      case "export":
        return <ExportPanel apiBase={apiBase} messages={messages} />;
      case "login":
        return <Login />;
      case "settings":
        return (
          <div className="card p-6">
            <h2 className="text-2xl font-semibold mb-4">Settings</h2>
            <button
              onClick={() => setSettingsOpen(true)}
              className="btn-primary"
            >
              Open Settings
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <Head>
        <title>Jarvis</title>
        <meta name="description" content="Jarvis AI Assistant - RAG-powered chat interface" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="flex h-screen overflow-hidden bg-gray-50">
        <Sidebar activePanel={activePanel} onPanelChange={setActivePanel} />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 md:px-8 py-6 space-y-6">
            <Hero onGenerate={scrollToChat} statusText={statusText} />
            <StatusBar apiBase={apiBase} backendStatus={backendStatus} />
            {renderActivePanel()}
          </div>
        </main>
      </div>

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
        jarvisEnabled={jarvisEnabled}
        onJarvisEnabledChange={val => setJarvisEnabledRaw(val ? "true" : "false")}
      />
    </>
  );
}

function newId() {
  return Math.random().toString(36).slice(2);
}

