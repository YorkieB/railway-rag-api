"use client";

import { useState, useEffect, useRef } from "react";
import {
  getWaveformData,
  setAvatarState,
  getAvatarState,
  getMouthAnimation,
  type WaveformData,
} from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

interface AvatarProps {
  audioElement?: HTMLAudioElement | null;
  currentTime?: number;
  isListening?: boolean;
  isThinking?: boolean;
  isSpeaking?: boolean;
}

export function Avatar({ audioElement, currentTime = 0, isListening = false, isThinking = false, isSpeaking = false }: AvatarProps) {
  const [waveformData, setWaveformData] = useState<WaveformData | null>(null);
  const [mouthAnimation, setMouthAnimation] = useState<{ mouth_shape: string; intensity: number } | null>(null);
  const [avatarState, setAvatarStateLocal] = useState<string>("idle");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Update avatar state based on props
  useEffect(() => {
    let newState = "idle";
    if (isListening) newState = "listening";
    else if (isThinking) newState = "thinking";
    else if (isSpeaking) newState = "speaking";

    if (newState !== avatarState) {
      setAvatarStateLocal(newState);
      setAvatarState(API_BASE, newState as "idle" | "listening" | "thinking" | "speaking").catch(console.error);
    }
  }, [isListening, isThinking, isSpeaking, avatarState]);

  // Fetch waveform data periodically
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getWaveformData(API_BASE, 50);
        setWaveformData(data);
      } catch (err) {
        console.error("Failed to fetch waveform data:", err);
      }
    }, 100); // Update every 100ms

    return () => clearInterval(interval);
  }, []);

  // Update mouth animation based on current time
  useEffect(() => {
    if (isSpeaking && currentTime > 0) {
      getMouthAnimation(API_BASE, currentTime)
        .then((data) => {
          setMouthAnimation({ mouth_shape: data.mouth_shape, intensity: data.intensity });
        })
        .catch(console.error);
    }
  }, [currentTime, isSpeaking]);

  // Render waveform visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const drawWaveform = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (!waveformData || waveformData.amplitudes.length === 0) {
        // Draw idle state
        ctx.fillStyle = "rgba(100, 100, 100, 0.3)";
        ctx.beginPath();
        ctx.arc(canvas.width / 2, canvas.height / 2, 20, 0, Math.PI * 2);
        ctx.fill();
        return;
      }

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const maxRadius = Math.min(canvas.width, canvas.height) / 2 - 10;

      // Draw waveform based on state
      if (avatarState === "listening" || avatarState === "speaking") {
        const amplitudes = waveformData.amplitudes;
        const intensity = waveformData.intensity;

        // Draw circular waveform
        ctx.strokeStyle = avatarState === "listening" ? "rgba(0, 150, 255, 0.8)" : "rgba(0, 255, 150, 0.8)";
        ctx.lineWidth = 2;

        for (let i = 0; i < amplitudes.length; i++) {
          const angle = (i / amplitudes.length) * Math.PI * 2;
          const radius = 20 + amplitudes[i] * maxRadius * intensity;
          const x = centerX + Math.cos(angle) * radius;
          const y = centerY + Math.sin(angle) * radius;

          if (i === 0) {
            ctx.beginPath();
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.closePath();
        ctx.stroke();
      } else if (avatarState === "thinking") {
        // Draw thinking animation (slow pulse)
        const pulse = (Date.now() % 2000) / 2000;
        const radius = 20 + Math.sin(pulse * Math.PI) * 10;
        ctx.fillStyle = "rgba(255, 200, 0, 0.5)";
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fill();
      } else {
        // Idle state
        ctx.fillStyle = "rgba(100, 100, 100, 0.3)";
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20, 0, Math.PI * 2);
        ctx.fill();
      }

      // Draw mouth shape if speaking
      if (avatarState === "speaking" && mouthAnimation) {
        drawMouth(ctx, centerX, centerY, mouthAnimation.mouth_shape, mouthAnimation.intensity);
      }
    };

    drawWaveform();
    animationFrameRef.current = requestAnimationFrame(drawWaveform);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [waveformData, avatarState, mouthAnimation]);

  const drawMouth = (ctx: CanvasRenderingContext2D, x: number, y: number, shape: string, intensity: number) => {
    ctx.fillStyle = "rgba(200, 100, 100, 0.8)";
    ctx.strokeStyle = "rgba(150, 50, 50, 1.0)";
    ctx.lineWidth = 2;

    const mouthY = y + 30;
    const mouthWidth = 20 + intensity * 15;
    const mouthHeight = 5 + intensity * 10;

    if (shape === "closed") {
      // Draw closed mouth (line)
      ctx.beginPath();
      ctx.moveTo(x - 10, mouthY);
      ctx.lineTo(x + 10, mouthY);
      ctx.stroke();
    } else if (shape === "open") {
      // Draw open mouth (ellipse)
      ctx.beginPath();
      ctx.ellipse(x, mouthY, mouthWidth / 2, mouthHeight / 2, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else {
      // Draw neutral mouth (small ellipse)
      ctx.beginPath();
      ctx.ellipse(x, mouthY, 8, 3, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={200}
          height={200}
          className="border-2 border-gray-700 rounded-full bg-gray-800"
        />
        <div className="absolute top-0 left-0 right-0 text-center mt-2">
          <span
            className={`text-xs px-2 py-1 rounded ${
              avatarState === "listening"
                ? "bg-blue-600"
                : avatarState === "thinking"
                ? "bg-yellow-600"
                : avatarState === "speaking"
                ? "bg-green-600"
                : "bg-gray-600"
            }`}
          >
            {avatarState.toUpperCase()}
          </span>
        </div>
      </div>

      {waveformData && (
        <div className="mt-4 text-xs text-gray-400">
          <div>Amplitude: {waveformData.average_amplitude.toFixed(3)}</div>
          <div>Confidence: {waveformData.average_confidence.toFixed(3)}</div>
          <div>Intensity: {waveformData.intensity.toFixed(3)}</div>
        </div>
      )}

      {mouthAnimation && avatarState === "speaking" && (
        <div className="mt-2 text-xs text-gray-400">
          <div>Mouth: {mouthAnimation.mouth_shape}</div>
          <div>Intensity: {mouthAnimation.intensity.toFixed(2)}</div>
        </div>
      )}
    </div>
  );
}

