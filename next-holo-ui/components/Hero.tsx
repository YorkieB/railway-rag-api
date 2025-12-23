import { motion } from "framer-motion";

type HeroProps = {
  onGenerate?: () => void;
  statusText?: string;
};

export function Hero({ onGenerate, statusText }: HeroProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl glass p-8 md:p-12 xl:p-14 neon-border shadow-glow">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/12 to-cyan-400/12" />
      <div className="absolute -right-24 -top-24 w-72 h-72 bg-cyan-400/10 blur-3xl rounded-full" />
      <div className="absolute -left-20 bottom-0 w-80 h-80 bg-purple-500/10 blur-3xl rounded-full" />

      <div className="relative z-10 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
        <div className="space-y-3 max-w-2xl">
          <div className="text-sm uppercase tracking-[0.3em] text-neon-cyan">Jarvis Holo Interface</div>
          <h1 className="text-3xl md:text-4xl font-bold leading-tight text-white">
            Touch-first, holographic-inspired control surface for your RAG + Gemini Live stack.
          </h1>
          <p className="text-base md:text-lg text-slate-200/80 max-w-3xl">
            Stream audio/video to Gemini Live, chat with your documents, and drive artifacts from a neon, glass UI.
            Optimized for large touch panels and WebRTC.
          </p>
          {statusText ? (
            <div className="flex flex-wrap gap-2">
              <span className="chip">{statusText}</span>
            </div>
          ) : null}
        </div>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
          onClick={onGenerate}
          className="glow-button text-lg px-8 py-4"
          aria-label="Scroll to the chat panel"
        >
          Generate
        </motion.button>
      </div>
    </div>
  );
}

