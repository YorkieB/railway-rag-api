"""
AudioManager: Handles PyAudio input/output streams for real-time audio processing.
Based on the guidance document: Building a Real-Time AI Companion.txt
"""
import pyaudio
from typing import Optional
import numpy as np

from config import FORMAT, CHANNELS, RATE, CHUNK

# Map string format to PyAudio constant
PA_FORMAT = pyaudio.paInt16


class AudioManager:
    """
    Manages the low-level PyAudio streams for input (mic) and output (speakers).
    Provides non-blocking audio I/O for real-time processing.
    """
    
    def __init__(self):
        """Initialize PyAudio instance."""
        self.p = pyaudio.PyAudio()
        self.stream_in: Optional[pyaudio.Stream] = None
        self.stream_out: Optional[pyaudio.Stream] = None
    
    def start_input_stream(self, callback):
        """
        Opens the microphone input stream.
        
        Args:
            callback: Function to call with audio data chunks (frames, time_info, status)
        """
        if self.stream_in is None:
            self.stream_in = self.p.open(
                format=PA_FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback
            )
            self.stream_in.start_stream()
    
    def start_output_stream(self):
        """Opens the speaker output stream."""
        if self.stream_out is None:
            self.stream_out = self.p.open(
                format=PA_FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK
            )
    
    def write_audio(self, audio_data: bytes):
        """
        Writes a chunk of audio bytes to the speaker.
        
        Args:
            audio_data: Raw audio bytes (Int16 PCM format)
        """
        if self.stream_out and self.stream_out.is_active():
            try:
                self.stream_out.write(audio_data)
            except Exception as e:
                print(f"Error writing audio: {e}")
    
    def read_audio_chunk(self) -> Optional[bytes]:
        """
        Reads a chunk of audio from the microphone.
        Non-blocking read.
        
        Returns:
            Audio bytes or None if no data available
        """
        if self.stream_in and self.stream_in.is_active():
            try:
                data = self.stream_in.read(CHUNK, exception_on_overflow=False)
                return data
            except Exception as e:
                print(f"Error reading audio: {e}")
        return None
    
    def stop_input_stream(self):
        """Stops and closes the input stream."""
        if self.stream_in:
            try:
                self.stream_in.stop_stream()
                self.stream_in.close()
            except:
                pass
            self.stream_in = None
    
    def stop_output_stream(self):
        """Stops and closes the output stream."""
        if self.stream_out:
            try:
                self.stream_out.stop_stream()
                self.stream_out.close()
            except:
                pass
            self.stream_out = None
    
    def cleanup(self):
        """Closes all streams and terminates PyAudio to free system resources."""
        self.stop_input_stream()
        self.stop_output_stream()
        try:
            self.p.terminate()
        except:
            pass

