"""
Unit tests for Avatar Presence system (waveform, lip sync).
"""
import pytest
import sys
from pathlib import Path

# Add rag-api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "rag-api"))

from avatar.waveform import get_waveform_generator, AvatarState
from avatar.lipsync import get_lipsync_processor


class TestWaveformGenerator:
    """Test waveform generation."""
    
    def test_generator_initialization(self):
        """Test waveform generator can be initialized."""
        generator = get_waveform_generator()
        assert generator is not None
    
    def test_state_management(self):
        """Test avatar state management."""
        generator = get_waveform_generator()
        
        # Test setting states
        generator.set_state(AvatarState.LISTENING)
        assert generator.get_state() == "listening"
        
        generator.set_state(AvatarState.THINKING)
        assert generator.get_state() == "thinking"
        
        generator.set_state(AvatarState.SPEAKING)
        assert generator.get_state() == "speaking"
        
        generator.set_state(AvatarState.IDLE)
        assert generator.get_state() == "idle"
    
    def test_confidence_update(self):
        """Test confidence level update."""
        generator = get_waveform_generator()
        
        generator.update_confidence(0.8)
        data = generator.get_waveform_data()
        
        assert "confidence" in data or "average_confidence" in data
    
    def test_waveform_data(self):
        """Test getting waveform data."""
        generator = get_waveform_generator()
        
        data = generator.get_waveform_data()
        assert data is not None
        assert "state" in data
        assert "intensity" in data or "amplitudes" in data


class TestLipSyncProcessor:
    """Test lip sync processing."""
    
    def test_processor_initialization(self):
        """Test lip sync processor can be initialized."""
        processor = get_lipsync_processor()
        assert processor is not None
    
    def test_parse_timing_info(self):
        """Test parsing ElevenLabs timing_info."""
        processor = get_lipsync_processor()
        
        # Mock timing_info structure
        timing_info = {
            "phonemes": [
                {
                    "phoneme": "AA",
                    "start": 0.0,
                    "end": 0.1
                },
                {
                    "phoneme": "M",
                    "start": 0.1,
                    "end": 0.2
                }
            ]
        }
        
        phonemes = processor.parse_elevenlabs_timing(timing_info)
        assert isinstance(phonemes, list)
        assert len(phonemes) == 2
    
    def test_mouth_animation_data(self):
        """Test getting mouth animation data."""
        processor = get_lipsync_processor()
        
        # First parse some timing info
        timing_info = {
            "phonemes": [
                {
                    "phoneme": "AA",
                    "start": 0.0,
                    "end": 0.1
                }
            ]
        }
        processor.parse_elevenlabs_timing(timing_info)
        
        # Get animation data for current time
        animation = processor.get_mouth_animation_data(0.05)
        assert animation is not None
        assert "mouth_shape" in animation
        assert "intensity" in animation

