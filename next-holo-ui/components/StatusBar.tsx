import React from "react";

type Props = {
  apiBase: string;
  backendStatus?: string;
};

export function StatusBar({ apiBase, backendStatus }: Props) {
  const statusColor =
    backendStatus === "ok" ? "bg-green-500" : backendStatus === "unreachable" ? "bg-red-500" : "bg-yellow-500";

  return (
    <div className="card px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-sm" role="status" aria-live="polite">
      <div className="flex flex-wrap items-center gap-3">
        <span className="chip">
          <span className={`inline-block h-2 w-2 rounded-full ${statusColor} mr-2`} aria-hidden="true" />
          Backend: {backendStatus || "n/a"}
        </span>
        <span className="text-gray-600 truncate text-xs">API: {apiBase}</span>
      </div>
    </div>
  );
}

