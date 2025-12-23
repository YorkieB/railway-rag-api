"use client";

import { useState } from "react";
import clsx from "clsx";

export type PanelId =
  | "home"
  | "voice-video"
  | "screen-share"
  | "browser"
  | "os-automation"
  | "device-pairing"
  | "panic-stop"
  | "agent-orchestration"
  | "memory"
  | "evaluation"
  | "avatar"
  | "image-gen"
  | "video-gen"
  | "chart-gen"
  | "spotify"
  | "audio-live"
  | "video-live"
  | "export"
  | "login"
  | "settings";

type SidebarItem = {
  id: PanelId;
  label: string;
  icon: string;
};

const sidebarItems: SidebarItem[] = [
  { id: "home", label: "Home", icon: "🏠" },
  { id: "voice-video", label: "Voice/Video", icon: "🎤" },
  { id: "screen-share", label: "Screen Share", icon: "🖥️" },
  { id: "browser", label: "Browser", icon: "🌐" },
  { id: "os-automation", label: "OS Automation", icon: "⚙️" },
  { id: "device-pairing", label: "Device Pairing", icon: "📱" },
  { id: "panic-stop", label: "Panic Stop", icon: "🛑" },
  { id: "agent-orchestration", label: "Agents", icon: "🤖" },
  { id: "memory", label: "Memory", icon: "🧠" },
  { id: "evaluation", label: "Evaluation", icon: "📊" },
  { id: "avatar", label: "Avatar", icon: "👤" },
  { id: "image-gen", label: "Image Gen", icon: "🖼️" },
  { id: "video-gen", label: "Video Gen", icon: "🎬" },
  { id: "chart-gen", label: "Chart Gen", icon: "📈" },
  { id: "spotify", label: "Spotify", icon: "🎵" },
  { id: "audio-live", label: "Audio Live", icon: "🔊" },
  { id: "video-live", label: "Video Live", icon: "📹" },
  { id: "export", label: "Export", icon: "💾" },
  { id: "login", label: "Login", icon: "🔐" },
  { id: "settings", label: "Settings", icon: "⚙️" }
];

type SidebarProps = {
  activePanel: PanelId;
  onPanelChange: (panel: PanelId) => void;
};

export function Sidebar({ activePanel, onPanelChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={clsx(
        "bg-white border-r border-border transition-all duration-200",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            {!collapsed && <h2 className="text-lg font-semibold text-gray-900">Jarvis</h2>}
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="p-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              {collapsed ? "→" : "←"}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-2">
          <ul className="space-y-1">
            {sidebarItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => onPanelChange(item.id)}
                  className={clsx(
                    "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    activePanel === item.id
                      ? "bg-primary-light text-primary border border-primary/20"
                      : "text-gray-700 hover:bg-gray-100"
                  )}
                >
                  <span className="text-lg flex-shrink-0">{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </aside>
  );
}

