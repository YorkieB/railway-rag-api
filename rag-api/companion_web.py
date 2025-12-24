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
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    # Colorama not available - create dummy classes
    class Fore:
        RED = GREEN = BLUE = CYAN = MAGENTA = YELLOW = ""
    class Style:
        RESET_ALL = ""
    COLORAMA_AVAILABLE = False

# Try to import Deepgram SDK
# Use a function to import at runtime to avoid module load failures
def _import_deepgram():
    """Import Deepgram SDK with fallbacks. Returns True if successful, False otherwise"""
    global DEEPGRAM_AVAILABLE, DeepgramClient, LiveOptions, LiveTranscriptionEvents
    
    # First check if already imported
    if DEEPGRAM_AVAILABLE and DeepgramClient is not None:
        print(f"[_import_deepgram] Already imported: DEEPGRAM_AVAILABLE={DEEPGRAM_AVAILABLE}, DeepgramClient={DeepgramClient}")
        return True
    
    print("[_import_deepgram] Attempting to import Deepgram SDK...")
    
    # Check if deepgram package exists
    try:
        import deepgram
        print(f"[_import_deepgram] deepgram package found: {deepgram}, version: {getattr(deepgram, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"[_import_deepgram] deepgram package not found: {e}")
    
    try:
        # For deepgram-sdk v3.0+, the import is from 'deepgram'
        # For v5.x, LiveOptions may not be available - import only DeepgramClient
        print("[_import_deepgram] Trying: from deepgram import DeepgramClient")
        from deepgram import DeepgramClient
        print(f"[_import_deepgram] Successfully imported DeepgramClient: {DeepgramClient}, type: {type(DeepgramClient)}")
        
        # Try to import LiveOptions (may not exist in v5.x)
        try:
            from deepgram import LiveOptions
            print("[_import_deepgram] Successfully imported LiveOptions from deepgram")
        except ImportError:
            # LiveOptions doesn't exist in v5.x - we'll use dict instead
            print("[_import_deepgram] LiveOptions not available in this version (v5.x), will use dict for options")
            LiveOptions = None
        
        # Try to import LiveTranscriptionEvents
        try:
            from deepgram import LiveTranscriptionEvents
            print("[_import_deepgram] Successfully imported LiveTranscriptionEvents from deepgram")
        except ImportError:
            # LiveTranscriptionEvents might be in a different location or not available
            try:
                from deepgram.clients import LiveTranscriptionEvents
                print("[_import_deepgram] Successfully imported LiveTranscriptionEvents from deepgram.clients")
            except ImportError:
                try:
                    from deepgram.clients.listen import LiveTranscriptionEvents
                    print("[_import_deepgram] Successfully imported LiveTranscriptionEvents from deepgram.clients.listen")
                except ImportError:
                    print("[_import_deepgram] LiveTranscriptionEvents not available (optional)")
                    LiveTranscriptionEvents = None
        
        DEEPGRAM_AVAILABLE = True
        print(f"[_import_deepgram] SUCCESS: DEEPGRAM_AVAILABLE=True, DeepgramClient={DeepgramClient}, LiveOptions={LiveOptions}")
        return True
    except ImportError as e1:
        print(f"[_import_deepgram] Failed to import from 'deepgram': {type(e1).__name__}: {e1}")
        import traceback
        traceback.print_exc()
        try:
            # Fallback: try deepgram_sdk (older versions)
            print("[_import_deepgram] Trying fallback: from deepgram_sdk import DeepgramClient, LiveOptions")
            from deepgram_sdk import DeepgramClient, LiveOptions
            try:
                from deepgram_sdk import LiveTranscriptionEvents
            except ImportError:
                LiveTranscriptionEvents = None
            DEEPGRAM_AVAILABLE = True
            print("[_import_deepgram] Successfully imported DeepgramClient from 'deepgram_sdk'")
            return True
        except ImportError as e2:
            print(f"[_import_deepgram] Failed to import from 'deepgram_sdk': {type(e2).__name__}: {e2}")
            traceback.print_exc()
            print("[_import_deepgram] Deepgram SDK not available. Install with: pip install deepgram-sdk")
            DEEPGRAM_AVAILABLE = False
            DeepgramClient = None
            LiveOptions = None
            LiveTranscriptionEvents = None
            return False
    except Exception as e:
        print(f"[_import_deepgram] Unexpected error during import: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        DEEPGRAM_AVAILABLE = False
        DeepgramClient = None
        LiveOptions = None
        LiveTranscriptionEvents = None
        return False

# Initialize at module load
DEEPGRAM_AVAILABLE = False
DeepgramClient = None
LiveOptions = None
LiveTranscriptionEvents = None

# Try to import immediately
_import_deepgram()
from openai import AsyncOpenAI
from elevenlabs.client import ElevenLabs

from companion_memory_manager import MemoryManager
from companion_config import (
    SYSTEM_PROMPT,
    VOICE_ID,
    ELEVEN_MODEL_ID,
    DG_MODEL,
    DG_UTTERANCE_END_MS,
    OPENAI_MODEL,
    MAX_CONTEXT_TURNS,
    RAG_API_URL,
)

# Colorama initialized above


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
            # Debug: Log environment variable check (use print for reliability)
            dg_key = os.getenv("DEEPGRAM_API_KEY")
            openai_key = os.getenv("OPENAI_API_KEY")
            eleven_key = os.getenv("ELEVENLABS_API_KEY")
            
            # Debug logging (use print instead of logger for reliability)
            print(f"[WebCompanion] Environment variable check - DEEPGRAM_API_KEY: {'SET' if dg_key else 'MISSING'} (length: {len(dg_key) if dg_key else 0})")
            print(f"[WebCompanion] Environment variable check - ELEVENLABS_API_KEY: {'SET' if eleven_key else 'MISSING'} (length: {len(eleven_key) if eleven_key else 0})")
            print(f"[WebCompanion] Environment variable check - OPENAI_API_KEY: {'SET' if openai_key else 'MISSING'} (length: {len(openai_key) if openai_key else 0})")
            
            # Debug: Check for common typos
            if not dg_key:
                # Check for common typos
                dg_hyphen = os.getenv("DEEPGRAM_API-KEY")
                dg_lower = os.getenv("deepgram_api_key")
                if dg_hyphen:
                    print("[WebCompanion] WARNING: Found DEEPGRAM_API-KEY (with hyphen) but need DEEPGRAM_API_KEY (with underscore)")
                if dg_lower:
                    print("[WebCompanion] WARNING: Found deepgram_api_key (lowercase) but need DEEPGRAM_API_KEY (uppercase)")
            
            if not dg_key:
                raise ValueError("DEEPGRAM_API_KEY environment variable is required")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            if not eleven_key:
                raise ValueError("ELEVENLABS_API_KEY environment variable is required")
            
            # Verify DeepgramClient is available (not None)
            # Try to import again at runtime in case module load failed
            if not DEEPGRAM_AVAILABLE or DeepgramClient is None:
                print("[WebCompanion] DeepgramClient not available at module load, trying runtime import...")
                success = _import_deepgram()
                if not success or DeepgramClient is None:
                    raise ValueError(f"DeepgramClient is not available. DEEPGRAM_AVAILABLE={DEEPGRAM_AVAILABLE}, DeepgramClient={DeepgramClient}. Please install deepgram package: pip install deepgram-sdk")
            
            print(f"[WebCompanion] Initializing API clients...")
            print(f"[WebCompanion] DeepgramClient type: {type(DeepgramClient)}")
            print(f"[WebCompanion] DEEPGRAM_AVAILABLE: {DEEPGRAM_AVAILABLE}")
            
            try:
                # Deepgram SDK v5.x changed initialization - no positional args
                print(f"[WebCompanion] Attempting to initialize DeepgramClient with key length: {len(dg_key) if dg_key else 0}")
                
                # Pattern 1: v5.x - set env var and use no-arg constructor
                # This is the recommended pattern for v5.x
                original_env = os.environ.get("DEEPGRAM_API_KEY")
                os.environ["DEEPGRAM_API_KEY"] = dg_key
                try:
                    self.dg_client = DeepgramClient()
                    print(f"[WebCompanion] DeepgramClient initialized without args (v5.x pattern - using env var)")
                except Exception as e1:
                    print(f"[WebCompanion] Pattern 1 failed (no-arg constructor): {e1}")
                    # Pattern 2: Try api_key keyword argument
                    try:
                        self.dg_client = DeepgramClient(api_key=dg_key)
                        print(f"[WebCompanion] DeepgramClient initialized with api_key keyword (v5.x alternative)")
                    except TypeError as e2:
                        print(f"[WebCompanion] Pattern 2 failed (api_key=): {e2}")
                        # Pattern 3: Try with config dict
                        try:
                            self.dg_client = DeepgramClient(config={"api_key": dg_key})
                            print(f"[WebCompanion] DeepgramClient initialized with config dict")
                        except (TypeError, ValueError) as e3:
                            print(f"[WebCompanion] Pattern 3 failed (config dict): {e3}")
                            # Pattern 4: Try positional (older versions) - should not work in v5.x
                            try:
                                self.dg_client = DeepgramClient(dg_key)
                                print(f"[WebCompanion] DeepgramClient initialized with positional (v3.x pattern)")
                            except TypeError as e4:
                                print(f"[WebCompanion] All patterns failed. Last error: {e4}")
                                raise ValueError(f"Cannot initialize DeepgramClient with any known pattern. Errors: {e1}, {e2}, {e3}, {e4}")
                finally:
                    # Restore original env var if it existed (but keep it if we successfully used it)
                    if original_env is not None and hasattr(self, 'dg_client') and self.dg_client is None:
                        os.environ["DEEPGRAM_API_KEY"] = original_env
                    # If initialization succeeded, keep the env var set for the client
                
                print(f"[WebCompanion] DeepgramClient initialized successfully: {type(self.dg_client)}")
            except Exception as e:
                print(f"[WebCompanion] Error initializing DeepgramClient: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise ValueError(f"Failed to initialize DeepgramClient: {e}")
            
            try:
                self.openai_client = AsyncOpenAI(api_key=openai_key)
                print(f"[WebCompanion] OpenAI client initialized successfully")
            except Exception as e:
                print(f"[WebCompanion] Error initializing OpenAI client: {e}")
                raise ValueError(f"Failed to initialize OpenAI client: {e}")
            
            try:
                self.eleven_client = ElevenLabs(api_key=eleven_key)
                print(f"[WebCompanion] ElevenLabs client initialized successfully")
            except Exception as e:
                print(f"[WebCompanion] Error initializing ElevenLabs client: {e}")
                raise ValueError(f"Failed to initialize ElevenLabs client: {e}")
            
            self.http_client = httpx.AsyncClient(timeout=30.0)
            print(f"[WebCompanion] All API clients initialized successfully")
        except Exception as e:
            if COLORAMA_AVAILABLE:
                print(Fore.RED + f"Error initializing clients: {e}")
            else:
                print(f"Error initializing clients: {e}")
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
        # In Deepgram SDK v5.x, LiveOptions may not exist - use dict instead
        if LiveOptions is not None:
            # Use LiveOptions if available (older versions)
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
        else:
            # Use dict for v5.x (LiveOptions doesn't exist)
            options = {
                "model": DG_MODEL,
                "language": "en-US",
                "smart_format": True,
                "encoding": "linear16",
                "channels": 1,
                "sample_rate": 16000,
                "interim_results": True,
                "utterance_end_ms": int(DG_UTTERANCE_END_MS),
                "vad_events": True
            }
        
        self.dg_connection = self.dg_client.listen.live.v("1")
        
        # Event handlers
        def on_message(result, **kwargs):
            print(f"[WebCompanion] Deepgram on_message called with result: {result}, type: {type(result)}")
            try:
                # Handle different result structures (v3.x vs v5.x)
                if hasattr(result, 'channel') and result.channel:
                    sentence = result.channel.alternatives[0].transcript if result.channel.alternatives else ""
                    is_final = getattr(result, 'is_final', False)
                elif hasattr(result, 'alternatives') and result.alternatives:
                    sentence = result.alternatives[0].transcript if result.alternatives else ""
                    is_final = getattr(result, 'is_final', False)
                elif isinstance(result, dict):
                    sentence = result.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
                    is_final = result.get("is_final", False)
                else:
                    # Try to access attributes directly
                    sentence = getattr(result, 'transcript', '') or getattr(result, 'sentence', '')
                    is_final = getattr(result, 'is_final', False)
                    print(f"[WebCompanion] Using fallback extraction: sentence='{sentence}', is_final={is_final}")
                
                print(f"[WebCompanion] Extracted transcript: '{sentence}' (is_final={is_final})")
                
                if len(sentence) == 0:
                    print(f"[WebCompanion] Empty transcript, skipping")
                    return
            except Exception as e:
                print(f"[WebCompanion] Error extracting transcript from result: {e}")
                import traceback
                traceback.print_exc()
                return
            
            # Interruption detection
            if not is_final and len(sentence) > 5:
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
            
            if is_final:
                print(f"[WebCompanion] Final transcript received: '{sentence}' - queuing for processing")
                if COLORAMA_AVAILABLE:
                    print(Fore.CYAN + f"You: {sentence}")
                else:
                    print(f"You: {sentence}")
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
                        print(f"[WebCompanion] Queueing transcript in running event loop")
                        asyncio.run_coroutine_threadsafe(
                            self.transcript_queue.put(sentence),
                            loop
                        )
                    else:
                        print(f"[WebCompanion] Queueing transcript in new event loop")
                        loop.run_until_complete(self.transcript_queue.put(sentence))
                except RuntimeError as e:
                    print(f"[WebCompanion] RuntimeError queueing transcript: {e}")
                    # No event loop, create one
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    asyncio.run_coroutine_threadsafe(
                        self.transcript_queue.put(sentence),
                        loop
                    )
                print(f"[WebCompanion] Transcript queued successfully")
        
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
                    if COLORAMA_AVAILABLE:
                        if COLORAMA_AVAILABLE:
                            print(Fore.RED + "[Interrupted by user speech]")
                        else:
                            print("[Interrupted by user speech]")
                    else:
                        print("[Interrupted by user speech]")
        
        def on_error(error, **kwargs):
            if COLORAMA_AVAILABLE:
                if COLORAMA_AVAILABLE:
                    print(Fore.RED + f"Deepgram error: {error}")
                else:
                    print(f"Deepgram error: {error}")
            else:
                print(f"Deepgram error: {error}")
            asyncio.create_task(self.send_to_browser({
                "type": "error",
                "message": f"Deepgram error: {error}"
            }))
        
        # Register event handlers (per guidance: use VAD events for interruption)
        if LiveTranscriptionEvents:
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
            self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        else:
            # Fallback: use string event names
            self.dg_connection.on("transcript", on_message)
            self.dg_connection.on("speech_started", on_speech_started)
            self.dg_connection.on("error", on_error)
        
        if self.dg_connection.start(options) is False:
            raise Exception("Failed to start Deepgram connection")
        
        if COLORAMA_AVAILABLE:
            if COLORAMA_AVAILABLE:
                print(Fore.GREEN + "Deepgram connection established")
            else:
                print("Deepgram connection established")
        else:
            print("Deepgram connection established")
    
    async def send_to_browser(self, data: dict):
        """Send JSON data to browser via WebSocket."""
        if self.websocket:
            try:
                import json
                await self.websocket.send_json(data)
            except Exception as e:
                if COLORAMA_AVAILABLE:
                    print(Fore.RED + f"Error sending to browser: {e}")
                else:
                    print(f"Error sending to browser: {e}")
    
    def process_audio_chunk(self, audio_bytes: bytes):
        """Process audio chunk from browser and send to Deepgram (synchronous)."""
        print(f"[WebCompanion] Received audio chunk: {len(audio_bytes)} bytes")
        if self.dg_connection:
            try:
                print(f"[WebCompanion] Sending audio to Deepgram connection: {self.dg_connection}")
                self.dg_connection.send(audio_bytes)
                print(f"[WebCompanion] Audio chunk sent successfully to Deepgram")
            except Exception as e:
                print(f"[WebCompanion] Error sending audio to Deepgram: {e}")
                import traceback
                traceback.print_exc()
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
        else:
            print(f"[WebCompanion] WARNING: dg_connection is None! Cannot send audio.")
    
    async def start_processing_loop(self):
        """Start the main processing loop for transcripts."""
        print("[WebCompanion] Starting processing loop...")
        
        while True:
            try:
                # Wait for transcript
                print(f"[WebCompanion] Waiting for transcript from queue (queue size: {self.transcript_queue.qsize()})...")
                user_text = await self.transcript_queue.get()
                print(f"[WebCompanion] Received transcript from queue: '{user_text}' - starting generate_and_speak")
                
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
                if COLORAMA_AVAILABLE:
                    print(Fore.RED + f"Error in processing loop: {e}")
                else:
                    print(f"Error in processing loop: {e}")
    
    async def _ensure_browser_session(self) -> str:
        """Ensure browser session exists, create if needed."""
        if not self.browser_session_id:
            try:
                # Use internal call instead of HTTP request (same process)
                # This avoids network issues and is faster
                from browser.session import BrowserSession, active_browser_sessions
                import uuid
                
                session_id = str(uuid.uuid4())
                browser_session = BrowserSession(session_id)
                await browser_session.initialize()
                active_browser_sessions[session_id] = browser_session
                
                self.browser_session_id = session_id
                if COLORAMA_AVAILABLE:
                    print(Fore.GREEN + f"Created browser session: {self.browser_session_id}")
                else:
                    print(f"Created browser session: {self.browser_session_id}")
            except Exception as e:
                # Fallback to HTTP request if internal call fails
                try:
                    response = await self.http_client.post(
                        f"{self.rag_api_url}/browser/sessions",
                        params={"user_id": "companion"}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        self.browser_session_id = data.get("session_id")
                        if COLORAMA_AVAILABLE:
                            print(Fore.GREEN + f"Created browser session via HTTP: {self.browser_session_id}")
                        else:
                            print(f"Created browser session via HTTP: {self.browser_session_id}")
                    else:
                        if COLORAMA_AVAILABLE:
                            print(Fore.RED + f"Failed to create browser session: {response.status_code}")
                        else:
                            print(f"Failed to create browser session: {response.status_code}")
                except Exception as http_err:
                    if COLORAMA_AVAILABLE:
                        print(Fore.RED + f"Error creating browser session (both methods failed): {e}, {http_err}")
                    else:
                        print(f"Error creating browser session (both methods failed): {e}, {http_err}")
        return self.browser_session_id or ""
    
    async def _search_web(self, query: str) -> str:
        """Search the web using browser automation."""
        try:
            session_id = await self._ensure_browser_session()
            if not session_id:
                return "Unable to access web: browser session unavailable"
            
            # Use internal browser session directly (same process)
            from browser.session import active_browser_sessions
            from browser.actions import ActionExecutor
            from browser.ax_tree import extract_ax_tree
            
            if session_id not in active_browser_sessions:
                return "Browser session expired, please try again"
            
            browser_session = active_browser_sessions[session_id]
            
            # Navigate to search engine
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            nav_result = await browser_session.navigate(search_url)
            
            if not nav_result.get("success"):
                return f"Failed to navigate to search: {nav_result.get('error', 'Unknown error')}"
            
            # Wait for page load
            await asyncio.sleep(2)
            
            # Extract text from page
            try:
                ax_tree = await extract_ax_tree(browser_session.page)
                executor = ActionExecutor(browser_session.page)
                extract_result = await executor.extract_text(ax_tree, role="main")
                
                text = extract_result.get("text", "")[:2000]  # Limit to 2000 chars
                return f"Search results for '{query}': {text}"
            except Exception as extract_err:
                # Fallback: try to get page title at least
                try:
                    title = await browser_session.page.title()
                    return f"Found search results for '{query}' on {title}"
                except:
                    return f"Found search results for '{query}' but couldn't extract text: {str(extract_err)}"
                
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    async def _browse_web(self, url: str) -> str:
        """Browse a specific URL and extract content."""
        try:
            session_id = await self._ensure_browser_session()
            if not session_id:
                return "Unable to access web: browser session unavailable"
            
            # Use internal browser session directly (same process)
            from browser.session import active_browser_sessions
            from browser.actions import ActionExecutor
            from browser.ax_tree import extract_ax_tree
            
            if session_id not in active_browser_sessions:
                return "Browser session expired, please try again"
            
            browser_session = active_browser_sessions[session_id]
            
            # Navigate to URL
            nav_result = await browser_session.navigate(url)
            
            if not nav_result.get("success"):
                return f"Failed to navigate to {url}: {nav_result.get('error', 'Unknown error')}"
            
            # Wait for page load
            await asyncio.sleep(2)
            
            # Extract text
            try:
                ax_tree = await extract_ax_tree(browser_session.page)
                executor = ActionExecutor(browser_session.page)
                extract_result = await executor.extract_text(ax_tree, role="main")
                
                text = extract_result.get("text", "")[:2000]
                title = nav_result.get("title", url)
                return f"Content from {title}: {text}"
            except Exception as extract_err:
                # Fallback: use page title
                try:
                    title = await browser_session.page.title()
                    return f"Navigated to {title} but couldn't extract full content: {str(extract_err)}"
                except:
                    return f"Navigated to {url} but couldn't extract content: {str(extract_err)}"
                
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
        if COLORAMA_AVAILABLE:
            if COLORAMA_AVAILABLE:
                print(Fore.MAGENTA + "Thinking...", end="", flush=True)
            else:
                print("Thinking...", end="", flush=True)
        else:
            print("Thinking...", end="", flush=True)
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
                if COLORAMA_AVAILABLE:
                    if COLORAMA_AVAILABLE:
                        print(Fore.CYAN + "\n[Using web access...]")
                    else:
                        print("\n[Using web access...]")
                else:
                    print("\n[Using web access...]")
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
                if COLORAMA_AVAILABLE:
                    if COLORAMA_AVAILABLE:
                        print(Fore.MAGENTA + "Processing web results...", end="", flush=True)
                    else:
                        print("Processing web results...", end="", flush=True)
                else:
                    print("Processing web results...", end="", flush=True)
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
                        # Don't print streaming text (too verbose)
                        # print(delta_text, end="", flush=True)
                        
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
            if COLORAMA_AVAILABLE:
                if COLORAMA_AVAILABLE:
                    print(Fore.BLUE + f"\n[TTFT: {ttft:.0f}ms]")
                else:
                    print(f"\n[TTFT: {ttft:.0f}ms]")
            else:
                print(f"\n[TTFT: {ttft:.0f}ms]")
            
            await self.send_to_browser({
                "type": "response_start",
                "ttft_ms": ttft
            })
            
            # Stream audio chunks to browser (if we have audio)
            if audio_stream:
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
            if COLORAMA_AVAILABLE:
                if COLORAMA_AVAILABLE:
                    print(Fore.GREEN + f"[Total: {total_time:.0f}ms]\n")
                else:
                    print(f"[Total: {total_time:.0f}ms]\n")
            else:
                print(f"[Total: {total_time:.0f}ms]\n")
            
            await self.send_to_browser({
                "type": "response_complete",
                "total_ms": total_time
            })
        
        except Exception as e:
            if COLORAMA_AVAILABLE:
                print(Fore.RED + f"\nError in generate_and_speak: {e}")
            else:
                print(f"\nError in generate_and_speak: {e}")
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

