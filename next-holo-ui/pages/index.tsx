/**
 * Jarvis Main Page
 * 
 * Complete integration of all features:
 * - Budget Status
 * - Memory Panel
 * - Browser Automation
 * - Uncertainty Banner
 * - Query Interface
 */

import React, { useState } from "react";
import { BudgetStatus } from "@/components/BudgetStatus";
import { MemoryPanel } from "@/components/MemoryPanel";
import { BrowserPanel } from "@/components/BrowserPanel";
import { UncertaintyBanner } from "@/components/UncertaintyBanner";
import { ChatInterface } from "@/components/ChatInterface";
import { VoiceChat } from "@/components/VoiceChat";

export default function HomePage() {
  // User ID - replace with actual authentication
  const [userId] = useState("user123");
  const [projectId, setProjectId] = useState<string | undefined>(undefined);
  const [uncertainResponse, setUncertainResponse] = useState<any>(null);
  const [queryMessage, setQueryMessage] = useState("");
  const [queryResponse, setQueryResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Get API base URL from environment
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  const handleQuery = async () => {
    if (!queryMessage.trim()) return;

    try {
      setLoading(true);
      setUncertainResponse(null);
      setQueryResponse(null);

      const response = await fetch(`${apiBase}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: queryMessage,
          user_id: userId,
          project_id: projectId,
          history: [],
          private_session: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Check for uncertainty
      if (data.uncertain) {
        setUncertainResponse(data);
      }

      setQueryResponse(data);
      setQueryMessage("");
    } catch (error) {
      console.error("Query failed:", error);
      setQueryResponse({
        answer: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
        uncertain: false,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 transition-colors duration-200">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <Card variant="elevated">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Jarvis AI Assistant</CardTitle>
                  <CardDescription>
                    Complete integration of all features: Budget, Memory, Live Sessions, and Browser Automation
                  </CardDescription>
                </div>
                <ThemeToggle />
              </div>
            </CardHeader>
          </Card>

          {/* Budget Status Section */}
          <Card>
            <CardHeader>
              <CardTitle>Budget Status</CardTitle>
            </CardHeader>
            <CardContent>
              <BudgetStatus userId={userId} />
            </CardContent>
          </Card>

        {/* Uncertainty Banner */}
        {uncertainResponse && (
          <section>
            <UncertaintyBanner response={uncertainResponse} />
          </section>
        )}

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Memory Panel */}
            <Card hover>
              <CardHeader>
                <CardTitle>Memory Management</CardTitle>
              </CardHeader>
              <CardContent>
                <MemoryPanel userId={userId} projectId={projectId} />
              </CardContent>
            </Card>

            {/* Browser Panel */}
            <Card hover>
              <CardHeader>
                <CardTitle>Browser Automation</CardTitle>
              </CardHeader>
              <CardContent>
                <BrowserPanel userId={userId} />
              </CardContent>
            </Card>
          </div>

          {/* Voice Chat - Real-time Voice Conversation */}
          <Card>
            <CardHeader>
              <CardTitle>Voice Chat with Jarvis</CardTitle>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Real-time voice conversation using ElevenLabs TTS and Deepgram STT
              </p>
            </CardHeader>
            <CardContent>
              <VoiceChat 
                userId={userId}
                apiBase={apiBase}
              />
            </CardContent>
          </Card>

          {/* Text Chat Interface - Full Conversation */}
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Text Chat with Jarvis</CardTitle>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Have a text conversation with your AI assistant
                </p>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
              <ChatInterface 
                userId={userId} 
                projectId={projectId}
                apiBase={apiBase}
              />
            </CardContent>
          </Card>

          {/* Project Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Project Selection</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={projectId || ""}
                  onChange={(e) => setProjectId(e.target.value || undefined)}
                  placeholder="Enter project ID (optional)"
                  className="flex-1 px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button
                  variant="secondary"
                  onClick={() => setProjectId(undefined)}
                >
                  Clear
                </Button>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Project ID: {projectId || "None (global memory)"}
              </p>
            </CardContent>
          </Card>

          {/* Stage C: Media Features */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ImageGenerator />
            <SpotifyPlayer />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MusicCreator />
            <SocialMediaPoster />
          </div>

          {/* Word Processor */}
          <WordProcessor />
        </div>
      </div>
    </ThemeProvider>
  );
}

