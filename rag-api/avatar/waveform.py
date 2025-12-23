"""
Waveform Generation
Audio amplitude analysis and confidence-based visualization for avatar.
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import numpy as np


class AvatarState(Enum):
    """Avatar state machine states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


class WaveformGenerator:
    """
    Generates waveform data for avatar visualization.
    
    Features:
    - Audio amplitude analysis
    - Confidence-based visualization
    - State machine (listening, thinking, speaking)
    - Waveform data API
    """
    
    def __init__(self):
        """Initialize waveform generator."""
        self.current_state = AvatarState.IDLE
        self.amplitude_history: List[float] = []
        self.confidence_history: List[float] = []
        self.max_history_length = 100
    
    def analyze_audio_amplitude(self, audio_data: bytes, sample_rate: int = 44100) -> Dict:
        """
        Analyze audio amplitude from raw audio bytes.
        
        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate (default: 44100)
            
        Returns:
            Dict with amplitude data
        """
        try:
            # Convert bytes to numpy array
            # For now, use a simple approach (in production, use proper audio library)
            import struct
            
            # Assume 16-bit PCM audio
            samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
            samples_array = np.array(samples, dtype=np.float32)
            
            # Normalize to [-1, 1]
            if len(samples_array) > 0:
                samples_array = samples_array / 32768.0
            
            # Calculate amplitude metrics
            rms = np.sqrt(np.mean(samples_array**2)) if len(samples_array) > 0 else 0.0
            peak = np.max(np.abs(samples_array)) if len(samples_array) > 0 else 0.0
            average = np.mean(np.abs(samples_array)) if len(samples_array) > 0 else 0.0
            
            # Update history
            self.amplitude_history.append(rms)
            if len(self.amplitude_history) > self.max_history_length:
                self.amplitude_history.pop(0)
            
            return {
                "rms": float(rms),
                "peak": float(peak),
                "average": float(average),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "rms": 0.0,
                "peak": 0.0,
                "average": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def update_confidence(self, confidence: float):
        """
        Update confidence level (from Deepgram or other STT).
        
        Args:
            confidence: Confidence score (0.0 to 1.0)
        """
        self.confidence_history.append(confidence)
        if len(self.confidence_history) > self.max_history_length:
            self.confidence_history.pop(0)
    
    def get_waveform_data(self, window_size: int = 50) -> Dict:
        """
        Get waveform data for visualization.
        
        Args:
            window_size: Number of samples to return
            
        Returns:
            Dict with waveform data
        """
        # Get recent amplitude history
        recent_amplitudes = self.amplitude_history[-window_size:] if len(self.amplitude_history) > window_size else self.amplitude_history
        
        # Get recent confidence history
        recent_confidence = self.confidence_history[-window_size:] if len(self.confidence_history) > window_size else self.confidence_history
        
        # Calculate visualization parameters
        avg_amplitude = np.mean(recent_amplitudes) if recent_amplitudes else 0.0
        avg_confidence = np.mean(recent_confidence) if recent_confidence else 0.0
        
        # Determine visualization intensity based on state
        if self.current_state == AvatarState.LISTENING:
            intensity = avg_confidence * 0.8  # Pulse with confidence
        elif self.current_state == AvatarState.THINKING:
            intensity = 0.3  # Dimmed, slow pulse
        elif self.current_state == AvatarState.SPEAKING:
            intensity = avg_amplitude * 1.2  # Pulse with audio amplitude
        else:
            intensity = 0.1  # Idle state
        
        return {
            "state": self.current_state.value,
            "amplitudes": [float(a) for a in recent_amplitudes],
            "confidence": [float(c) for c in recent_confidence],
            "intensity": float(intensity),
            "average_amplitude": float(avg_amplitude),
            "average_confidence": float(avg_confidence),
            "timestamp": datetime.now().isoformat()
        }
    
    def set_state(self, state: AvatarState):
        """
        Set avatar state.
        
        Args:
            state: New avatar state
        """
        self.current_state = state
    
    def get_state(self) -> str:
        """
        Get current avatar state.
        
        Returns:
            Current state as string
        """
        return self.current_state.value
    
    def reset(self):
        """Reset waveform generator."""
        self.current_state = AvatarState.IDLE
        self.amplitude_history.clear()
        self.confidence_history.clear()


# Global waveform generator instance
waveform_generator = WaveformGenerator()

def get_waveform_generator() -> WaveformGenerator:
    """Get global waveform generator instance."""
    return waveform_generator

