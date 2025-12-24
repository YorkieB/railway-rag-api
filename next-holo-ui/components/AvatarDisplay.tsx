import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocalStorage } from "@/hooks/useLocalStorage";

type Props = {
  isSpeaking?: boolean;
  audioUrl?: string;
  text?: string;
};

type JarvisPersonality = {
  avatarEnabled: boolean;
  avatarType: "2d" | "3d" | "minimal";
  avatarPosition: "center" | "left" | "right";
};

export function AvatarDisplay({ isSpeaking = false, audioUrl, text }: Props) {
  const [personality] = useLocalStorage<JarvisPersonality>("jarvis-personality", {
    avatarEnabled: true,
    avatarType: "3d",
    avatarPosition: "center",
  });

  const [mouthOpen, setMouthOpen] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (isSpeaking && audioUrl && audioRef.current) {
      // Start lip sync animation
      const animateMouth = () => {
        setMouthOpen((prev) => !prev);
        animationRef.current = requestAnimationFrame(animateMouth);
      };
      animateMouth();

      // Play audio
      audioRef.current.src = audioUrl;
      audioRef.current.play().catch(console.error);
      
      // Stop animation when audio ends
      const handleEnded = () => {
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }
        setMouthOpen(false);
      };
      audioRef.current.addEventListener("ended", handleEnded);

      return () => {
        if (animationRef.current) {
          cancelAnimationFrame(animationRef.current);
        }
        if (audioRef.current) {
          audioRef.current.removeEventListener("ended", handleEnded);
        }
        setMouthOpen(false);
      };
    } else {
      setMouthOpen(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
  }, [isSpeaking, audioUrl]);

  if (!personality.avatarEnabled) {
    return null;
  }

  const renderAvatar = () => {
    switch (personality.avatarType) {
      case "3d":
        return (
          <div className="relative w-full h-full flex items-center justify-center">
            {/* 3D Avatar Placeholder - Replace with actual 3D model */}
            <div className="relative w-64 h-96 bg-gradient-to-b from-blue-100 to-blue-200 rounded-2xl shadow-2xl overflow-hidden">
              {/* Avatar Body */}
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-48 h-80 bg-gradient-to-b from-blue-300 to-blue-500 rounded-t-full">
                {/* Head */}
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 w-32 h-32 bg-blue-200 rounded-full border-4 border-blue-400">
                  {/* Eyes */}
                  <div className="absolute top-8 left-1/2 transform -translate-x-1/2 flex gap-4">
                    <div className="w-4 h-4 bg-blue-800 rounded-full animate-blink" />
                    <div className="w-4 h-4 bg-blue-800 rounded-full animate-blink" />
                  </div>
                  {/* Mouth - animated for lip sync */}
                  <motion.div
                    className="absolute bottom-6 left-1/2 transform -translate-x-1/2 w-8 h-4 bg-blue-800 rounded-full"
                    animate={{
                      scaleY: mouthOpen ? 1.5 : 0.8,
                      scaleX: mouthOpen ? 1.2 : 1,
                    }}
                    transition={{
                      duration: 0.1,
                      repeat: Infinity,
                      repeatType: "reverse",
                    }}
                  />
                </div>
              </div>
              {/* Speaking indicator */}
              {isSpeaking && (
                <motion.div
                  className="absolute top-4 right-4 w-3 h-3 bg-green-500 rounded-full"
                  animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </div>
          </div>
        );
      case "2d":
        return (
          <div className="relative w-full h-full flex items-center justify-center">
            <div className="relative w-48 h-64">
              {/* 2D Sprite Avatar */}
              <div className="relative w-full h-full bg-gradient-to-b from-purple-100 to-purple-200 rounded-xl shadow-lg overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center">
                  {/* Face */}
                  <div className="relative w-32 h-32">
                    {/* Eyes */}
                    <div className="absolute top-6 left-1/2 transform -translate-x-1/2 flex gap-3">
                      <div className="w-3 h-3 bg-purple-800 rounded-full" />
                      <div className="w-3 h-3 bg-purple-800 rounded-full" />
                    </div>
                    {/* Mouth - animated */}
                    <motion.div
                      className="absolute bottom-4 left-1/2 transform -translate-x-1/2 w-6 h-3 bg-purple-800 rounded-full"
                      animate={{
                        scaleY: mouthOpen ? 1.8 : 0.6,
                      }}
                      transition={{
                        duration: 0.1,
                        repeat: Infinity,
                        repeatType: "reverse",
                      }}
                    />
                  </div>
                </div>
                {isSpeaking && (
                  <motion.div
                    className="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full"
                    animate={{ scale: [1, 1.5, 1], opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </div>
            </div>
          </div>
        );
      case "minimal":
        return (
          <div className="relative w-full h-full flex items-center justify-center">
            <div className="relative w-32 h-32">
              {/* Minimal Avatar - Simple circle with animated mouth */}
              <div className="relative w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 rounded-full shadow-lg flex items-center justify-center">
                {/* Eyes */}
                <div className="absolute top-8 left-1/2 transform -translate-x-1/2 flex gap-2">
                  <div className="w-2 h-2 bg-gray-700 rounded-full" />
                  <div className="w-2 h-2 bg-gray-700 rounded-full" />
                </div>
                {/* Mouth */}
                <motion.div
                  className="absolute bottom-6 left-1/2 transform -translate-x-1/2 w-4 h-2 bg-gray-700 rounded-full"
                  animate={{
                    scaleY: mouthOpen ? 1.5 : 0.5,
                  }}
                  transition={{
                    duration: 0.1,
                    repeat: Infinity,
                    repeatType: "reverse",
                  }}
                />
              </div>
              {isSpeaking && (
                <motion.div
                  className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"
                  animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
              )}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center p-4 bg-gradient-to-b from-gray-50 to-white rounded-lg border border-gray-200">
      <AnimatePresence mode="wait">
        {isSpeaking ? (
          <motion.div
            key="speaking"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="w-full h-full"
          >
            {renderAvatar()}
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="w-full h-full flex items-center justify-center"
          >
            {renderAvatar()}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Audio element for playback */}
      <audio ref={audioRef} className="hidden" />
      
      {/* Optional: Show text being spoken */}
      {text && isSpeaking && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-lg border border-gray-200 shadow-sm max-w-xs"
        >
          <p className="text-sm text-gray-700 text-center line-clamp-2">{text}</p>
        </motion.div>
      )}
    </div>
  );
}


