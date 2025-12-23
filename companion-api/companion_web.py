"""
WebCompanion: Browser-compatible version of AICompanion.
Receives audio via WebSocket instead of local microphone.
"""
import asyncio
import base64
import os
import time
import httpx
import json
from typing import Optional, AsyncGenerator, Dict, Any
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
    RAG_API_URL,
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
        self.rag_api_url = RAG_API_URL
        self.browser_session_id: Optional[str] = None
        
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
            self.http_client = httpx.AsyncClient(timeout=30.0)
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
    
    async def _ensure_browser_session(self) -> str:
        """Ensure browser session exists, create if needed."""
        if not self.browser_session_id:
            try:
                response = await self.http_client.post(
                    f"{self.rag_api_url}/browser/sessions",
                    params={"user_id": "companion"}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.browser_session_id = data.get("session_id")
                    print(Fore.GREEN + f"Created browser session: {self.browser_session_id}")
                else:
                    print(Fore.RED + f"Failed to create browser session: {response.status_code}")
            except Exception as e:
                print(Fore.RED + f"Error creating browser session: {e}")
        return self.browser_session_id or ""
    
    async def _search_web(self, query: str) -> str:
        """Search the web using browser automation."""
        try:
            session_id = await self._ensure_browser_session()
            if not session_id:
                return "Unable to access web: browser session unavailable"
            
            # Navigate to search engine
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            response = await self.http_client.post(
                f"{self.rag_api_url}/browser/sessions/{session_id}/navigate",
                params={"url": search_url}
            )
            
            if response.status_code != 200:
                return f"Failed to navigate to search: {response.status_code}"
            
            # Get page content
            await asyncio.sleep(2)  # Wait for page load
            
            # Extract text from page
            extract_response = await self.http_client.post(
                f"{self.rag_api_url}/browser/sessions/{session_id}/actions/extract",
                params={"role": "main", "include_text": "true"}
            )
            
            if extract_response.status_code == 200:
                data = extract_response.json()
                text = data.get("text", "")[:2000]  # Limit to 2000 chars
                return f"Search results for '{query}': {text}"
            else:
                return f"Found search results for '{query}' but couldn't extract text"
                
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    async def _browse_web(self, url: str) -> str:
        """Browse a specific URL and extract content."""
        try:
            session_id = await self._ensure_browser_session()
            if not session_id:
                return "Unable to access web: browser session unavailable"
            
            # Navigate to URL
            response = await self.http_client.post(
                f"{self.rag_api_url}/browser/sessions/{session_id}/navigate",
                params={"url": url}
            )
            
            if response.status_code != 200:
                return f"Failed to navigate to {url}: {response.status_code}"
            
            # Wait for page load
            await asyncio.sleep(2)
            
            # Extract text
            extract_response = await self.http_client.post(
                f"{self.rag_api_url}/browser/sessions/{session_id}/actions/extract",
                params={"role": "main", "include_text": "true"}
            )
            
            if extract_response.status_code == 200:
                data = extract_response.json()
                text = data.get("text", "")[:2000]
                title = data.get("title", url)
                return f"Content from {title}: {text}"
            else:
                return f"Navigated to {url} but couldn't extract content"
                
        except Exception as e:
            return f"Error browsing web: {str(e)}"
    
    async def generate_and_speak(self, user_text: str):
        """
        Generate response and stream TTS audio to browser.
        Now with web access capabilities.
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
        
        # Define tools for web access
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for real-time information. Use this when the user asks about current events, news, weather, or any information that might change over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on the web"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "browse_web",
                    "description": "Browse a specific URL to get information from a webpage. Use this when the user provides a URL or asks about content from a specific website.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to browse (must include http:// or https://)"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
        
        # LLM streaming with function calling
        print(Fore.MAGENTA + "Thinking...", end="", flush=True)
        start_time = time.time()
        
        try:
            response_stream = await self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
                temperature=0.7
            )
            
            # Handle streaming with tool calls
            full_response = ""
            tool_calls = []
            current_tool_call = None
            
            async for chunk in response_stream:
                choice = chunk.choices[0] if chunk.choices else None
                if not choice:
                    continue
                
                delta = choice.delta
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        idx = tool_call_delta.index
                        if idx >= len(tool_calls):
                            # New tool call
                            tool_calls.extend([None] * (idx + 1 - len(tool_calls)))
                            tool_calls[idx] = {
                                "id": tool_call_delta.id or "",
                                "type": "function",
                                "function": {"name": "", "arguments": ""}
                            }
                        
                        if tool_calls[idx]:
                            if tool_call_delta.id:
                                tool_calls[idx]["id"] = tool_call_delta.id
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    tool_calls[idx]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    tool_calls[idx]["function"]["arguments"] += tool_call_delta.function.arguments
                
                # Handle content
                if delta.content:
                    delta_text = delta.content
                    full_response += delta_text
                    print(delta_text, end="", flush=True)
                    
                    # Send text chunk to browser
                    await self.send_to_browser({
                        "type": "text_chunk",
                        "text": delta_text
                    })
            
            # Process tool calls if any
            if tool_calls:
                print(Fore.CYAN + "\n[Using web access...]")
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": full_response if full_response else None,
                    "tool_calls": [tc for tc in tool_calls if tc]
                })
                
                # Execute tool calls
                for tool_call in tool_calls:
                    if not tool_call:
                        continue
                    
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    # Execute function
                    if function_name == "search_web":
                        result = await self._search_web(function_args.get("query", ""))
                    elif function_name == "browse_web":
                        result = await self._browse_web(function_args.get("url", ""))
                    else:
                        result = f"Unknown function: {function_name}"
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": result
                    })
                
                # Get final response after tool execution
                print(Fore.MAGENTA + "Processing web results...", end="", flush=True)
                final_response = await self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    stream=True,
                    temperature=0.7
                )
                
                full_response = ""
                async for chunk in final_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        delta_text = chunk.choices[0].delta.content
                        full_response += delta_text
                        print(delta_text, end="", flush=True)
                        
                        await self.send_to_browser({
                            "type": "text_chunk",
                            "text": delta_text
                        })
            
            # Save memory
            if full_response:
                self.memory.add_memory(user_text, full_response)
                self.conversation_history.append({"role": "user", "content": user_text})
                self.conversation_history.append({"role": "assistant", "content": full_response})
                
                # Trim history
                if len(self.conversation_history) > MAX_CONTEXT_TURNS * 2:
                    self.conversation_history = self.conversation_history[-MAX_CONTEXT_TURNS * 2:]
                
                # Text iterator for ElevenLabs (use full_response)
                async def text_iterator() -> AsyncGenerator[str, None]:
                    for char in full_response:
                        yield char
                
                # ElevenLabs streaming
                audio_stream = self.eleven_client.text_to_speech.stream(
                    voice_id=VOICE_ID,
                    model_id=ELEVEN_MODEL_ID,
                    text=text_iterator()
                )
            else:
                audio_stream = None
            
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

