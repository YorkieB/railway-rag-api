"""
AICompanion: The central orchestrator connecting STT, LLM, Memory, and TTS.
Based on the guidance document: Building a Real-Time AI Companion.txt
"""
import asyncio
import os
import sys
import time
from typing import AsyncGenerator, Optional
from colorama import Fore, Style, init

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from openai import AsyncOpenAI
from elevenlabs.client import ElevenLabs

from audio_manager import AudioManager
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

# Initialize colorama
init(autoreset=True)


class AICompanion:
    """
    The central orchestrator connecting STT (Deepgram), LLM (OpenAI), 
    Memory (ChromaDB), and TTS (ElevenLabs).
    Implements real-time conversation with sub-800ms latency target.
    """
    
    def __init__(self):
        """Initialize all components and API clients."""
        self.audio = AudioManager()
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
            sys.exit(1)
        
        # Queues for inter-task communication
        self.transcript_queue = asyncio.Queue()
        
        # Conversation context (sliding window)
        self.conversation_history = []
        
        # Flags for state management
        self.is_speaking = False
        self.current_playback_task: Optional[asyncio.Task] = None
        self.dg_connection = None
        self.microphone = None
    
    async def run(self):
        """Main execution loop."""
        print(Fore.GREEN + Style.BRIGHT + "Starting AI Companion... (Press Ctrl+C to stop)")
        
        # 1. Setup Deepgram Live Connection
        options = LiveOptions(
            model=DG_MODEL,
            language="en-US",
            smart_format=True,  # Adds punctuation
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms=DG_UTTERANCE_END_MS,
            vad_events=True  # Voice Activity Detection for interruption
        )
        
        self.dg_connection = self.dg_client.listen.live.v("1")
        
        # 2. Define Event Handlers
        loop = asyncio.get_event_loop()
        
        def on_message(result, **kwargs):
            """Callback for when Deepgram sends transcript data."""
            sentence = result.channel.alternatives[0].transcript if result.channel.alternatives else ""
            if len(sentence) == 0:
                return
            
            # Interruption Detection: If user starts speaking while AI is speaking
            if result.is_final is False and len(sentence) > 5:
                if self.is_speaking:
                    # Cancel current playback
                    if self.current_playback_task and not self.current_playback_task.done():
                        self.current_playback_task.cancel()
                        print(Fore.YELLOW + "[User interrupting...]")
            
            if result.is_final:
                print(Fore.CYAN + f"You: {sentence}")
                # Put the text into the queue for processing
                asyncio.run_coroutine_threadsafe(
                    self.transcript_queue.put(sentence), loop
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
                    print(Fore.RED + "[Interrupted by user speech]")
        
        def on_utterance_end(utterance_end, **kwargs):
            """Callback for silence detection."""
            # Deepgram detected end of utterance
            pass
        
        def on_error(error, **kwargs):
            """Callback for Deepgram errors."""
            print(Fore.RED + f"Deepgram error: {error}")
        
        # Register event handlers (per guidance: use VAD events for interruption)
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        self.dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        
        # 3. Start Audio Output Stream
        self.audio.start_output_stream()
        
        # 4. Start Deepgram Connection
        if self.dg_connection.start(options) is False:
            print(Fore.RED + "Failed to connect to Deepgram.")
            return
        
        # 5. Start Microphone (feeds Deepgram in background thread)
        self.microphone = Microphone(self.dg_connection.send)
        self.microphone.start()
        
        print(Fore.GREEN + "System Ready. Say something...")
        
        # 6. Main Process Loop
        try:
            while True:
                # Wait here until a sentence is received from Deepgram
                user_text = await self.transcript_queue.get()
                
                # Barge-in logic: If we were speaking, stop
                if self.current_playback_task and not self.current_playback_task.done():
                    self.current_playback_task.cancel()
                    print(Fore.RED + "[Interrupted]")
                    try:
                        await self.current_playback_task
                    except asyncio.CancelledError:
                        pass
                
                # Generate and Speak
                self.current_playback_task = asyncio.create_task(
                    self.generate_and_speak(user_text)
                )
                try:
                    await self.current_playback_task
                except asyncio.CancelledError:
                    pass  # Task cancellation is normal flow here
        
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nShutting down...")
        except Exception as e:
            print(Fore.RED + f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    async def generate_and_speak(self, user_text: str):
        """
        The Core Logic: RAG -> LLM -> TTS -> Audio
        
        Pipeline:
        1. Retrieve relevant memories from ChromaDB
        2. Construct prompt with context
        3. Stream LLM response token by token
        4. Pipe tokens to ElevenLabs for streaming TTS
        5. Play audio chunks immediately
        6. Save conversation to memory
        """
        self.is_speaking = True
        
        # A. Memory Retrieval (RAG)
        context_memory = self.memory.get_relevant_context(user_text)
        
        # B. Construct Messages with Context Window Management
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Inject relevant memories if available
        if context_memory:
            messages.append({
                "role": "system",
                "content": f"Relevant Memories: {context_memory}"
            })
        
        # Add conversation history (sliding window)
        for turn in self.conversation_history[-MAX_CONTEXT_TURNS:]:
            messages.append(turn)
        
        # Add current user message
        messages.append({"role": "user", "content": user_text})
        
        # C. LLM Generation (Streaming)
        print(Fore.MAGENTA + "Thinking...", end="", flush=True)
        start_time = time.time()
        
        try:
            response_stream = await self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                stream=True,
                temperature=0.7
            )
            
            # D. The Pipeline: LLM Stream -> ElevenLabs Stream
            # Define async generator that yields text chunks to ElevenLabs
            async def text_iterator() -> AsyncGenerator[str, None]:
                full_response = ""
                async for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        delta = chunk.choices[0].delta.content
                        full_response += delta
                        print(delta, end="", flush=True)
                        yield delta
                
                # Once stream is done, save memory and update conversation history
                self.memory.add_memory(user_text, full_response)
                self.conversation_history.append({"role": "user", "content": user_text})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                # Trim conversation history if too long
                if len(self.conversation_history) > MAX_CONTEXT_TURNS * 2:
                    self.conversation_history = self.conversation_history[-MAX_CONTEXT_TURNS * 2:]
            
            # E. ElevenLabs Streaming TTS
            # This converts the text_iterator into an audio stream
            audio_stream = self.eleven_client.text_to_speech.stream(
                voice_id=VOICE_ID,
                model_id=ELEVEN_MODEL_ID,
                text=text_iterator()
            )
            
            ttft = (time.time() - start_time) * 1000
            print(Fore.BLUE + f"\n[TTFT: {ttft:.0f}ms]")
            
            # F. Playback Loop
            # Iterate over audio bytes from ElevenLabs and write to PyAudio
            loop = asyncio.get_event_loop()
            
            for chunk in audio_stream:
                if chunk:
                    # Use run_in_executor to avoid blocking the asyncio loop
                    await loop.run_in_executor(None, self.audio.write_audio, chunk)
            
            total_time = (time.time() - start_time) * 1000
            print(Fore.GREEN + f"[Total: {total_time:.0f}ms]\n")
        
        except Exception as e:
            print(Fore.RED + f"\nError in generate_and_speak: {e}")
        finally:
            self.is_speaking = False
    
    def cleanup(self):
        """Clean up all resources."""
        print(Fore.YELLOW + "Cleaning up...")
        
        if self.microphone:
            try:
                self.microphone.finish()
            except:
                pass
        
        if self.dg_connection:
            try:
                self.dg_connection.finish()
            except:
                pass
        
        self.audio.cleanup()
        print(Fore.GREEN + "Cleanup complete.")


# --- ENTRY POINT ---
if __name__ == "__main__":
    # Create the Event Loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    companion = AICompanion()
    
    try:
        loop.run_until_complete(companion.run())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nDisconnecting...")
    finally:
        loop.close()

