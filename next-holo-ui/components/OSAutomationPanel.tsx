"use client";

import { useState, useEffect } from "react";
import {
  launchApp,
  switchToApp,
  listRunningApps,
  readFile,
  writeFile,
  deleteFile,
  listDirectory,
  captureScreenshot,
  findElementInScreenshot,
  clickCoordinate,
  setROC,
  clearROC,
  getROC,
  listWindows,
  type AppInfo,
  type FileInfo,
  type ROCInfo,
} from "@/lib/api";

interface OSAutomationPanelProps {
  apiBase: string;
}

export function OSAutomationPanel({ apiBase }: OSAutomationPanelProps) {
  const [activeTab, setActiveTab] = useState<"apps" | "files" | "vision" | "roc">("apps");
  const [runningApps, setRunningApps] = useState<AppInfo[]>([]);
  const [windows, setWindows] = useState<Array<{ title: string; hwnd: number; bounds: any }>>([]);
  const [activeROC, setActiveROC] = useState<ROCInfo | null>(null);
  const [filePath, setFilePath] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [directoryPath, setDirectoryPath] = useState("");
  const [directoryItems, setDirectoryItems] = useState<FileInfo[]>([]);
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [elementDescription, setElementDescription] = useState("");
  const [foundElement, setFoundElement] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Load running apps and windows on mount
  useEffect(() => {
    loadRunningApps();
    loadWindows();
    loadROC();
  }, []);

  const loadRunningApps = async () => {
    try {
      const result = await listRunningApps(apiBase);
      setRunningApps(result.apps);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const loadWindows = async () => {
    try {
      const result = await listWindows(apiBase);
      setWindows(result.windows);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const loadROC = async () => {
    try {
      const result = await getROC(apiBase);
      if (result.success && result.roc) {
        setActiveROC(result.roc);
      }
    } catch (err: any) {
      // ROC might not be set, ignore error
    }
  };

  const handleLaunchApp = async (appPath: string) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await launchApp(apiBase, appPath);
      if (result.success) {
        setSuccess(`App launched: ${appPath}`);
        await loadRunningApps();
      } else {
        setError(result.error || "Failed to launch app");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSwitchToApp = async (windowTitle: string) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await switchToApp(apiBase, windowTitle);
      if (result.success) {
        setSuccess(`Switched to: ${result.window_title}`);
      } else {
        setError(result.error || "Failed to switch to app");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReadFile = async () => {
    if (!filePath) {
      setError("Please enter a file path");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await readFile(apiBase, filePath);
      if (result.success) {
        setFileContent(result.content || "");
        setSuccess(`File read: ${result.size} bytes`);
      } else {
        setError(result.error || "Failed to read file");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleListDirectory = async () => {
    if (!directoryPath) {
      setError("Please enter a directory path");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await listDirectory(apiBase, directoryPath);
      if (result.success) {
        setDirectoryItems(result.items);
        setSuccess(`Found ${result.count} items`);
      } else {
        setError(result.error || "Failed to list directory");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCaptureScreenshot = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await captureScreenshot(apiBase);
      if (result.success) {
        setScreenshot(result.screenshot);
        setSuccess("Screenshot captured");
      } else {
        setError("Failed to capture screenshot");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFindElement = async () => {
    if (!screenshot || !elementDescription) {
      setError("Please capture a screenshot and enter element description");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await findElementInScreenshot(apiBase, screenshot, elementDescription);
      if (result.success && result.bounds) {
        setFoundElement(result);
        setSuccess(`Element found (confidence: ${(result.confidence || 0) * 100}%)`);
      } else {
        setError(result.error || "Element not found");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClickElement = async () => {
    if (!foundElement || !foundElement.center) {
      setError("No element selected to click");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await clickCoordinate(apiBase, foundElement.center.x, foundElement.center.y);
      if (result.success) {
        setSuccess(`Clicked at (${result.x}, ${result.y})`);
        setFoundElement(null);
      } else {
        setError(result.error || "Click failed");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSetROC = async (windowTitle: string) => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await setROC(apiBase, windowTitle);
      if (result.success) {
        setActiveROC(result.roc);
        setSuccess(`ROC set to: ${result.roc.window_title}`);
      } else {
        setError(result.error || "Failed to set ROC");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClearROC = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await clearROC(apiBase);
      if (result.success) {
        setActiveROC(null);
        setSuccess("ROC cleared");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700/50">
      <h2 className="text-xl font-semibold text-white mb-4">OS Automation</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-500/20 border border-green-500/50 rounded text-green-200 text-sm">
          {success}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-slate-700/50">
        <button
          onClick={() => setActiveTab("apps")}
          className={`px-4 py-2 text-sm transition-colors ${
            activeTab === "apps"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Apps
        </button>
        <button
          onClick={() => setActiveTab("files")}
          className={`px-4 py-2 text-sm transition-colors ${
            activeTab === "files"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Files
        </button>
        <button
          onClick={() => setActiveTab("vision")}
          className={`px-4 py-2 text-sm transition-colors ${
            activeTab === "vision"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Vision
        </button>
        <button
          onClick={() => setActiveTab("roc")}
          className={`px-4 py-2 text-sm transition-colors ${
            activeTab === "roc"
              ? "text-blue-400 border-b-2 border-blue-400"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          ROC
        </button>
      </div>

      {/* Apps Tab */}
      {activeTab === "apps" && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-2">Running Apps</h3>
            <div className="max-h-40 overflow-y-auto space-y-1">
              {runningApps.length > 0 ? (
                runningApps.map((app, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-slate-700/30 rounded text-sm text-slate-200 flex justify-between items-center"
                  >
                    <span>{app.window_title}</span>
                    <button
                      onClick={() => handleSwitchToApp(app.window_title)}
                      className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs"
                    >
                      Switch
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-slate-400 text-sm">No running apps</div>
              )}
            </div>
            <button
              onClick={loadRunningApps}
              className="mt-2 px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs"
            >
              Refresh
            </button>
          </div>
        </div>
      )}

      {/* Files Tab */}
      {activeTab === "files" && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-2">Read File</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder="C:\\Users\\...\\file.txt"
                className="flex-1 px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-slate-200 text-sm"
              />
              <button
                onClick={handleReadFile}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm"
              >
                Read
              </button>
            </div>
            {fileContent && (
              <div className="mt-2 p-3 bg-slate-900/50 rounded border border-slate-700 text-slate-200 text-xs max-h-40 overflow-y-auto">
                <pre className="whitespace-pre-wrap">{fileContent}</pre>
              </div>
            )}
          </div>

          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-2">List Directory</h3>
            <div className="flex gap-2">
              <input
                type="text"
                value={directoryPath}
                onChange={(e) => setDirectoryPath(e.target.value)}
                placeholder="C:\\Users\\..."
                className="flex-1 px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-slate-200 text-sm"
              />
              <button
                onClick={handleListDirectory}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm"
              >
                List
              </button>
            </div>
            {directoryItems.length > 0 && (
              <div className="mt-2 max-h-40 overflow-y-auto space-y-1">
                {directoryItems.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-slate-700/30 rounded text-sm text-slate-200"
                  >
                    {item.is_dir ? "📁" : "📄"} {item.name} ({item.size} bytes)
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Vision Tab */}
      {activeTab === "vision" && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-2">Screenshot</h3>
            <button
              onClick={handleCaptureScreenshot}
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm"
            >
              Capture Screenshot
            </button>
            {screenshot && (
              <div className="mt-2">
                <img
                  src={`data:image/png;base64,${screenshot}`}
                  alt="Screenshot"
                  className="max-w-full h-auto rounded border border-slate-600"
                />
              </div>
            )}
          </div>

          {screenshot && (
            <div>
              <h3 className="text-sm font-medium text-slate-300 mb-2">Find Element</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={elementDescription}
                  onChange={(e) => setElementDescription(e.target.value)}
                  placeholder="Describe the element to find..."
                  className="flex-1 px-3 py-2 bg-slate-700/50 border border-slate-600 rounded text-slate-200 text-sm"
                />
                <button
                  onClick={handleFindElement}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm"
                >
                  Find
                </button>
              </div>
              {foundElement && (
                <div className="mt-2 p-3 bg-slate-700/30 rounded text-sm text-slate-200">
                  <div>Found: {foundElement.description}</div>
                  <div>Confidence: {(foundElement.confidence || 0) * 100}%</div>
                  <div>
                    Bounds: ({foundElement.bounds.x}, {foundElement.bounds.y}) -{" "}
                    {foundElement.bounds.width}x{foundElement.bounds.height}
                  </div>
                  <button
                    onClick={handleClickElement}
                    disabled={loading}
                    className="mt-2 px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs"
                  >
                    Click Element
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ROC Tab */}
      {activeTab === "roc" && (
        <div className="space-y-4">
          {activeROC ? (
            <div className="p-3 bg-slate-700/30 rounded border border-slate-600">
              <div className="text-sm text-slate-200 mb-2">
                <strong>Active ROC:</strong> {activeROC.window_title}
              </div>
              <div className="text-xs text-slate-400">
                Bounds: ({activeROC.bounds.x}, {activeROC.bounds.y}) -{" "}
                {activeROC.bounds.width}x{activeROC.bounds.height}
              </div>
              <button
                onClick={handleClearROC}
                disabled={loading}
                className="mt-2 px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs"
              >
                Clear ROC
              </button>
            </div>
          ) : (
            <div className="text-sm text-slate-400 mb-2">No active ROC</div>
          )}

          <div>
            <h3 className="text-sm font-medium text-slate-300 mb-2">Available Windows</h3>
            <div className="max-h-40 overflow-y-auto space-y-1">
              {windows.length > 0 ? (
                windows.map((window, idx) => (
                  <div
                    key={idx}
                    className="p-2 bg-slate-700/30 rounded text-sm text-slate-200 flex justify-between items-center"
                  >
                    <span>{window.title}</span>
                    <button
                      onClick={() => handleSetROC(window.title)}
                      disabled={loading}
                      className="px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-xs"
                    >
                      Set ROC
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-slate-400 text-sm">No windows found</div>
              )}
            </div>
            <button
              onClick={loadWindows}
              className="mt-2 px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs"
            >
              Refresh
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

