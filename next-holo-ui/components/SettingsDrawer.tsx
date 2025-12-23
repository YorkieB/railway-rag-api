import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

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
  onTtsEnabledChange
}: Props) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <AnimatePresence>
      {open && mounted && (
        <div className="fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-xs" onClick={onClose} aria-hidden="true" />
          <motion.div
            initial={{ x: 360, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 360, opacity: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 28 }}
            className="absolute right-0 top-0 h-full w-full max-w-md glass neon-border p-6 overflow-y-auto"
            role="dialog"
            aria-modal="true"
            aria-label="Settings panel"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-lg font-semibold">Settings</div>
              <button type="button" onClick={onClose} className="text-slate-200/70 hover:text-white tap-target">
                Close
              </button>
            </div>
            <div className="space-y-4">
              <Field label="API Base URL" value={apiBase} onChange={onApiBaseChange} placeholder="https://your-api.run.app" />
              <Field label="Gemini API Key (client use optional)" value={geminiKey} onChange={onGeminiKeyChange} placeholder="sk-..." />
              <Field label="ElevenLabs API Key" value={elevenLabsKey} onChange={onElevenLabsKeyChange} placeholder="elevenlabs..." />
              <Field label="ElevenLabs Voice ID" value={elevenLabsVoice} onChange={onElevenLabsVoiceChange} placeholder="voice id" />
              <Field label="OpenAI API Key" value={openAiKey} onChange={onOpenAiKeyChange} placeholder="sk-..." />
              <ToggleRow
                label="Play assistant responses (ElevenLabs TTS)"
                checked={ttsEnabled}
                onChange={onTtsEnabledChange}
              />
              <p className="text-xs text-slate-200/70">
                Keys are stored locally in your browser (localStorage). Gemini Live WS uses the backend environment key; client key is optional for client-side calls.
              </p>
            </div>
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
      <div className="text-sm text-slate-200/80">{label}</div>
      <input
        className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm focus:outline-none focus:border-neon-violet placeholder:text-slate-400/80"
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
    <label className="flex items-center justify-between text-sm text-slate-200/80 border border-white/10 rounded-lg px-3 py-2 bg-white/5 tap-target cursor-pointer">
      <span>{label}</span>
      <input type="checkbox" className="h-5 w-5 accent-neon-violet" checked={checked} onChange={e => onChange(e.target.checked)} />
    </label>
  );
}

