import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { DiagnosticsPanel } from "@/components/DiagnosticsPanel";
import { UserManagement } from "@/components/UserManagement";
import { IntegrationsPanel } from "@/components/IntegrationsPanel";
import { useAuth } from "@/lib/auth";

type Props = {
  open: boolean;
  onClose: () => void;
  apiBase: string;
  onApiBaseChange: (val: string) => void;
  geminiKey: string;
  onGeminiKeyChange: (val: string) => void;
  elevenLabsKey: string;
  onElevenLabsKeyChange: (val: string) => void;
  elevenLabsVoice: string;
  onElevenLabsVoiceChange: (val: string) => void;
  openAiKey: string;
  onOpenAiKeyChange: (val: string) => void;
  ttsEnabled: boolean;
  onTtsEnabledChange: (val: boolean) => void;
  jarvisEnabled: boolean;
  onJarvisEnabledChange: (val: boolean) => void;
};

export function SettingsDrawer({
  open,
  onClose,
  apiBase,
  onApiBaseChange,
  geminiKey,
  onGeminiKeyChange,
  elevenLabsKey,
  onElevenLabsKeyChange,
  elevenLabsVoice,
  onElevenLabsVoiceChange,
  openAiKey,
  onOpenAiKeyChange,
  ttsEnabled,
  onTtsEnabledChange,
  jarvisEnabled,
  onJarvisEnabledChange
}: Props) {
  const { isAdmin, token } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState<"settings" | "diagnostics" | "users" | "integrations">("settings");

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <AnimatePresence>
      {open && mounted && (
        <div className="fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/30" onClick={onClose} aria-hidden="true" />
          <motion.div
            initial={{ x: 360, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 360, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 28 }}
            className="absolute right-0 top-0 h-full w-full max-w-md bg-white border-l border-gray-200 p-6 overflow-y-auto shadow-lg"
            role="dialog"
            aria-modal="true"
            aria-label="Settings panel"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-lg font-semibold text-gray-900">Settings</div>
              <button type="button" onClick={onClose} className="text-gray-600 hover:text-gray-900 tap-target transition-colors">
                Close
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-200 mb-4">
              <button
                onClick={() => setActiveTab("settings")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "settings"
                    ? "border-primary text-primary"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                Settings
              </button>
              <button
                onClick={() => setActiveTab("diagnostics")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "diagnostics"
                    ? "border-primary text-primary"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                Diagnostics
              </button>
              {isAdmin && (
                <button
                  onClick={() => setActiveTab("users")}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === "users"
                      ? "border-primary text-primary"
                      : "border-transparent text-gray-600 hover:text-gray-900"
                  }`}
                >
                  User Management
                </button>
              )}
              <button
                onClick={() => setActiveTab("integrations")}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "integrations"
                    ? "border-primary text-primary"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                Integrations
              </button>
            </div>

            {activeTab === "diagnostics" ? (
              <DiagnosticsPanel apiBase={apiBase} />
            ) : activeTab === "users" ? (
              <UserManagement apiBase={apiBase} token={token || ""} />
            ) : activeTab === "integrations" ? (
              <IntegrationsPanel apiBase={apiBase} token={token || ""} />
            ) : (
            <div className="space-y-4">
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Jarvis Activation</h3>
                <ToggleRow
                  label="Activate Jarvis Companion"
                  checked={jarvisEnabled}
                  onChange={onJarvisEnabledChange}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Enable live conversation with Jarvis. Say &quot;Hi Jarvis&quot; to start a conversation. Jarvis can access the web for real-time information.
                </p>
              </div>
              
              <div className="border-b border-gray-200 pb-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">API Keys</h3>
                <Field label="API Base URL" value={apiBase} onChange={onApiBaseChange} placeholder="https://your-api.run.app" />
                <Field label="OpenAI API Key" value={openAiKey} onChange={onOpenAiKeyChange} placeholder="sk-..." />
                <Field label="ElevenLabs API Key" value={elevenLabsKey} onChange={onElevenLabsKeyChange} placeholder="elevenlabs..." />
                <Field label="ElevenLabs Voice ID" value={elevenLabsVoice} onChange={onElevenLabsVoiceChange} placeholder="voice id" />
                <Field label="Gemini API Key (client use optional)" value={geminiKey} onChange={onGeminiKeyChange} placeholder="sk-..." />
              </div>
              
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Audio Settings</h3>
                <ToggleRow
                  label="Play assistant responses (ElevenLabs TTS)"
                  checked={ttsEnabled}
                  onChange={onTtsEnabledChange}
                />
              </div>
              
              <p className="text-xs text-gray-600">
                Keys are stored locally in your browser (localStorage). Gemini Live WS uses the backend environment key; client key is optional for client-side calls.
              </p>
            </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

type FieldProps = {
  label: string;
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
};

function Field({ label, value, onChange, placeholder }: FieldProps) {
  return (
    <div className="space-y-1">
      <div className="text-sm text-gray-700 font-medium">{label}</div>
      <input
        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 placeholder:text-gray-400 text-gray-900"
        value={value}
        placeholder={placeholder}
        onChange={e => onChange(e.target.value)}
      />
    </div>
  );
}

type ToggleProps = {
  label: string;
  checked: boolean;
  onChange: (val: boolean) => void;
};

function ToggleRow({ label, checked, onChange }: ToggleProps) {
  return (
    <label className="flex items-center justify-between text-sm text-gray-700 border border-gray-200 rounded-lg px-3 py-2 bg-gray-50 tap-target cursor-pointer hover:bg-gray-100 transition-colors">
      <span>{label}</span>
      <input type="checkbox" className="h-5 w-5 accent-primary" checked={checked} onChange={e => onChange(e.target.checked)} />
    </label>
  );
}

