import { motion } from "framer-motion";

type HeroProps = {
  onGenerate?: () => void;
  statusText?: string;
};

export function Hero({ onGenerate, statusText }: HeroProps) {
  return (
    <div className="card p-6 md:p-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-2 max-w-2xl">
          <div className="text-sm uppercase tracking-wide text-gray-500 font-medium">Jarvis AI Assistant</div>
          <h1 className="text-2xl md:text-3xl font-bold leading-tight text-gray-900">
            RAG-powered chat interface with multimodal capabilities
          </h1>
          <p className="text-base text-gray-600 max-w-3xl">
            Chat with your documents, generate content, and interact with various AI-powered features.
          </p>
          {statusText ? (
            <div className="flex flex-wrap gap-2 mt-3">
              <span className="chip">{statusText}</span>
            </div>
          ) : null}
        </div>
        {onGenerate && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onGenerate}
            className="btn-primary text-base px-6 py-3"
            aria-label="Scroll to the chat panel"
          >
            Start Chatting
          </motion.button>
        )}
      </div>
    </div>
  );
}

