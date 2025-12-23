"""
WebCompanion: Browser-compatible version of AICompanion.
Receives audio via WebSocket instead of local microphone.
"""
import asyncio
import base64
import os
import time
from typing import Optional, AsyncGenerator
from colorama import Fore, Style, init

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
from openai import AsyncOpenAI
from elevenlabs.client import ElevenLabs

from memory_manager import MemoryManager
from config import (
    SYSTEM_PROMPT,
    VOICE_ID,
    ELEVEN_MODEL_ID,
    DG_MODEL,
    DG_UTTERANCE_END_MS,
    OPENAI_MODEL,
    MAX_CONTEXT_TURNS,
)

init(autoreset=True)


class WebCompanion:
    """
    Browser-compatible companion that receives audio via WebSocket
    and streams responses back through WebSocket.
    """
    
    def __init__(self, websocket=None):
        """
        Initialize companion with optional WebSocket for browser communication.
        
        Args:
            websocket: FastAPI WebSocket connection (optional, for sending responses)
        """
        self.websocket = websocket
        self.memory = MemoryManager()
        
        # Initialize API Clients
        try:
            dg_key = os.getenv("DEEPGRAM_API_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            eleven_key = os.getenv("ELEVENLABS_API_KEY")
            
            if not dg_key:
                raise ValueError("DEEPGRAM_API_KEY environment variable is required")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            if not eleven_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable is required")
            
            self.dg_client = DeepgramClient(dg_key)
            self.openai_client = AsyncOpenAI(api_key=openai_key)
            self.eleven_client = ElevenLabs(api_key=eleven_key)
        except Exception as e:
            print(Fore.RED + f"Error initializing clients: {e}")
            raise
        
        # Deepgram connection
        self.dg_connection = None
        
        # Queues for inter-task communication
        self.transcript_queue = asyncio.Queue()
        self.audio_chunk_queue = asyncio.Queue()  # Browser audio chunks
        
        # Conversation context
        self.conversation_history = []
        
        # State flags
        self.is_speaking = False
        self.current_playback_task: Optional[asyncio.Task] = None
        self.processing_task: Optional[asyncio.Task] = None
    
    async def initialize_deepgram(self):
        """Initialize Deepgram Live connection."""
        options = LiveOptions(
            model=DG_MODEL,
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms=DG_UTTERANCE_END_MS,
            vad_events=True
        )
        
        self.dg_connection = self.dg_client.listen.live.v("1")
        
        # Event handlers
        def on_message(result, **kwargs):
            sentence = result.channel.alternatives[0].transcript if result.channel.alternatives else ""
            if len(sentence) == 0:
                return
            
            # Interruption detection
            if result.is_final is False and len(sentence) > 5:
                if self.is_speaking:
                    if self.current_playback_task and not self.current_playback_task.done():
                        self.current_playback_task.cancel()
                        # Schedule send to browser (will be handled by event loop)
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    self.send_to_browser({
                                        "type": "interrupted",
                                        "message": "User interrupting"
                                    }),
                                    loop
                                )
                        except:
                            pass
            
            if result.is_final:
                print(Fore.CYAN + f"You: {sentence}")
                asyncio.create_task(self.send_to_browser({
                    "type": "transcript",
                    "text": sentence,
                    "role": "user"
                }))
                # Put transcript in queue for processing
                # Use thread-safe method since this is called from Deepgram callback thread
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(
                            self.transcript_queue.put(sentence),
                            loop
                        )
                    else:
                        loop.run_until_complete(self.transcript_queue.put(sentence))
                except RuntimeError:
                    # No event loop, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    asyncio.run_coroutine_threadsafe(
                        self.transcript_queue.put(sentence),
                        loop
                    )
        
        def on_speech_started(speech_started, **kwargs):
            """
            VAD event: User started speaking.
            Per guidance: If AI is speaking and user starts speaking, interrupt AI.
            """
            if self.is_speaking:
                if self.current_playback_task and not self.current_playback_task.done():
                    self.current_playback_task.cancel()
                    self.is_speaking = False
                    # Notify browser of interruption
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.run_coroutine_threadsafe(
                                self.send_to_browser({
                                    "type": "interrupted"
                                }),
                                loop
                            )
                    except:
                        pass
                    print(Fore.RED + "[Interrupted by user speech]")
        
        def on_error(error, **kwargs):
            print(Fore.RED + f"Deepgram error: {error}")
            asyncio.create_task(self.send_to_browser({
                "type": "error",
                "message": f"Deepgram error: {error}"
            }))
        
        # Register event handlers (per guidance: use VAD events for interruption)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        
        if self.dg_connection.start(options) is False:
            raise Exception("Failed to start Deepgram connection")
        
        print(Fore.GREEN + "Deepgram connection established")
    
    async def send_to_browser(self, data: dict):
        """Send JSON data to browser via WebSocket."""
        if self.websocket:
            try:
                import json
                await self.websocket.send_json(data)
            except Exception as e:
                print(Fore.RED + f"Error sending to browser: {e}")
    
    def process_audio_chunk(self, audio_bytes: bytes):
        """Process audio chunk from browser and send to Deepgram (synchronous)."""
        if self.dg_connection:
            try:
                self.dg_connection.send(audio_bytes)
            except Exception as e:
                print(Fore.RED + f"Error sending audio to Deepgram: {e}")
                # Try to send error to browser if websocket available
                if self.websocket:
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.run_coroutine_threadsafe(
                                self.send_to_browser({
                                    "type": "error",
                                    "message": f"Deepgram error: {str(e)}"
                                }),
                                loop
                            )
                    except:
                        pass
    
    async def start_processing_loop(self):
        """Start the main processing loop for transcripts."""
        print(Fore.GREEN + "Starting processing loop...")
        
        while True:
            try:
                # Wait for transcript
                user_text = await self.transcript_queue.get()
                
                # Handle interruption
                if self.current_playback_task and not self.current_playback_task.done():
                    self.current_playback_task.cancel()
                    try:
                        await self.current_playback_task
                    except asyncio.CancelledError:
                        pass
                
                # Generate and speak
                self.current_playback_task = asyncio.create_task(
                    self.generate_and_speak(user_text)
                )
                try:
                    await self.current_playback_task
                except asyncio.CancelledError:
                    pass
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(Fore.RED + f"Error in processing loop: {e}")
    
    async def generate_and_speak(self, user_text: str):
        """
        Generate response and stream TTS audio to browser.
        """
        self.is_speaking = True
        
        # Memory retrieval
        context_memory = self.memory.get_relevant_context(user_text)
        
        # Construct messages (per guidance: insert memory at position 1)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if context_memory:
            # Insert memory context at position 1 (after system prompt, before user message)
            # This matches the guidance document pattern
            messages.insert(1, {
                "role": "system",
                "content": f"Relevant Memories: {context_memory}"
            })
        
        # Add conversation history
        for turn in self.conversation_history[-MAX_CONTEXT_TURNS:]:
            messages.append(turn)
        
        messages.append({"role": "user", "content": user_text})
        
        # LLM streaming
        print(Fore.MAGENTA + "Thinking...", end="", flush=True)
        start_time = time.time()
        
        try:
            response_stream = await self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                stream=True,
                temperature=0.7
            )
            
            # Text iterator for ElevenLabs
            async def text_iterator() -> AsyncGenerator[str, None]:
                full_response = ""
                async for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        full_response += delta
                        print(delta, end="", flush=True)
                        
                        # Send text chunk to browser
                        await self.send_to_browser({
                            "type": "text_chunk",
                            "text": delta
                        })
                        
                        yield delta
                
                # Save memory
                self.memory.add_memory(user_text, full_response)
                self.conversation_history.append({"role": "user", "content": user_text})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                # Trim history
                if len(self.conversation_history) > MAX_CONTEXT_TURNS * 2:
                    self.conversation_history = self.conversation_history[-MAX_CONTEXT_TURNS * 2:]
            
            # ElevenLabs streaming
            audio_stream = self.eleven_client.text_to_speech.stream(
                voice_id=VOICE_ID,
                model_id=ELEVEN_MODEL_ID,
                text=text_iterator()
            )
            
            ttft = (time.time() - start_time) * 1000
            print(Fore.BLUE + f"\n[TTFT: {ttft:.0f}ms]")
            
            await self.send_to_browser({
                "type": "response_start",
                "ttft_ms": ttft
            })
            
            # Stream audio chunks to browser
            for chunk in audio_stream:
                if chunk:
                    # Encode audio chunk as base64 for browser
                    audio_b64 = base64.b64encode(chunk).decode('utf-8')
                    await self.send_to_browser({
                        "type": "audio_chunk",
                        "audio": audio_b64,
                        "format": "mp3"
                    })
            
            total_time = (time.time() - start_time) * 1000
            print(Fore.GREEN + f"[Total: {total_time:.0f}ms]\n")
            
            await self.send_to_browser({
                "type": "response_complete",
                "total_ms": total_time
            })
        
        except Exception as e:
            print(Fore.RED + f"\nError in generate_and_speak: {e}")
            await self.send_to_browser({
                "type": "error",
                "message": str(e)
            })
        finally:
            self.is_speaking = False
    
    async def cleanup(self):
        """Clean up resources."""
        if self.dg_connection:
            try:
                self.dg_connection.finish()
            except:
                pass
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

