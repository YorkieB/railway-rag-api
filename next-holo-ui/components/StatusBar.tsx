type Props = {
  apiBase: string;
  backendStatus?: string;
};

export function StatusBar({ apiBase, backendStatus }: Props) {
  const statusTone =
    backendStatus === "ok" ? "bg-emerald-400" : backendStatus === "unreachable" ? "bg-red-400" : "bg-amber-300";

  return (
    <div className="glass neon-border px-4 py-3 flex flex-wrap items-center gap-3 text-sm" role="status" aria-live="polite">
      <span className="chip">
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${statusTone}`} aria-hidden="true" />
        Backend: {backendStatus || "n/a"}
      </span>
      <span className="text-slate-200/80 truncate">API: {apiBase}</span>
    </div>
  );
}

