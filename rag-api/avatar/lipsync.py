"""
Lip Sync
ElevenLabs timing_info parsing and phoneme mapping for mouth animation.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json


class PhonemeMapper:
    """
    Maps phonemes to mouth shapes for lip sync animation.
    
    Phoneme Categories:
    - Closed: M, B, P
    - Open: A, E, I, O, U
    - Fricative: F, V, TH, S, Z
    - Plosive: T, D, K, G
    - Nasal: N, NG
    """
    
    def __init__(self):
        """Initialize phoneme mapper."""
        # Phoneme to mouth shape mapping
        self.phoneme_map = {
            # Closed
            "M": "closed",
            "B": "closed",
            "P": "closed",
            # Open vowels
            "AA": "open",
            "AE": "open",
            "AH": "open",
            "AO": "open",
            "AW": "open",
            "AY": "open",
            "EH": "open",
            "ER": "open",
            "EY": "open",
            "IH": "open",
            "IY": "open",
            "OW": "open",
            "OY": "open",
            "UH": "open",
            "UW": "open",
            # Fricative
            "F": "fricative",
            "V": "fricative",
            "TH": "fricative",
            "DH": "fricative",
            "S": "fricative",
            "Z": "fricative",
            "SH": "fricative",
            "ZH": "fricative",
            "HH": "fricative",
            # Plosive
            "T": "plosive",
            "D": "plosive",
            "K": "plosive",
            "G": "plosive",
            # Nasal
            "N": "nasal",
            "NG": "nasal",
            # Other
            "L": "lateral",
            "R": "r",
            "W": "w",
            "Y": "y"
        }
    
    def map_phoneme(self, phoneme: str) -> str:
        """
        Map phoneme to mouth shape.
        
        Args:
            phoneme: Phoneme code
            
        Returns:
            Mouth shape name
        """
        return self.phoneme_map.get(phoneme.upper(), "neutral")
    
    def get_mouth_shape_intensity(self, mouth_shape: str) -> float:
        """
        Get intensity for mouth shape (0.0 to 1.0).
        
        Args:
            mouth_shape: Mouth shape name
            
        Returns:
            Intensity value
        """
        intensity_map = {
            "closed": 0.0,
            "neutral": 0.3,
            "fricative": 0.5,
            "plosive": 0.6,
            "open": 1.0,
            "lateral": 0.4,
            "r": 0.5,
            "w": 0.7,
            "y": 0.6,
            "nasal": 0.2
        }
        return intensity_map.get(mouth_shape, 0.3)


class LipSyncProcessor:
    """
    Processes ElevenLabs timing_info for lip sync animation.
    
    Features:
    - ElevenLabs timing_info parsing
    - Phoneme mapping
    - Mouth animation data
    - Sync accuracy
    """
    
    def __init__(self):
        """Initialize lip sync processor."""
        self.phoneme_mapper = PhonemeMapper()
        self.current_phonemes: List[Dict] = []
    
    def parse_elevenlabs_timing(self, timing_info: Dict) -> List[Dict]:
        """
        Parse ElevenLabs timing_info JSON.
        
        Args:
            timing_info: ElevenLabs timing_info structure
            
        Returns:
            List of phoneme timing data
        """
        try:
            phonemes = []
            
            # ElevenLabs timing_info structure:
            # {
            #   "characters": [...],
            #   "phonemes": [...],
            #   "words": [...]
            # }
            
            if "phonemes" in timing_info:
                for phoneme_data in timing_info["phonemes"]:
                    phoneme = phoneme_data.get("phoneme", "")
                    start = phoneme_data.get("start", 0.0)
                    end = phoneme_data.get("end", 0.0)
                    duration = end - start
                    
                    mouth_shape = self.phoneme_mapper.map_phoneme(phoneme)
                    intensity = self.phoneme_mapper.get_mouth_shape_intensity(mouth_shape)
                    
                    phonemes.append({
                        "phoneme": phoneme,
                        "mouth_shape": mouth_shape,
                        "intensity": intensity,
                        "start": start,
                        "end": end,
                        "duration": duration
                    })
            
            self.current_phonemes = phonemes
            return phonemes
            
        except Exception as e:
            return []
    
    def get_mouth_animation_data(self, current_time: float) -> Dict:
        """
        Get mouth animation data for current time.
        
        Args:
            current_time: Current playback time in seconds
            
        Returns:
            Dict with mouth animation data
        """
        if not self.current_phonemes:
            return {
                "mouth_shape": "neutral",
                "intensity": 0.3,
                "phoneme": "",
                "timestamp": datetime.now().isoformat()
            }
        
        # Find current phoneme based on time
        current_phoneme = None
        for phoneme_data in self.current_phonemes:
            if phoneme_data["start"] <= current_time <= phoneme_data["end"]:
                current_phoneme = phoneme_data
                break
        
        if current_phoneme:
            return {
                "mouth_shape": current_phoneme["mouth_shape"],
                "intensity": current_phoneme["intensity"],
                "phoneme": current_phoneme["phoneme"],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Return neutral if no phoneme matches
            return {
                "mouth_shape": "neutral",
                "intensity": 0.3,
                "phoneme": "",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_all_phonemes(self) -> List[Dict]:
        """
        Get all parsed phonemes.
        
        Returns:
            List of phoneme data
        """
        return self.current_phonemes
    
    def clear_phonemes(self):
        """Clear current phonemes."""
        self.current_phonemes.clear()


# Global lip sync processor instance
lipsync_processor = LipSyncProcessor()

def get_lipsync_processor() -> LipSyncProcessor:
    """Get global lip sync processor instance."""
    return lipsync_processor

