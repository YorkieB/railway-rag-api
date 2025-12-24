import { useState, useEffect } from "react";
import { useLocalStorage } from "@/hooks/useLocalStorage";

type Props = {
  apiBase: string;
};

type JarvisPersonality = {
  tone: "formal" | "casual" | "friendly" | "professional" | "warm" | "energetic";
  personality: string[];
  speakingStyle: "concise" | "detailed" | "conversational" | "storytelling";
  avatarEnabled: boolean;
  avatarType: "2d" | "3d" | "minimal";
  avatarPosition: "center" | "left" | "right";
};

const TONE_OPTIONS = [
  { value: "formal", label: "Formal", description: "Professional and respectful" },
  { value: "casual", label: "Casual", description: "Relaxed and informal" },
  { value: "friendly", label: "Friendly", description: "Warm and approachable" },
  { value: "professional", label: "Professional", description: "Business-focused" },
  { value: "warm", label: "Warm", description: "Empathetic and caring" },
  { value: "energetic", label: "Energetic", description: "Enthusiastic and dynamic" },
];

const PERSONALITY_TRAITS = [
  "Empathetic",
  "Analytical",
  "Creative",
  "Supportive",
  "Humor",
  "Direct",
  "Patient",
  "Curious",
  "Encouraging",
  "Practical",
];

const SPEAKING_STYLES = [
  { value: "concise", label: "Concise", description: "Brief and to the point" },
  { value: "detailed", label: "Detailed", description: "Thorough explanations" },
  { value: "conversational", label: "Conversational", description: "Natural dialogue" },
  { value: "storytelling", label: "Storytelling", description: "Narrative approach" },
];

export function JarvisCustomization({ apiBase }: Props) {
  const [personality, setPersonality] = useLocalStorage<JarvisPersonality>("jarvis-personality", {
    tone: "friendly",
    personality: ["Empathetic", "Supportive"],
    speakingStyle: "conversational",
    avatarEnabled: true,
    avatarType: "3d",
    avatarPosition: "center",
  });

  const togglePersonalityTrait = (trait: string) => {
    setPersonality((prev) => ({
      ...prev,
      personality: prev.personality.includes(trait)
        ? prev.personality.filter((t) => t !== trait)
        : [...prev.personality, trait],
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Jarvis Customization</h3>
        <p className="text-sm text-gray-600 mb-6">
          Customize Jarvis&apos;s personality, tone, and appearance to match your preferences.
        </p>
      </div>

      {/* Tone Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-900">Communication Tone</label>
        <div className="grid grid-cols-2 gap-3">
          {TONE_OPTIONS.map((option) => (
            <label
              key={option.value}
              className={`flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                personality.tone === option.value
                  ? "border-primary bg-primary/5"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <input
                type="radio"
                name="tone"
                value={option.value}
                checked={personality.tone === option.value}
                onChange={(e) =>
                  setPersonality((prev) => ({ ...prev, tone: e.target.value as any }))
                }
                className="mt-1 h-4 w-4 accent-primary"
              />
              <div className="ml-3 flex-1">
                <div className="text-sm font-medium text-gray-900">{option.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{option.description}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Personality Traits */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-900">Personality Traits</label>
        <p className="text-xs text-gray-500">Select traits that describe how Jarvis should behave</p>
        <div className="flex flex-wrap gap-2">
          {PERSONALITY_TRAITS.map((trait) => (
            <button
              key={trait}
              type="button"
              onClick={() => togglePersonalityTrait(trait)}
              className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
                personality.personality.includes(trait)
                  ? "bg-primary text-white border-primary"
                  : "bg-white text-gray-700 border-gray-300 hover:border-gray-400"
              }`}
            >
              {trait}
            </button>
          ))}
        </div>
      </div>

      {/* Speaking Style */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-900">Speaking Style</label>
        <div className="grid grid-cols-2 gap-3">
          {SPEAKING_STYLES.map((style) => (
            <label
              key={style.value}
              className={`flex items-start p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                personality.speakingStyle === style.value
                  ? "border-primary bg-primary/5"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <input
                type="radio"
                name="speakingStyle"
                value={style.value}
                checked={personality.speakingStyle === style.value}
                onChange={(e) =>
                  setPersonality((prev) => ({ ...prev, speakingStyle: e.target.value as any }))
                }
                className="mt-1 h-4 w-4 accent-primary"
              />
              <div className="ml-3 flex-1">
                <div className="text-sm font-medium text-gray-900">{style.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{style.description}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Avatar Settings */}
      <div className="space-y-4 border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between">
          <div>
            <label className="text-sm font-medium text-gray-900">Avatar Display</label>
            <p className="text-xs text-gray-500 mt-0.5">
              Show animated avatar with lip sync during conversations
            </p>
          </div>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={personality.avatarEnabled}
              onChange={(e) =>
                setPersonality((prev) => ({ ...prev, avatarEnabled: e.target.checked }))
              }
              className="h-5 w-5 accent-primary"
            />
          </label>
        </div>

        {personality.avatarEnabled && (
          <>
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-900">Avatar Type</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: "3d", label: "3D Avatar", description: "Full 3D character" },
                  { value: "2d", label: "2D Avatar", description: "Animated sprite" },
                  { value: "minimal", label: "Minimal", description: "Simple visualization" },
                ].map((type) => (
                  <label
                    key={type.value}
                    className={`flex flex-col items-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                      personality.avatarType === type.value
                        ? "border-primary bg-primary/5"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="avatarType"
                      value={type.value}
                      checked={personality.avatarType === type.value}
                      onChange={(e) =>
                        setPersonality((prev) => ({ ...prev, avatarType: e.target.value as any }))
                      }
                      className="h-4 w-4 accent-primary"
                    />
                    <div className="mt-2 text-center">
                      <div className="text-sm font-medium text-gray-900">{type.label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{type.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-900">Avatar Position</label>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { value: "center", label: "Center" },
                  { value: "left", label: "Left" },
                  { value: "right", label: "Right" },
                ].map((pos) => (
                  <label
                    key={pos.value}
                    className={`flex items-center justify-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                      personality.avatarPosition === pos.value
                        ? "border-primary bg-primary/5"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="avatarPosition"
                      value={pos.value}
                      checked={personality.avatarPosition === pos.value}
                      onChange={(e) =>
                        setPersonality((prev) => ({ ...prev, avatarPosition: e.target.value as any }))
                      }
                      className="h-4 w-4 accent-primary"
                    />
                    <span className="ml-2 text-sm text-gray-900">{pos.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800">
          <strong>Note:</strong> Personality settings will be applied to future conversations. The
          avatar will appear in the center area between chat messages and artifacts, with lip sync
          animation synchronized to Jarvis&apos;s voice.
        </p>
      </div>
    </div>
  );
}


