import { Artifact } from "@/types";
import { motion } from "framer-motion";

type Props = {
  artifacts: Artifact[];
  onClear?: () => void;
  onRemove?: (id: string) => void;
};

export function ArtifactPanel({ artifacts, onClear, onRemove }: Props) {
  return (
    <div className="card p-4 md:p-6 h-full flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Artifacts</h2>
        <button
          className="text-xs text-gray-600 hover:text-gray-900 underline underline-offset-4 tap-target disabled:opacity-50 disabled:no-underline disabled:cursor-not-allowed px-3 py-2 rounded-lg transition-colors"
          onClick={onClear}
          disabled={!artifacts.length}
          aria-label="Clear all artifacts"
        >
          Clear all
        </button>
      </div>

      <div
        className="flex-1 min-h-[380px] md:min-h-[420px] max-h-[540px] xl:max-h-[640px] overflow-y-auto space-y-3 pr-1"
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
      >
        {artifacts.length === 0 && (
          <div className="text-gray-500 text-sm">Generated patterns and code will appear here.</div>
        )}

        {artifacts.map(item => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-gray-200 bg-gray-50 p-3 space-y-2"
          >
            <div className="flex items-center justify-between">
              <div className="font-semibold text-gray-900">{item.title}</div>
              <button
                className="text-xs text-gray-600 hover:text-gray-900 tap-target transition-colors"
                onClick={() => onRemove?.(item.id)}
                aria-label={`Close artifact ${item.title}`}
              >
                Close
              </button>
            </div>
            <pre className="code-block text-sm leading-relaxed whitespace-pre-wrap">{item.content}</pre>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

