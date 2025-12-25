"""
LS1A Audio Pipeline

Real-time audio processing pipeline with:
- Deepgram WebSocket for STT (Speech-to-Text)
- OpenAI streaming LLM
- ElevenLabs streaming TTS (Text-to-Speech)
- Barge-in detection
- Budget tracking
"""

import asyncio
import json
import os
import base64
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import websockets
from deepgram import DeepgramClient, PrerecordedOptions, LiveOptions, LiveTranscriptionEvents
from openai import AsyncOpenAI
from elevenlabs import AsyncElevenLabs
from .models import LiveSession
from .live_session_storage import LiveSessionStorage
from .cost import CostTracker


class LS1APipeline:
    """
    LS1A Audio Pipeline for real-time voice interactions.
    
    Features:
    - Sub-1000ms latency (target)
    - Barge-in detection (<50ms response)
    - Budget enforcement
    - Session state management
    """
    
    def __init__(
        self,
        session: LiveSession,
        session_storage: LiveSessionStorage,
        cost_tracker: CostTracker,
        deepgram_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None
    ):
        """
        Initialize LS1A pipeline.
        
        Args:
            session: LiveSession instance
            session_storage: LiveSessionStorage instance
            cost_tracker: CostTracker instance
            deepgram_api_key: Deepgram API key (defaults to env var)
            openai_api_key: OpenAI API key (defaults to env var)
            elevenlabs_api_key: ElevenLabs API key (defaults to env var)
        """
        self.session = session
        self.session_storage = session_storage
        self.cost_tracker = cost_tracker
        
        # API clients
        self.deepgram_api_key = deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
        
        if not self.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable required")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable required")
        
        self.deepgram = DeepgramClient(self.deepgram_api_key)
        self.openai = AsyncOpenAI(api_key=self.openai_api_key)
        self.elevenlabs = AsyncElevenLabs(api_key=self.elevenlabs_api_key)
        
        # Pipeline state
        self.is_speaking = False  # TTS playback state
        self.is_listening = False  # User speaking state
        self.transcript_buffer = ""  # Current transcript
        self.llm_response_buffer = ""  # Streaming LLM response
        self.tts_queue = asyncio.Queue()  # TTS audio chunks queue
        self.barge_in_detected = False  # Barge-in flag
        
        # Audio tracking
        self.audio_start_time: Optional[datetime] = None
        self.total_audio_seconds = 0.0
        
        # Callbacks
        self.on_transcript: Optional[Callable[[str, bool], None]] = None  # (text, is_final)
        self.on_audio_chunk: Optional[Callable[[bytes], None]] = None  # (audio_bytes)
        self.on_budget_warning: Optional[Callable[[float], None]] = None  # (utilization)
        self.on_error: Optional[Callable[[Exception], None]] = None  # (error)
    
    async def connect_deepgram(self):
        """
        Connect to Deepgram WebSocket for real-time transcription.
        
        Returns:
            Deepgram connection object
        """
        # Connection options
        options = LiveOptions(
            model="nova-2",  # or "nova-3" for better accuracy
            language="en-US",
            smart_format=True,
            interim_results=True,  # Get partial transcripts
            utterance_end_ms=1000,  # 1 second silence = end of utterance
            vad_events=True,  # Voice activity detection for barge-in
            sample_rate=16000,  # 16kHz audio
            channels=1,
            encoding="linear16"
        )
        
        # Create connection using Deepgram SDK
        connection = self.deepgram.listen.live.v("1")
        
        # Register event handlers
        connection.on(LiveTranscriptionEvents.Open, self._on_deepgram_open)
        connection.on(LiveTranscriptionEvents.Transcript, self._on_deepgram_transcript)
        connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_deepgram_utterance_end)
        connection.on(LiveTranscriptionEvents.SpeechStarted, self._on_deepgram_speech_started)
        connection.on(LiveTranscriptionEvents.Error, self._on_deepgram_error)
        
        # Start connection
        if not await connection.start(options):
            raise ConnectionError("Failed to connect to Deepgram")
        
        self.deepgram_connection = connection
        return connection
    
    def _on_deepgram_open(self, *args, **kwargs):
        """Handle Deepgram connection open."""
        print(f"[LS1A] Deepgram connected for session {self.session.id}")
    
    def _on_deepgram_transcript(self, result, **kwargs):
        """Handle Deepgram transcript event."""
        try:
            channel = result.channel
            alternatives = channel.alternatives
            
            if alternatives and len(alternatives) > 0:
                text = alternatives[0].transcript
                is_final = result.is_final
                
                if text:
                    if is_final:
                        # Final transcript - append to buffer
                        self.transcript_buffer = text
                    else:
                        # Partial transcript - update current
                        self.transcript_buffer = text
                    
                    # Update session transcript
                    self._update_session_transcript(text, is_final)
                    
                    # Callback
                    if self.on_transcript:
                        asyncio.create_task(self._call_callback(
                            self.on_transcript, text, is_final
                        ))
                    
                    # If final, trigger LLM
                    if is_final and text:
                        asyncio.create_task(self._process_llm(text))
        except Exception as e:
            print(f"[LS1A] Transcript error: {e}")
            if self.on_error:
                asyncio.create_task(self._call_callback(self.on_error, e))
    
    def _on_deepgram_utterance_end(self, result, **kwargs):
        """Handle Deepgram utterance end (user finished speaking)."""
        if self.transcript_buffer:
            # Finalize transcript
            self._update_session_transcript(self.transcript_buffer, is_final=True)
            # Process with LLM
            asyncio.create_task(self._process_llm(self.transcript_buffer))
            self.transcript_buffer = ""
    
    def _on_deepgram_speech_started(self, result, **kwargs):
        """Handle Deepgram speech started (barge-in detection)."""
        self.is_listening = True
        self.barge_in_detected = True
        
        # Cancel TTS if speaking
        if self.is_speaking:
            print("[LS1A] Barge-in detected, canceling TTS")
            self.is_speaking = False
            # Clear TTS queue
            while not self.tts_queue.empty():
                try:
                    self.tts_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
    
    def _on_deepgram_error(self, error, **kwargs):
        """Handle Deepgram error."""
        print(f"[LS1A] Deepgram error: {error}")
        if self.on_error:
            asyncio.create_task(self._call_callback(self.on_error, Exception(str(error))))
    
    async def _call_callback(self, callback: Callable, *args):
        """Helper to call callback safely."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            print(f"[LS1A] Callback error: {e}")
    
    async def _process_llm(self, transcript: str):
        """
        Process transcript with OpenAI streaming LLM.
        
        Args:
            transcript: User transcript text
        """
        try:
            # Check budget before LLM call
            budget_status = self.cost_tracker.get_budget_status(self.session.user_id)
            if budget_status.get("text_tokens", {}).get("utilization", 0) >= 1.0:
                # Budget exhausted
                await self._handle_budget_exhausted()
                return
            
            # Prepare messages
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant. Respond concisely."},
                {"role": "user", "content": transcript}
            ]
            
            # Stream LLM response
            self.llm_response_buffer = ""
            stream = await self.openai.chat.completions.create(
                model="gpt-4o",  # or "gpt-4o-mini" for faster/lower cost
                messages=messages,
                stream=True,
                max_tokens=500  # Keep responses concise for voice
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    self.llm_response_buffer += text
            
            # Process TTS
            if self.llm_response_buffer and not self.barge_in_detected:
                await self._process_tts(self.llm_response_buffer)
            
            self.llm_response_buffer = ""
            
        except Exception as e:
            print(f"[LS1A] LLM error: {e}")
            if self.on_error:
                self.on_error(e)
    
    async def _process_tts(self, text: str):
        """
        Process text with ElevenLabs streaming TTS.
        
        Args:
            text: Text to convert to speech
        """
        try:
            # Check if barge-in occurred
            if self.barge_in_detected:
                return
            
            self.is_speaking = True
            
            # Stream TTS audio
            voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Default voice
            model_id = "eleven_flash_v2_5"  # Fast, low-latency model
            
            audio_stream = await self.elevenlabs.text_to_speech.convert_as_stream(
                voice_id=voice_id,
                model_id=model_id,
                text=text
            )
            
            # Stream audio chunks
            async for audio_chunk in audio_stream:
                # Check for barge-in
                if self.barge_in_detected:
                    break
                
                # Send audio chunk via callback
                if self.on_audio_chunk:
                    self.on_audio_chunk(audio_chunk)
                
                # Track audio time
                self._track_audio_time(len(audio_chunk))
            
            self.is_speaking = False
            self.barge_in_detected = False
            
        except Exception as e:
            print(f"[LS1A] TTS error: {e}")
            self.is_speaking = False
            if self.on_error:
                self.on_error(e)
    
    def _update_session_transcript(self, text: str, is_final: bool):
        """Update session transcript in storage."""
        try:
            if is_final:
                # Append to partial transcript
                current = self.session.transcript_partial
                updated = current + " " + text if current else text
                self.session_storage.update(
                    self.session.id,
                    self.session.user_id,
                    {"transcript_partial": updated}
                )
            else:
                # Update partial transcript
                self.session_storage.update(
                    self.session.id,
                    self.session.user_id,
                    {"transcript_partial": text}
                )
        except Exception as e:
            print(f"[LS1A] Error updating transcript: {e}")
    
    def _track_audio_time(self, audio_bytes: int):
        """
        Track audio time for budget enforcement.
        
        Args:
            audio_bytes: Size of audio chunk in bytes
        """
        # Estimate audio duration (assuming 24kHz, 16-bit, mono)
        # bytes / (sample_rate * channels * bytes_per_sample)
        duration_seconds = audio_bytes / (24000 * 1 * 2)  # 24kHz, mono, 16-bit
        self.total_audio_seconds += duration_seconds
        
        # Update session
        audio_minutes = self.total_audio_seconds / 60.0
        self.session_storage.update(
            self.session.id,
            self.session.user_id,
            {"audio_minutes_used": audio_minutes}
        )
        
        # Track in cost tracker
        self.cost_tracker.track_usage(
            user_id=self.session.user_id,
            audio_minutes=duration_seconds / 60.0
        )
        
        # Check budget
        budget_status = self.cost_tracker.get_budget_status(self.session.user_id)
        audio_utilization = budget_status.get("audio_minutes", {}).get("utilization", 0)
        
        # Warning at 80%
        if audio_utilization >= 0.8 and audio_utilization < 1.0:
            if self.on_budget_warning:
                self.on_budget_warning(audio_utilization)
        
        # Auto-pause at 100%
        if audio_utilization >= 1.0:
            asyncio.create_task(self._handle_budget_exhausted())
    
    async def _handle_budget_exhausted(self):
        """Handle budget exhaustion by pausing session."""
        print(f"[LS1A] Budget exhausted for session {self.session.id}")
        
        # Pause session
        self.session_storage.update(
            self.session.id,
            self.session.user_id,
            {"state": "PAUSED"}
        )
        
        # Notify via callback
        if self.on_budget_warning:
            self.on_budget_warning(1.0)
    
    async def send_audio(self, audio_data: bytes):
        """
        Send audio data to Deepgram for transcription.
        
        Args:
            audio_data: Raw PCM audio bytes (16-bit, 16kHz, mono)
        """
        if hasattr(self, 'deepgram_connection') and self.deepgram_connection:
            try:
                self.deepgram_connection.send(audio_data)
            except Exception as e:
                print(f"[LS1A] Error sending audio to Deepgram: {e}")
                if self.on_error:
                    await self._call_callback(self.on_error, e)
    
    async def close(self):
        """Close pipeline and cleanup."""
        self.is_speaking = False
        self.is_listening = False
        self.barge_in_detected = False
        
        # Finalize transcript
        if self.session.transcript_partial:
            self.session_storage.update(
                self.session.id,
                self.session.user_id,
                {
                    "transcript_final": self.session.transcript_partial,
                    "state": "ENDED"
                }
            )

