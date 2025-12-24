from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Request
from contextlib import asynccontextmanager
import asyncio
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from openai import OpenAI
import chromadb
import os
import numpy as np
import io
import tempfile
from docx import Document
import PyPDF2
import json
import base64
import uuid
from datetime import datetime
from uncertainty import UncertaintyChecker
from budget import ContextBudgetEnforcer
from cost import CostTracker
from memory import MemoryStorage
from models import MemoryItem, MemoryCreateRequest, MemoryUpdateRequest, MemorySearchRequest, MemoryListRequest, LiveSession, LiveSessionCreateRequest
from live_sessions import ScreenShareSession, active_live_sessions
from browser.session import BrowserSession, active_browser_sessions
from browser.ax_tree import extract_ax_tree, filter_ax_tree, find_element_by_ax
from browser.safety import browser_safety
from browser.actions import ActionExecutor
from browser.agent_loop import BrowserAutomation
from export import export_conversation_to_pdf, export_query_results_to_pdf

# Optional imports - wrap in try/except to prevent crashes
try:
    from windows.device import device_pairing
    from windows.credentials import credential_manager
    from windows.security import trust_boundaries
    from windows.apps import app_manager
    from windows.files import file_manager
    from windows.vision import screen_vision
    from windows.roc import roc
    from windows.panic import panic_stop
    from windows.indicator import automation_indicator
    WINDOWS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Windows modules not available: {e}")
    device_pairing = None
    credential_manager = None
    trust_boundaries = None
    app_manager = None
    file_manager = None
    screen_vision = None
    roc = None
    panic_stop = None
    automation_indicator = None
    WINDOWS_AVAILABLE = False

try:
    from agents.crew import get_crewai_manager
    from agents.autonomy import agent_autonomy_manager
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agents modules not available: {e}")
    get_crewai_manager = None
    agent_autonomy_manager = None
    AGENTS_AVAILABLE = False

try:
    from memory.relationships import get_relationship_manager
    from memory.expiration import get_expiration_manager
    from memory.analytics import get_memory_analytics
    from memory.clustering import memory_clustering
    from memory.conflicts import memory_conflict_detector
    from memory.templates import memory_template_manager
    MEMORY_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Memory modules not available: {e}")
    get_relationship_manager = None
    get_expiration_manager = None
    get_memory_analytics = None
    memory_clustering = None
    memory_conflict_detector = None
    memory_template_manager = None
    MEMORY_MODULES_AVAILABLE = False

try:
    from avatar.waveform import get_waveform_generator
    from avatar.lipsync import get_lipsync_processor
    AVATAR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Avatar modules not available: {e}")
    get_waveform_generator = None
    get_lipsync_processor = None
    AVATAR_AVAILABLE = False

try:
    from media.image_generation import image_generator
    from media.video_generation import video_generator
    from media.charts import chart_generator
    from media.storage import media_storage
    MEDIA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Media modules not available: {e}")
    image_generator = None
    video_generator = None
    chart_generator = None
    media_storage = None
    MEDIA_AVAILABLE = False

try:
    from integrations.spotify import get_spotify_client
    SPOTIFY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Spotify integration not available: {e}")
    get_spotify_client = None
    SPOTIFY_AVAILABLE = False

try:
    from documents.processing import document_processor
    DOCUMENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Documents processing not available: {e}")
    document_processor = None
    DOCUMENTS_AVAILABLE = False

try:
    from analytics.dashboards import analytics_dashboard
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Analytics not available: {e}")
    analytics_dashboard = None
    ANALYTICS_AVAILABLE = False

try:
    from collaboration.sessions import collaboration_manager
    from collaboration.editing import get_editor
    COLLABORATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Collaboration modules not available: {e}")
    collaboration_manager = None
    get_editor = None
    COLLABORATION_AVAILABLE = False
from models import (
    ImageGenerationRequest, ImageEditRequest, ImageVariationsRequest, ImageAnalysisRequest,
    VideoGenerationRequest, ChartGenerationRequest, SpotifyPlaylistCreateRequest, SmartPlaylistRequest,
    ProjectShareRequest, UserRegisterRequest, UserLoginRequest
)

# Auth import - wrap in try/except to prevent crashes
try:
    from auth.users import user_manager
    AUTH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Auth module not available: {e}")
    # Create a dummy user_manager to prevent crashes
    class DummyUserManager:
        def create_user(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Authentication not available")
        def authenticate_user(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Authentication not available")
    user_manager = DummyUserManager()
    AUTH_AVAILABLE = False
except Exception as e:
    print(f"Warning: Error loading auth module: {e}")
    import traceback
    traceback.print_exc()
    class DummyUserManager:
        def create_user(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Authentication not available")
        def authenticate_user(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Authentication not available")
    user_manager = DummyUserManager()
    AUTH_AVAILABLE = False

# Using ChromaDB's built-in OpenAI embedding function and OpenAI for answer generation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Authentication removed - all endpoints are public
    print("[Startup] Authentication disabled - all endpoints are public")
    
    yield  # App is running
    
    # Shutdown (if needed)
    pass

app = FastAPI(
    title="RAG Knowledge Base API - ChromaDB + OpenAI Edition",
    lifespan=lifespan
)

# Add CORS middleware for WebRTC
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Companion-API integration
COMPANION_API_URL = os.getenv("COMPANION_API_URL", "http://localhost:8081")

# Import companion functionality
try:
    from companion_web import WebCompanion
    COMPANION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Companion functionality not available: {e}")
    COMPANION_AVAILABLE = False
    WebCompanion = None

# Companion sessions (in-memory for MVP)
active_companion_sessions: Dict[str, any] = {}
companion_session_websockets: Dict[str, WebSocket] = {}

# Cost tracking middleware
@app.middleware("http")
async def cost_tracking_middleware(request: Request, call_next):
    """
    Track costs for all requests and enforce daily budget limits
    
    - Extracts user_id from request headers (default: "default")
    - Estimates tokens from response size after processing
    - Updates budget after processing
    - Adds cost headers to response
    
    Note: Budget checking is done in endpoints where we have actual token estimates.
    This middleware handles post-request cost tracking and header addition.
    """
    # Extract user_id from request headers (future: from auth token)
    user_id = request.headers.get("X-User-ID", "default")
    
    # Skip cost tracking for health check and static endpoints
    if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # Process request first
    response = await call_next(request)
    
    # Estimate tokens from response (rough estimate)
    # Future: Extract actual token usage from OpenAI API response
    estimated_tokens = 1000  # Default estimate
    try:
        # Try to get response body if available
        if hasattr(response, 'body') and response.body:
            response_text = response.body.decode('utf-8', errors='ignore') if isinstance(response.body, bytes) else str(response.body)
            # Rough estimate: 1 token ≈ 4 characters
            estimated_tokens = len(response_text) // 4
    except:
        pass
    
    # Estimate cost
    estimated_cost = cost_tracker.estimate_cost(estimated_tokens)
    
    # Check budget status (for warning headers, not rejection - rejection happens in endpoints)
    budget_status = cost_tracker.get_budget_status(user_id)
    if budget_status:
        budget_check = cost_tracker.check_daily_budget(user_id, estimated_tokens, estimated_cost)
        
        # Only update if within budget (rejection handled in endpoints)
        if budget_check["within_budget"]:
            cost_tracker.update_budget(user_id, estimated_tokens, estimated_cost)
            
            # Add cost headers
            response.headers["X-Cost-Tokens"] = str(estimated_tokens)
            response.headers["X-Cost-Dollars"] = f"{estimated_cost:.4f}"
            
            if budget_check.get("warning"):
                response.headers["X-Budget-Warning"] = "true"
                response.headers["X-Budget-Utilization"] = f"{budget_check['utilization']:.2f}"
                response.headers["X-Budget-Tokens-Used"] = str(budget_check["tokens_used"])
                response.headers["X-Budget-Tokens-Limit"] = str(budget_check["tokens_limit"])
                response.headers["X-Budget-Dollars-Used"] = f"{budget_check['dollars_used']:.2f}"
                response.headers["X-Budget-Dollars-Limit"] = f"{budget_check['dollars_limit']:.2f}"
        else:
            # Budget exceeded - add headers but don't update (endpoint should have rejected)
            response.headers["X-Cost-Tokens"] = str(estimated_tokens)
            response.headers["X-Cost-Dollars"] = f"{estimated_cost:.4f}"
            response.headers["X-Budget-Exceeded"] = "true"
    else:
        # First request for user - initialize and update
        cost_tracker.update_budget(user_id, estimated_tokens, estimated_cost)
        response.headers["X-Cost-Tokens"] = str(estimated_tokens)
        response.headers["X-Cost-Dollars"] = f"{estimated_cost:.4f}"
    
    return response

# Authentication removed - all endpoints are public

# Initialize clients
chromadb_path = os.getenv("CHROMADB_PATH", "./rag_knowledge_base")
collection_name = "documents"

# Initialize uncertainty checker (with error handling)
try:
    uncertainty_checker = UncertaintyChecker(threshold=0.6)
except Exception as e:
    print(f"Warning: Failed to initialize uncertainty checker: {e}")
    class DummyUncertaintyChecker:
        def check(self, *args, **kwargs):
            return {"uncertain": False, "confidence": 1.0}
    uncertainty_checker = DummyUncertaintyChecker()

# Initialize context budget enforcer (with error handling)
try:
    budget_enforcer = ContextBudgetEnforcer(max_tokens=100000, warn_threshold=0.8)
except Exception as e:
    print(f"Warning: Failed to initialize budget enforcer: {e}")
    class DummyBudgetEnforcer:
        def check_budget(self, *args, **kwargs):
            return {"over_budget": False, "warnings": []}
        def truncate_history(self, *args, **kwargs):
            return args[0] if args else []
    budget_enforcer = DummyBudgetEnforcer()

# Initialize cost tracker (with error handling)
try:
    cost_tracker = CostTracker()
except Exception as e:
    print(f"Warning: Failed to initialize cost tracker: {e}")
    class DummyCostTracker:
        def estimate_cost(self, *args, **kwargs):
            return 0.0
        def get_budget_status(self, *args, **kwargs):
            return None
    cost_tracker = DummyCostTracker()

# Initialize memory storage (with error handling)
try:
    memory_storage = MemoryStorage(chromadb_path=chromadb_path)
    print("[Startup] Memory storage initialized successfully")
except Exception as e:
    print(f"Warning: Failed to initialize memory storage: {e}")
    import traceback
    traceback.print_exc()
    # Create a dummy storage that won't crash
    class DummyMemoryStorage:
        def search(self, *args, **kwargs):
            return []
        def create(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Memory storage not available")
        def list(self, *args, **kwargs):
            return []
        def get(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Memory storage not available")
        def update(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Memory storage not available")
        def delete(self, *args, **kwargs):
            raise HTTPException(status_code=503, detail="Memory storage not available")
    memory_storage = DummyMemoryStorage()

# Initialize OpenAI client (lazy initialization) - used for answer generation and vision
openai_client = None

def get_openai_client():
    """Get or create OpenAI client (lazy initialization) - used for answer generation and vision"""
    global openai_client
    if openai_client is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise Exception("OPENAI_API_KEY environment variable not set")
        openai_client = OpenAI(api_key=openai_api_key)
    return openai_client

# Initialize ChromaDB client and collection lazily
chroma_client = None
chroma_collection = None

def get_chromadb_collection():
    """Get or create ChromaDB collection (lazy initialization)"""
    global chroma_client, chroma_collection
    if chroma_collection is None:
        try:
            # Create persistent client
            print(f"[ChromaDB] Initializing ChromaDB at path: {chromadb_path}")
            chroma_client = chromadb.PersistentClient(path=chromadb_path)
            
            # Create embedding function using OpenAI
            # We can use ChromaDB's built-in OpenAI function or our custom one
            from chromadb.utils import embedding_functions
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise Exception("OPENAI_API_KEY environment variable is required for embeddings")
            # Use ChromaDB's built-in OpenAI embedding function (simpler and well-tested)
            embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai_api_key,
                model_name="text-embedding-3-small"
            )
            
            # Get or create collection
            chroma_collection = chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_fn
            )
            print(f"[ChromaDB] Successfully initialized collection: {collection_name}")
        except Exception as e:
            print(f"[ChromaDB] ERROR: Failed to initialize ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            raise
    return chroma_collection

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    use_hybrid_search: bool = True
    document_filter: Optional[str] = None  # Optional document name filter
    user_id: str = "default"  # User identifier for memory retrieval
    project_id: Optional[str] = None  # Project identifier for memory filtering
    private_session: bool = False  # If True, don't retrieve or write memories

class QueryResponse(BaseModel):
    answer: str
    sources: list
    uncertain: bool = False
    reason: Optional[str] = None
    suggestions: Optional[List[str]] = None
    memories_used: Optional[List[Dict]] = None  # List of memories used in answer

def embed_text(text: str) -> list:
    """Generate embedding for text using OpenAI (for query embeddings)"""
    from openai import OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def keyword_score(query_text: str, document_text: str) -> float:
    """Calculate keyword matching score (simple BM25-like scoring)"""
    query_words = set(query_text.lower().split())
    doc_words = document_text.lower().split()
    doc_word_set = set(doc_words)
    
    # Count matches
    matches = len(query_words.intersection(doc_word_set))
    if matches == 0:
        return 0.0
    
    # Simple TF-IDF-like score (normalized by query length)
    score = matches / len(query_words)
    return min(score, 1.0)

def search_chromadb(
    query_text: str = "", 
    top_k: int = 3, 
    use_hybrid: bool = True, 
    document_filter: Optional[str] = None,
    project_id: Optional[str] = None
):
    """Search ChromaDB for similar documents with optional hybrid search and metadata filtering
    
    Optimized to:
    - Use ChromaDB's native vector search
    - Calculate keyword scores in-memory for hybrid search
    - Support metadata filtering
    - Implement hybrid search with reranking
    """
    try:
        collection = get_chromadb_collection()
        
        # Validate query text
        if not query_text or not query_text.strip():
            print(f"[RAG] Warning: Empty query text, returning empty results")
            return []
        
        # Retrieve more candidates for reranking
        retrieve_count = min(top_k * 10, 100)
        
        # Build where clause for document filter and project_id
        where_clause = None
        if document_filter or project_id:
            where_clause = {}
            if document_filter:
                where_clause["document_name"] = document_filter
            if project_id:
                where_clause["project_id"] = project_id
        
        # Query ChromaDB - it will use the embedding function automatically
        # But we need to pass the query text, not the embedding
        # ChromaDB will generate the embedding using OpenAI embedding function
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=retrieve_count,
                where=where_clause
            )
        except Exception as e:
            print(f"[RAG] Error querying ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return []  # Return empty results instead of crashing
        
        # Process results
        scored_results = []
        
        # Safely extract results with None checks
        if not results:
            print(f"[RAG] Warning: ChromaDB returned None or empty results")
            return []
        
        documents = results.get('documents', [])
        if not documents or len(documents) == 0:
            print(f"[RAG] No documents found in ChromaDB for query: {query_text[:50]}...")
            return []
        
        # Safely extract nested arrays
        documents = documents[0] if documents and len(documents) > 0 else []
        metadatas = results.get('metadatas', [[]])[0] if results.get('metadatas') and len(results.get('metadatas', [])) > 0 else [{}] * len(documents)
        ids = results.get('ids', [[]])[0] if results.get('ids') and len(results.get('ids', [])) > 0 else []
        distances = results.get('distances', [[]])[0] if results.get('distances') and len(results.get('distances', [])) > 0 else []
        
        # Ensure all arrays have the same length
        min_length = min(len(documents), len(metadatas), len(ids), len(distances))
        if min_length == 0:
            print(f"[RAG] Warning: All result arrays are empty")
            return []
        
        documents = documents[:min_length]
        metadatas = metadatas[:min_length] if isinstance(metadatas, list) else [{}] * min_length
        ids = ids[:min_length]
        distances = distances[:min_length]
        
        for i, (doc_text, metadata, doc_id, distance) in enumerate(zip(documents, metadatas, ids, distances)):
            try:
                # Validate data types
                if not isinstance(doc_text, str):
                    doc_text = str(doc_text) if doc_text else ""
                if not isinstance(metadata, dict):
                    metadata = {} if metadata is None else {}
                if not isinstance(doc_id, (str, int)):
                    doc_id = str(doc_id) if doc_id else f"unknown_{i}"
                
                # Convert distance to similarity (ChromaDB returns distance, lower is better)
                # Distance is typically cosine distance, so similarity = 1 - distance
                try:
                    distance_float = float(distance) if distance is not None else 1.0
                except (ValueError, TypeError):
                    distance_float = 1.0
                
                vector_score = 1.0 - distance_float if distance_float <= 1.0 else 0.0
                
                # Hybrid search: combine vector and keyword scores
                if use_hybrid and query_text:
                    keyword_score_val = keyword_score(query_text, doc_text)
                    # Weighted combination: 70% vector, 30% keyword
                    combined_score = 0.7 * vector_score + 0.3 * keyword_score_val
                else:
                    combined_score = vector_score
                
                scored_results.append({
                    'id': str(doc_id),
                    'document_name': metadata.get('document_name', 'unknown') if isinstance(metadata, dict) else 'unknown',
                    'text': doc_text,
                    'chunk_index': metadata.get('chunk_index', 0) if isinstance(metadata, dict) else 0,
                    'score': float(combined_score),
                    'vector_score': float(vector_score),
                    'keyword_score': float(keyword_score(query_text, doc_text)) if query_text else 0.0
                })
            except Exception as e:
                print(f"[RAG] Error processing result {i}: {e}")
                continue  # Skip this result instead of crashing
        
        # Sort by combined score
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Simple reranking: boost scores for documents with high keyword match
        if use_hybrid and query_text:
            for result in scored_results:
                # Boost if keyword score is high (indicates exact term match)
                if result.get('keyword_score', 0) > 0.5:
                    result['score'] = min(result['score'] * 1.2, 1.0)
        
        # Re-sort after reranking
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top_k after reranking
        return scored_results[:top_k]
    
    except Exception as e:
        print(f"[RAG] CRITICAL ERROR in search_chromadb: {e}")
        import traceback
        traceback.print_exc()
        return []  # Return empty results instead of crashing

def generate_answer(
    question: str, 
    context_docs: list, 
    conversation_history: Optional[List[Dict]] = None,
    memories: Optional[List[MemoryItem]] = None
) -> tuple[str, Dict, int]:
    """
    Generate answer using OpenAI GPT-4o with context budget enforcement
    
    Args:
        question: User's question
        context_docs: List of retrieved document chunks
        conversation_history: Optional list of previous messages (for context budget)
        
    Returns:
        Tuple of (answer string, budget_check dict)
    """
    client = get_openai_client()
    
    # Build context from retrieved documents
    context = "\n\n".join([
        f"Source: {doc['document_name']} (chunk {doc['chunk_index']})\n{doc['text']}"
        for doc in context_docs
    ])
    
    # Build memory context if memories are provided
    memory_context = ""
    if memories:
        memory_context = "\n\nRelevant Memories:\n" + "\n\n".join([
            f"- {mem.content} (type: {mem.memory_type})"
            for mem in memories
        ])
    
    system_prompt = "You are a helpful assistant that answers questions based on the provided context and relevant memories. If the answer is not in the context, say so explicitly."
    user_prompt = f"""Based on the following context{(' and memories' if memories else '')}, answer the question.

Context:
{context}{memory_context}

Question: {question}

Answer:"""
    
    # Estimate tokens for budget check
    system_tokens = budget_enforcer.estimate_tokens(system_prompt)
    user_tokens = budget_enforcer.estimate_tokens(user_prompt)
    rag_tokens = budget_enforcer.estimate_tokens(context)
    memory_tokens = budget_enforcer.estimate_tokens(memory_context) if memory_context else 0
    
    # Estimate history tokens
    history_tokens = 0
    if conversation_history:
        history_tokens = sum([
            budget_enforcer.estimate_tokens(msg.get('content', '')) 
            for msg in conversation_history
        ])
    
    # Check budget
    budget_check = budget_enforcer.check_budget(
        system_tokens=system_tokens,
        history_tokens=history_tokens,
        rag_tokens=rag_tokens,
        memory_tokens=memory_tokens
    )
    
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history if provided (truncated if needed)
    if conversation_history:
        if budget_check.get("over_budget"):
            # Truncate history to fit budget
            max_history_tokens = 50000  # Reserve space for system + RAG + user prompt
            truncated_history = budget_enforcer.truncate_history(conversation_history, max_history_tokens)
            messages.extend(truncated_history)
        else:
            messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_prompt})
    
    # Generate answer with timeout
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # GPT-4o supports text, vision, and audio
            messages=messages,
            temperature=0.7,
            timeout=30.0  # 30 second timeout for API call
        )
    except Exception as e:
        error_str = str(e)
        # Check for quota errors and provide helpful message
        if "quota" in error_str.lower() or "insufficient_quota" in error_str.lower():
            raise Exception(f"OpenAI API quota exceeded. Please check your billing and plan details. Original error: {error_str}")
        raise Exception(f"OpenAI API call failed: {error_str}")
    
    answer = response.choices[0].message.content
    
    # Extract actual token usage from OpenAI response (if available)
    actual_tokens_used = 0
    if hasattr(response, 'usage') and response.usage:
        # Total tokens = input + output
        actual_tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
    
    # Update budget_check with actual tokens if available
    if actual_tokens_used > 0:
        budget_check["actual_tokens_used"] = actual_tokens_used
    
    return answer, budget_check, actual_tokens_used

# ==================== Document Upload Functions ====================

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    doc = Document(io.BytesIO(file_content))
    return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_parts = []
    for page in pdf_reader.pages:
        text_parts.append(page.extract_text())
    return '\n'.join(text_parts)

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    return file_content.decode('utf-8')

def extract_text_from_markdown(file_content: bytes) -> str:
    """Extract text from Markdown file"""
    return file_content.decode('utf-8')

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from file based on extension"""
    ext = filename.lower().split('.')[-1] if filename else 'txt'
    
    if ext == 'docx':
        return extract_text_from_docx(file_content)
    elif ext == 'pdf':
        return extract_text_from_pdf(file_content)
    elif ext == 'txt':
        return extract_text_from_txt(file_content)
    elif ext in ['md', 'markdown']:
        return extract_text_from_markdown(file_content)
    else:
        # Try as plain text
        try:
            return extract_text_from_txt(file_content)
        except (UnicodeDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Error: {str(e)}")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def embed_text_for_document(text: str) -> list:
    """Generate embedding for document text using OpenAI (deprecated - ChromaDB handles this automatically)"""
    # This function is kept for compatibility but not used since ChromaDB generates embeddings automatically
    from openai import OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def ensure_collection_exists():
    """Ensure ChromaDB collection exists (created automatically on first access)"""
    return get_chromadb_collection()

@app.get("/")
def root():
    return {
        "message": "RAG Knowledge Base API - ChromaDB + OpenAI Edition",
        "endpoints": {
            "/query": "POST - Query the knowledge base",
            "/health": "GET - Health check",
            "/companion-api/health": "GET - Companion-API health check",
            "/companion/session/create": "POST - Create companion session",
            "/companion/ws/{session_id}": "WebSocket - Companion real-time interaction",
            "/upload": "POST - Upload and ingest documents",
            "/documents": "GET - List all documents",
            "/multimodal-live/create-session": "POST - Create multimodal live session",
            "/multimodal-live/ws/{session_id}": "WebSocket - Real-time multimodal communication (text, vision, audio)",
            "/multimodal-live/sessions/{session_id}": "GET/DELETE - Manage multimodal live sessions",
            "/companion-api/health": "GET - Companion-API health check",
            "/live-sessions": "POST - Create live session (LS3 screen share)",
            "/live-sessions/ws/{session_id}": "WebSocket - Screen share session",
            "/live-sessions/{session_id}": "GET/PUT/DELETE - Manage live sessions",
            "/browser/sessions": "POST - Create browser session",
            "/browser/sessions/{session_id}/ax-tree": "GET - Get accessibility tree",
            "/browser/sessions/{session_id}/navigate": "POST - Navigate browser",
            "/browser/sessions/{session_id}/screenshot": "GET - Get screenshot",
            "/browser/sessions/{session_id}/actions/*": "POST - Browser actions (click, type, extract, plan-execute)",
            "/export/conversation": "POST - Export conversation to PDF",
            "/export/query-results": "POST - Export query results to PDF"
        }
    }

@app.get("/health")
def health():
    try:
        # Test ChromaDB connection
        collection = get_chromadb_collection()
        count = collection.count()
        
        return {
            "status": "healthy",
            "chromadb_connection": "ok",
            "document_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companion-api/health")
async def companion_api_health():
    """Check companion-api service health"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{COMPANION_API_URL}/health")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "companion_api": "connected",
                    "companion_api_url": COMPANION_API_URL,
                    "companion_api_status": response.json()
                }
            else:
                return {
                    "status": "degraded",
                    "companion_api": "unreachable",
                    "companion_api_url": COMPANION_API_URL,
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "degraded",
            "companion_api": "unreachable",
            "companion_api_url": COMPANION_API_URL,
            "error": str(e)
        }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, http_request: Request):
    try:
        # Validate request
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # 1. Retrieve relevant memories (if not private session)
        relevant_memories = []
        try:
            if not request.private_session:
                relevant_memories = memory_storage.search(
                    user_id=request.user_id,
                    query=request.question,
                    project_id=request.project_id,
                    top_k=3
                )
        except Exception as e:
            print(f"[RAG] Warning: Error retrieving memories: {e}")
            relevant_memories = []  # Continue without memories
        
        # 2. Search ChromaDB for similar documents (with hybrid search and optional filtering)
        # Note: ChromaDB generates embeddings automatically using OpenAI embedding function
        try:
            similar_docs = search_chromadb(
                request.question, 
                request.top_k, 
                use_hybrid=request.use_hybrid_search,
                document_filter=request.document_filter,
                project_id=request.project_id
            )
        except Exception as e:
            print(f"[RAG] Error in search_chromadb: {e}")
            import traceback
            traceback.print_exc()
            similar_docs = []  # Continue with empty results
        
        # 3. Check uncertainty BEFORE generating answer (prevents hallucination)
        try:
            uncertainty_result = uncertainty_checker.check_retrieval(similar_docs)
        except Exception as e:
            print(f"[RAG] Error in uncertainty check: {e}")
            uncertainty_result = {"uncertain": True, "reason": "Error checking uncertainty"}
        
        if uncertainty_result.get("uncertain", False):
            # Return structured uncertain response instead of generating answer
            try:
                uncertain_response = uncertainty_checker.generate_uncertain_response(
                    request.question,
                    uncertainty_result.get("reason", "No relevant documents found")
                )
                return QueryResponse(**uncertain_response)
            except Exception as e:
                print(f"[RAG] Error generating uncertain response: {e}")
                return QueryResponse(
                    answer="I'm sorry, I couldn't find relevant information to answer your question. Please try rephrasing it or uploading relevant documents.",
                    sources=[],
                    uncertain=True,
                    reason="Error processing uncertainty response"
                )
        
        # 4. Generate answer using OpenAI GPT-4o (only if NOT uncertain)
        # Note: conversation_history is None for now (will be added later)
        try:
            answer, budget_check, actual_tokens_used = generate_answer(
                request.question, 
                similar_docs, 
                conversation_history=None,
                memories=relevant_memories
            )
        except Exception as e:
            print(f"[RAG] Error generating answer: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating answer: {str(e)}"
            )
        
        # Track actual cost if we have token usage
        user_id = "default"
        if http_request:
            user_id = http_request.headers.get("X-User-ID", "default")
        if actual_tokens_used > 0:
            try:
                actual_cost = cost_tracker.estimate_cost(actual_tokens_used)
                # Check budget with actual tokens
                budget_check_cost = cost_tracker.check_daily_budget(user_id, actual_tokens_used, actual_cost)
                if not budget_check_cost.get("within_budget", True):
                    # Budget exceeded - return error
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Daily budget limit reached",
                            "tokens_used": budget_check_cost.get("tokens_used", 0),
                            "tokens_limit": budget_check_cost.get("tokens_limit", 0),
                            "dollars_used": budget_check_cost.get("dollars_used", 0),
                            "dollars_limit": budget_check_cost.get("dollars_limit", 0)
                        }
                    )
                # Update budget with actual tokens
                cost_tracker.update_budget(user_id, actual_tokens_used, actual_cost)
            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except Exception as e:
                print(f"[RAG] Warning: Error tracking cost: {e}")
                # Continue without cost tracking
        
        # 4. Format sources
        sources = []
        try:
            sources = [
                {
                    "document": doc.get('document_name', 'unknown'),
                    "chunk": doc.get('chunk_index', 0),
                    "score": doc.get('score', 0.0),
                    "text": (doc.get('text', '')[:200] + "...") if len(doc.get('text', '')) > 200 else doc.get('text', '')
                }
                for doc in similar_docs
            ]
        except Exception as e:
            print(f"[RAG] Warning: Error formatting sources: {e}")
            sources = []
        
        # 5. Build response with budget info and memory citations
        try:
            response_data = {
                "answer": answer,
                "sources": sources,
                "uncertain": False,
                "memories_used": [
                    {"id": m.id, "content": m.content, "type": m.memory_type}
                    for m in relevant_memories
                ] if relevant_memories else None
            }
        except Exception as e:
            print(f"[RAG] Warning: Error building response data: {e}")
            response_data = {
                "answer": answer,
                "sources": sources,
                "uncertain": False,
                "memories_used": None
            }
        
        # Add budget warning if applicable
        if budget_check.get("warning"):
            # Budget info will be included in response headers (via cost tracking middleware)
            pass
        
        return QueryResponse(**response_data)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"[RAG] CRITICAL ERROR in /query endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_name: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None)
):
    """
    Upload and process a document (PDF, DOCX, TXT, MD)
    The file will be chunked, embedded, and stored in ChromaDB
    """
    try:
        # Ensure dependencies are initialized
        try:
            collection = ensure_collection_exists()
        except Exception:
            raise HTTPException(status_code=500, detail="ChromaDB client not initialized")

        # OpenAI client will be initialized lazily when needed
        try:
            get_openai_client()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI client initialization failed: {str(e)}")
        
        # Use provided name or filename
        doc_name = document_name or file.filename or "uploaded_document"
        
        # Read file content
        file_content = await file.read()
        
        # Extract text
        text = extract_text_from_file(file_content, file.filename or "document.txt")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Chunk text
        chunks = chunk_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid chunks created from document")
        
        # Process chunks for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Generate unique ID for each chunk
            chunk_id = str(uuid.uuid4())
            
            documents.append(chunk)
            metadata = {
                "document_name": doc_name,
                "chunk_index": i
            }
            if project_id:
                metadata["project_id"] = project_id
            metadatas.append(metadata)
            ids.append(chunk_id)
        
        # Insert into ChromaDB (embeddings generated automatically by embedding function)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return JSONResponse({
            "status": "success",
            "message": f"Document '{doc_name}' uploaded successfully",
            "document_name": doc_name,
            "chunks_created": len(chunks),
            "total_chars": len(text)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        try:
            collection = get_chromadb_collection()
        except Exception:
            raise HTTPException(status_code=500, detail="ChromaDB client not initialized")
        
        # Get all documents from ChromaDB
        all_data = collection.get()
        
        # Count chunks per document
        doc_counts = {}
        if all_data['metadatas']:
            for metadata in all_data['metadatas']:
                doc_name = metadata.get('document_name', 'unknown')
                doc_counts[doc_name] = doc_counts.get(doc_name, 0) + 1
        
        documents = [
            {
                "document_name": doc_name,
                "chunk_count": count
            }
            for doc_name, count in sorted(doc_counts.items())
        ]
        
        return {
            "documents": documents,
            "total_documents": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

# Memory API Endpoints

@app.post("/memory")
async def create_memory(memory_request: MemoryCreateRequest):
    """Create a new memory"""
    try:
        memory = MemoryItem.create(
            user_id=memory_request.user_id,
            content=memory_request.content,
            memory_type=memory_request.memory_type,
            project_id=memory_request.project_id
        )
        stored_memory = memory_storage.create(memory)
        return stored_memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating memory: {str(e)}")

@app.get("/memory")
async def list_memories(user_id: str, project_id: Optional[str] = None):
    """List all memories for user (optionally filtered by project)"""
    try:
        memories = memory_storage.list(user_id, project_id)
        return {
            "memories": memories,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing memories: {str(e)}")

@app.get("/memory/{memory_id}")
async def get_memory(memory_id: str, user_id: str):
    """Get memory by ID"""
    try:
        memory = memory_storage.get(memory_id, user_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memory: {str(e)}")

@app.put("/memory/{memory_id}")
async def update_memory(memory_id: str, user_id: str, update_request: MemoryUpdateRequest):
    """Update memory by ID"""
    try:
        memory = memory_storage.get(memory_id, user_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Update memory
        if update_request.content is not None:
            memory.content = update_request.content
        if update_request.memory_type is not None:
            memory.memory_type = update_request.memory_type
        memory.updated_at = datetime.now()
        
        updated_memory = memory_storage.update(memory)
        if not updated_memory:
            raise HTTPException(status_code=500, detail="Error updating memory")
        return updated_memory
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating memory: {str(e)}")

@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, user_id: str):
    """Delete memory by ID"""
    try:
        deleted = memory_storage.delete(memory_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory: {str(e)}")

@app.post("/memory/search")
async def search_memories(search_request: MemorySearchRequest):
    """Search memories by relevance"""
    try:
        memories = memory_storage.search(
            user_id=search_request.user_id,
            query=search_request.query,
            project_id=search_request.project_id,
            top_k=search_request.top_k
        )
        return {
            "memories": memories,
            "query": search_request.query,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")

# Multimodal Live API Integration (using OpenAI)
class MultimodalLiveSession(BaseModel):
    session_id: str
    model: str = "gpt-4o"
    system_instruction: Optional[str] = None

# Store active multimodal live sessions
active_sessions = {}

@app.post("/multimodal-live/create-session")
async def create_multimodal_live_session(config: Optional[dict] = None):
    """Create a new multimodal live session and return session token"""
    try:
        import time
        session_id = str(uuid.uuid4())
        
        # Configure multimodal session
        model_config = {
            "model": config.get("model", "gpt-4o") if config else "gpt-4o",
            "system_instruction": config.get("system_instruction", "You are JARVIS, an AI assistant powered by RAG system. Provide helpful, accurate responses based on the knowledge base.") if config else "You are JARVIS, an AI assistant powered by RAG system. Provide helpful, accurate responses based on the knowledge base."
        }
        
        # Store session configuration
        active_sessions[session_id] = {
            "config": model_config,
            "created_at": time.time()
        }
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Multimodal live session created. Use WebSocket endpoint for real-time communication."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.websocket("/multimodal-live/ws/{session_id}")
async def multimodal_live_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for multimodal live real-time communication (using OpenAI)"""
    await websocket.accept()
    
    try:
        if session_id not in active_sessions:
            await websocket.send_json({
                "error": "Session not found",
                "status": "error"
            })
            await websocket.close()
            return
        
        session_config = active_sessions[session_id]["config"]
        client = get_openai_client()
        
        # Initialize OpenAI client for multimodal communication
        # Note: This is a simplified implementation
        # Full streaming would use OpenAI's streaming API
        
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session_id,
            "status": "connected"
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == "video_frame":
                    # Process video frame with OpenAI GPT-4 Vision
                    try:
                        image_data = data.get("image", "")
                        if image_data:
                            # Decode base64 image
                            image_bytes = base64.b64decode(image_data)
                            base64_image = base64.b64encode(image_bytes).decode('utf-8')
                            
                            # Create prompt for vision analysis
                            vision_prompt = """Look at this image and describe what you see in detail. 
                            Focus on:
                            - People and their activities
                            - Objects and their positions
                            - The environment and setting
                            - Any text or important details
                            - The overall scene context
                            
                            Provide a concise but comprehensive description."""
                            
                            # Analyze image using OpenAI GPT-4o Vision
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": vision_prompt},
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                max_tokens=300,
                                timeout=30.0
                            )
                            
                            description = response.choices[0].message.content or "Processing image..."
                            
                            # Send vision description back to client
                            await websocket.send_json({
                                "type": "vision_description",
                                "description": description,
                                "timestamp": data.get("timestamp")
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing video frame: {str(e)}"
                        })
                
                elif data.get("type") == "audio_chunk":
                    # Process audio chunk and get response
                    # Note: For full audio processing, use companion-api which handles STT/TTS
                    # This endpoint focuses on text and vision
                    await websocket.send_json({
                        "type": "audio_response",
                        "status": "processing",
                        "message": "Audio received. For full audio processing, use companion-api WebSocket endpoint."
                    })
                
                elif data.get("type") == "multimodal_query":
                    # Handle combined text + image query using OpenAI GPT-4o
                    try:
                        query_text = data.get("text", "")
                        image_data = data.get("image")
                        
                        if image_data and query_text:
                            # Multimodal query with image context
                            image_bytes = base64.b64decode(image_data)
                            base64_image = base64.b64encode(image_bytes).decode('utf-8')
                            
                            # Combine RAG knowledge with vision
                            similar_docs = search_chromadb(query_text, top_k=3, use_hybrid=True) if query_text else []
                            
                            context = "\n\n".join([
                                f"Source: {doc['document_name']}\n{doc['text']}"
                                for doc in similar_docs
                            ]) if similar_docs else ""
                            
                            if context:
                                system_prompt = "You are a helpful assistant that answers questions based on the provided knowledge base context and what you see in images."
                                user_content = [
                                    {"type": "text", "text": f"""Based on the knowledge base context and what you see in the image, answer the user's question.

Knowledge Base Context:
{context}

User Question: {query_text}

Look at the image and provide a comprehensive answer that combines what you see with the knowledge base information."""},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            else:
                                system_prompt = "You are a helpful assistant that answers questions about images."
                                user_content = [
                                    {"type": "text", "text": query_text or "Describe what you see in this image."},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_image}"
                                        }
                                    }
                                ]
                            
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_content}
                                ],
                                max_tokens=500,
                                timeout=30.0
                            )
                            
                            await websocket.send_json({
                                "type": "text_response",
                                "answer": response.choices[0].message.content,
                                "has_vision": True
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing multimodal query: {str(e)}"
                        })
                
                elif data.get("type") == "text_input":
                    # Handle text input as fallback
                    query = data.get("text", "")
                    if query:
                        # Use existing RAG query endpoint logic
                        similar_docs = search_chromadb(query, top_k=3, use_hybrid=True)
                        
                        if similar_docs:
                            answer = generate_answer(query, similar_docs)
                            await websocket.send_json({
                                "type": "text_response",
                                "answer": answer,
                                "sources": [{"document": doc['document_name'], "chunk": doc['chunk_index']} for doc in similar_docs]
                            })
                        else:
                            await websocket.send_json({
                                "type": "text_response",
                                "answer": "I couldn't find relevant information in the knowledge base."
                            })
                
                elif data.get("type") == "close":
                    break
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Connection error: {str(e)}"
        })
    finally:
        # Clean up session
        if session_id in active_sessions:
            del active_sessions[session_id]
        await websocket.close()

@app.get("/multimodal-live/sessions/{session_id}")
async def get_session_status(session_id: str):
    """Get status of a multimodal live session"""
    if session_id in active_sessions:
        return {
            "session_id": session_id,
            "status": "active",
            "config": active_sessions[session_id]["config"]
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/multimodal-live/sessions/{session_id}")
async def close_session(session_id: str):
    """Close a multimodal live session"""
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"status": "closed", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# Live Session (LS3 Screen Share) APIs

@app.post("/live-sessions")
async def create_live_session(request: LiveSessionCreateRequest):
    """Create a new live session (LS1A-LS3)"""
    try:
        session_id = str(uuid.uuid4())
        session = LiveSession.create(
            session_id=session_id,
            user_id=request.user_id,
            mode=request.mode,
            recording_consent=request.recording_consent
        )
        
        # Set frame sampling rate for LS3
        if request.mode == "LS3" and request.frame_sampling_rate:
            session.frame_sampling_rate = request.frame_sampling_rate
        
        # Create session based on mode
        if request.mode == "LS3":
            screen_session = ScreenShareSession(session)
            active_live_sessions[session_id] = screen_session
        elif request.mode == "LS1A":
            from live_sessions.audio_session import AudioLiveSession
            audio_session = AudioLiveSession(session)
            active_live_sessions[session_id] = audio_session
        elif request.mode in ["LS1B", "LS1C"]:
            from live_sessions.video_session import VideoLiveSession
            video_session = VideoLiveSession(session)
            active_live_sessions[session_id] = video_session
        
        session.transition_to("CONNECTING")
        
        return {
            "session_id": session_id,
            "status": session.state,
            "mode": session.mode,
            "message": "Live session created. Connect via WebSocket."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating live session: {str(e)}")

@app.websocket("/live-sessions/ws/{session_id}")
async def live_session_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live session (LS3 screen share)"""
    await websocket.accept()
    
    try:
        if session_id not in active_live_sessions:
            await websocket.send_json({
                "type": "error",
                "message": "Session not found"
            })
            await websocket.close()
            return
        
        session_obj = active_live_sessions[session_id]
        session_obj.session.transition_to("LIVE")
        
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session_id,
            "status": "connected",
            "mode": session_obj.session.mode
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                # LS1A Audio handling
                if session_obj.session.mode == "LS1A":
                    from live_sessions.audio_session import AudioLiveSession
                    if isinstance(session_obj, AudioLiveSession):
                        if msg_type == "audio_chunk":
                            audio_data = data.get("audio", "")
                            import base64
                            audio_bytes = base64.b64decode(audio_data) if audio_data else b""
                            result = await session_obj.process_audio_chunk(audio_bytes)
                            await websocket.send_json({
                                "type": "transcript",
                                "result": result
                            })
                            
                            # If transcript is final, generate response
                            if result.get("is_final"):
                                response = await session_obj.generate_response(result.get("transcript", ""))
                                audio_bytes = await session_obj.generate_audio(response["text"])
                                
                                await websocket.send_json({
                                    "type": "response",
                                    "text": response["text"],
                                    "audio": base64.b64encode(audio_bytes).decode() if audio_bytes else ""
                                })
                        
                        elif msg_type == "barge_in":
                            await session_obj.handle_barge_in()
                            await websocket.send_json({
                                "type": "barge_in_acknowledged"
                            })
                
                # LS1B/LS1C Video handling
                elif session_obj.session.mode in ["LS1B", "LS1C"]:
                    from live_sessions.video_session import VideoLiveSession
                    if isinstance(session_obj, VideoLiveSession):
                        if msg_type == "video_frame":
                            frame_data = data.get("frame", "")
                            frame_rate = data.get("frame_rate", 0.5)
                            result = await session_obj.process_video_frame(frame_data, frame_rate)
                            await websocket.send_json({
                                "type": "frame_analysis",
                                "result": result
                            })
                
                # LS3 Screen Share handling
                elif msg_type == "frame":
                    from live_sessions import ScreenShareSession
                    if isinstance(session_obj, ScreenShareSession):
                        # Process screen share frame
                        frame_data = data.get("frame", "")
                        query = data.get("query")
                        mode = data.get("mode", "describe")  # describe, guide, pin
                        
                        result = session_obj.process_frame(frame_data, query, mode)
                        
                        await websocket.send_json({
                            "type": "analysis",
                            "result": result,
                            "session_id": session_id
                        })
                
                elif msg_type == "pause":
                    session_obj.session.transition_to("PAUSED")
                    await websocket.send_json({
                        "type": "paused",
                        "session_id": session_id
                    })
                
                elif msg_type == "resume":
                    session_obj.session.transition_to("LIVE")
                    await websocket.send_json({
                        "type": "resumed",
                        "session_id": session_id
                    })
                
                elif msg_type == "close":
                    break
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Connection error: {str(e)}"
        })
    finally:
        # Cleanup
        if session_id in active_live_sessions:
            session_obj = active_live_sessions[session_id]
            session_obj.session.transition_to("ENDED")
            del active_live_sessions[session_id]
        await websocket.close()

@app.get("/live-sessions/{session_id}")
async def get_live_session(session_id: str):
    """Get live session status"""
    if session_id in active_live_sessions:
        session = active_live_sessions[session_id].session
        response = {
            "session_id": session.session_id,
            "state": session.state,
            "mode": session.mode,
            "audio_minutes_used": session.audio_minutes_used,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
        
        # Add mode-specific fields
        if session.mode == "LS3":
            response.update({
                "frames_processed": session.frames_processed,
                "vision_tokens_used": session.vision_tokens_used,
                "vision_tokens_limit": session.daily_vision_tokens_limit,
            })
        
        return response
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.put("/live-sessions/{session_id}/pause")
async def pause_live_session(session_id: str):
    """Pause a live session"""
    if session_id in active_live_sessions:
        session_obj = active_live_sessions[session_id]
        session_obj.session.transition_to("PAUSED")
        return {
            "status": "paused",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.put("/live-sessions/{session_id}/resume")
async def resume_live_session(session_id: str):
    """Resume a live session"""
    if session_id in active_live_sessions:
        session_obj = active_live_sessions[session_id]
        session_obj.session.transition_to("LIVE")
        return {
            "status": "resumed",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/live-sessions/{session_id}")
async def delete_live_session(session_id: str):
    """End a live session"""
    if session_id in active_live_sessions:
        session_obj = active_live_sessions[session_id]
        session_obj.session.transition_to("ENDED")
        del active_live_sessions[session_id]
        return {
            "status": "ended",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=404, detail="Session not found")

# Browser Automation APIs

@app.post("/browser/sessions")
async def create_browser_session(user_id: str = "default"):
    """Create a new browser session"""
    try:
        session_id = str(uuid.uuid4())
        browser_session = BrowserSession(session_id)
        await browser_session.initialize()
        active_browser_sessions[session_id] = browser_session
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Browser session created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating browser session: {str(e)}")

@app.get("/browser/sessions/{session_id}/ax-tree")
async def get_ax_tree(session_id: str):
    """Get accessibility tree for current page"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        ax_tree = await extract_ax_tree(browser_session.page)
        return {
            "session_id": session_id,
            "ax_tree": ax_tree,
            "count": len(ax_tree)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting AX tree: {str(e)}")

@app.get("/browser/sessions/{session_id}/page-info")
async def get_page_info(session_id: str):
    """Get current page information (URL, title, content summary)"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        page = browser_session.page
        url = page.url
        title = await page.title()
        
        # Get page content summary
        try:
            # Get main text content
            body_text = await page.evaluate("""
                () => {
                    const body = document.body;
                    if (!body) return '';
                    return body.innerText || body.textContent || '';
                }
            """)
            # Get first 500 chars as summary
            content_summary = body_text[:500] if body_text else ""
        except:
            content_summary = ""
        
        # Get all input fields
        try:
            inputs = await page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
                    return inputs.map(input => ({
                        id: input.id || '',
                        name: input.name || '',
                        type: input.type || input.tagName.toLowerCase(),
                        placeholder: input.placeholder || '',
                        value: input.value || '',
                        required: input.required || false
                    }));
                }
            """)
        except:
            inputs = []
        
        # Get all buttons
        try:
            buttons = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]'));
                    return buttons.map(btn => ({
                        id: btn.id || '',
                        name: btn.name || '',
                        type: btn.type || 'button',
                        text: btn.innerText || btn.value || btn.textContent || '',
                        disabled: btn.disabled || false
                    }));
                }
            """)
        except:
            buttons = []
        
        return {
            "session_id": session_id,
            "url": url,
            "title": title,
            "content_summary": content_summary,
            "inputs": inputs,
            "buttons": buttons
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting page info: {str(e)}")

@app.post("/browser/sessions/{session_id}/navigate")
async def navigate_browser(session_id: str, url: str):
    """Navigate browser to URL (with safety check)"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    
    # Check domain safety
    safety_check = browser_safety.check_domain(url)
    if not safety_check["allowed"]:
        raise HTTPException(
            status_code=403,
            detail=f"Navigation blocked: {safety_check['reason']}"
        )
    
    try:
        result = await browser_session.navigate(url)
        
        # Log action
        browser_safety.log_action("navigate", {
            "session_id": session_id,
            "url": url,
            "success": result["success"]
        })
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Navigation failed"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error navigating: {str(e)}")

@app.get("/browser/sessions/{session_id}/screenshot")
async def get_browser_screenshot(session_id: str):
    """Get screenshot of current page"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        screenshot_bytes = await browser_session.get_screenshot()
        import base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return {
            "session_id": session_id,
            "screenshot": screenshot_b64,
            "format": "png"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error taking screenshot: {str(e)}")

@app.delete("/browser/sessions/{session_id}")
async def close_browser_session(session_id: str):
    """Close browser session"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    await browser_session.close()
    del active_browser_sessions[session_id]
    
    return {
        "status": "closed",
        "session_id": session_id
    }

# Browser Action APIs

@app.post("/browser/sessions/{session_id}/actions/click")
async def browser_click(
    session_id: str,
    role: Optional[str] = None,
    name: Optional[str] = None,
    exact_name: bool = False
):
    """Click element by AX Tree properties"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        ax_tree = await extract_ax_tree(browser_session.page)
        executor = ActionExecutor(browser_session.page)
        result = await executor.click_element(ax_tree, role=role, name=name, exact_name=exact_name)
        
        # Log action
        browser_safety.log_action("click", {
            "session_id": session_id,
            "role": role,
            "name": name,
            "success": result.get("success", False)
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clicking element: {str(e)}")

@app.post("/browser/sessions/{session_id}/actions/type")
async def browser_type(
    session_id: str,
    text: str,
    role: Optional[str] = None,
    name: Optional[str] = None
):
    """Type text into input field"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        ax_tree = await extract_ax_tree(browser_session.page)
        executor = ActionExecutor(browser_session.page)
        result = await executor.type_text(ax_tree, text, role=role, name=name)
        
        # Log action
        browser_safety.log_action("type", {
            "session_id": session_id,
            "role": role,
            "name": name,
            "success": result.get("success", False)
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error typing text: {str(e)}")

@app.post("/browser/sessions/{session_id}/actions/extract")
async def browser_extract(
    session_id: str,
    role: Optional[str] = None,
    name: Optional[str] = None
):
    """Extract text from element"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        ax_tree = await extract_ax_tree(browser_session.page)
        executor = ActionExecutor(browser_session.page)
        result = await executor.extract_text(ax_tree, role=role, name=name)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

@app.post("/browser/sessions/{session_id}/actions/plan-execute")
async def browser_plan_execute(session_id: str, user_intent: str):
    """Execute plan for user intent using Plan-Act-Verify-Recover"""
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        automation = BrowserAutomation(browser_session.page)
        result = await automation.execute_plan(user_intent)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing plan: {str(e)}")

@app.post("/browser/sessions/{session_id}/actions/login")
async def browser_login(
    session_id: str,
    username: str,
    password: str,
    url: Optional[str] = None
):
    """
    Automate login flow: navigate to login page (if URL provided), 
    find and fill login fields, and submit.
    
    Args:
        session_id: Browser session ID
        username: Username or email
        password: Password
        url: Optional URL to navigate to first (if not already on login page)
    """
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        from browser.login_helper import LoginHelper
        
        login_helper = LoginHelper(browser_session.page)
        
        # Navigate to URL if provided
        if url:
            nav_result = await browser_session.navigate(url)
            if not nav_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to navigate to {url}",
                    "navigation_error": nav_result.get("error")
                }
        
        # Complete login flow
        result = await login_helper.complete_login(username, password)
        
        # Refresh screenshot and AX tree after login
        await browser_session.page.wait_for_timeout(1000)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")

@app.post("/browser/sessions/{session_id}/actions/login/find-fields")
async def browser_find_login_fields(session_id: str):
    """
    Find login fields on the current page without filling them.
    Useful for checking if login form is present.
    """
    if session_id not in active_browser_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_session = active_browser_sessions[session_id]
    if not browser_session.is_active():
        raise HTTPException(status_code=400, detail="Browser session not active")
    
    try:
        from browser.login_helper import LoginHelper
        
        login_helper = LoginHelper(browser_session.page)
        fields = await login_helper.find_login_fields()
        
        return fields
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding login fields: {str(e)}")

# Authentication endpoints (public registration for first user)

@app.post("/auth/register")
async def register_user(request: UserRegisterRequest):
    """
    Register a new user. 
    First user automatically becomes admin.
    """
    try:
        result = user_manager.create_user(
            email=request.email,
            password=request.password,
            username=request.username
        )
        return {
            "status": "success",
            "message": "User created successfully",
            "user": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login_user(request: UserLoginRequest):
    """
    Login user and get access token.
    """
    try:
        result = user_manager.authenticate_user(request.email, request.password)
        if not result:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# PDF Export APIs

@app.post("/export/conversation")
async def export_conversation(
    conversation_history: List[Dict],
    project_name: Optional[str] = None
):
    """Export conversation history to PDF"""
    try:
        pdf_bytes = export_conversation_to_pdf(conversation_history, project_name)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="conversation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting conversation: {str(e)}")

@app.post("/export/query-results")
async def export_query_results(
    query: str,
    answer: str,
    sources: List[Dict],
    memories_used: Optional[List[Dict]] = None,
    project_name: Optional[str] = None
):
    """Export query results to PDF"""
    try:
        pdf_bytes = export_query_results_to_pdf(query, answer, sources, memories_used, project_name)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="query_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting query results: {str(e)}")


# Windows Companion APIs (V2 - Sprint 3.1)

@app.post("/windows/device/register")
async def register_device():
    """Register a new Windows device for pairing."""
    try:
        result = device_pairing.register_device()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering device: {str(e)}")

@app.get("/windows/device/{device_id}/status")
async def get_device_status(device_id: str):
    """Check device status (for revocation check)."""
    try:
        status = device_pairing.check_device_status(device_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking device status: {str(e)}")

@app.post("/windows/device/{device_id}/revoke")
async def revoke_device(device_id: str):
    """Revoke a device (admin only)."""
    try:
        success = device_pairing.revoke_device(device_id)
        if success:
            return {"status": "revoked", "device_id": device_id}
        else:
            raise HTTPException(status_code=404, detail="Device not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error revoking device: {str(e)}")

@app.post("/windows/credentials")
async def store_credential(
    credential_name: str,
    username: str,
    password: str,
    description: Optional[str] = None
):
    """Store credential in Windows Credential Manager."""
    try:
        success = credential_manager.store_credential(
            credential_name, username, password, description
        )
        if success:
            return {"status": "stored", "credential_name": credential_name}
        else:
            raise HTTPException(status_code=500, detail="Failed to store credential")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing credential: {str(e)}")

@app.get("/windows/credentials/{credential_name}")
async def get_credential(credential_name: str):
    """Retrieve credential from Windows Credential Manager."""
    try:
        credential = credential_manager.retrieve_credential(credential_name)
        if credential:
            # Never return password in API response (security)
            return {
                "credential_name": credential_name,
                "username": credential["username"],
                "description": credential.get("description", ""),
                "exists": True
            }
        else:
            raise HTTPException(status_code=404, detail="Credential not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving credential: {str(e)}")

@app.delete("/windows/credentials/{credential_name}")
async def delete_credential(credential_name: str):
    """Delete credential from Windows Credential Manager."""
    try:
        success = credential_manager.delete_credential(credential_name)
        if success:
            return {"status": "deleted", "credential_name": credential_name}
        else:
            raise HTTPException(status_code=404, detail="Credential not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting credential: {str(e)}")

@app.get("/windows/credentials")
async def list_credentials():
    """List all Jarvis credentials (names only, no secrets)."""
    try:
        credential_names = credential_manager.list_credentials()
        return {
            "credentials": credential_names,
            "total": len(credential_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing credentials: {str(e)}")


# OS Automation APIs (V2 - Sprint 3.2)

@app.post("/windows/apps/launch")
async def launch_app(app_path: str, arguments: Optional[List[str]] = None):
    """Launch a Windows application."""
    try:
        result = app_manager.launch_app(app_path, arguments)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to launch app"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error launching app: {str(e)}")

@app.post("/windows/apps/switch")
async def switch_to_app(window_title: str):
    """Switch to an existing application window."""
    try:
        result = app_manager.switch_to_app(window_title)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Window not found"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching to app: {str(e)}")

@app.get("/windows/apps/running")
async def list_running_apps():
    """List currently running applications."""
    try:
        apps = app_manager.list_running_apps()
        return {
            "apps": apps,
            "total": len(apps)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing apps: {str(e)}")

@app.get("/windows/files/read")
async def read_file(file_path: str, allow_list: Optional[List[str]] = None):
    """Read file content."""
    try:
        result = file_manager.read_file(file_path, allow_list)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error", "Access denied"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.post("/windows/files/write")
async def write_file(
    file_path: str,
    content: str,
    require_approval: bool = True
):
    """Write file (requires approval by default)."""
    try:
        result = file_manager.write_file(file_path, content, require_approval)
        if result.get("success"):
            return result
        elif result.get("requires_approval"):
            # Return approval request (not an error)
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error", "Access denied"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

@app.delete("/windows/files/delete")
async def delete_file(file_path: str, require_approval: bool = True):
    """Delete file (requires approval by default)."""
    try:
        result = file_manager.delete_file(file_path, require_approval)
        if result.get("success"):
            return result
        elif result.get("requires_approval"):
            # Return approval request (not an error)
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error", "Access denied"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.get("/windows/files/list")
async def list_directory(dir_path: str, allow_list: Optional[List[str]] = None):
    """List directory contents."""
    try:
        result = file_manager.list_directory(dir_path, allow_list)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=403, detail=result.get("error", "Access denied"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")

@app.post("/windows/vision/capture")
async def capture_screenshot(window_title: Optional[str] = None):
    """Capture screenshot of window or entire screen."""
    try:
        screenshot_bytes = screen_vision.capture_screenshot(window_title)
        if screenshot_bytes:
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            return {
                "success": True,
                "screenshot": screenshot_base64,
                "format": "png"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to capture screenshot")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error capturing screenshot: {str(e)}")

@app.post("/windows/vision/find-element")
async def find_element_in_screenshot(
    screenshot: str,  # base64 encoded
    element_description: str,
    query: Optional[str] = None
):
    """Find element in screenshot using vision model."""
    try:
        screenshot_bytes = base64.b64decode(screenshot)
        result = screen_vision.find_element_in_screenshot(
            screenshot_bytes, element_description, query
        )
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Vision analysis failed"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding element: {str(e)}")

@app.post("/windows/vision/click")
async def click_coordinate(x: int, y: int):
    """Click at specific screen coordinates."""
    try:
        # Check ROC if active
        active_roc = roc.get_roc()
        if active_roc and not roc.is_within_roc(x, y):
            raise HTTPException(
                status_code=403,
                detail="Coordinates outside Region-of-Control"
            )
        
        result = screen_vision.click_coordinate(x, y)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Click failed"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clicking coordinate: {str(e)}")

@app.post("/windows/roc/set")
async def set_roc(window_title: str):
    """Set Region-of-Control to a specific window."""
    try:
        result = roc.set_roc(window_title)
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "Window not found"))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting ROC: {str(e)}")

@app.delete("/windows/roc")
async def clear_roc():
    """Clear active Region-of-Control."""
    try:
        result = roc.clear_roc()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing ROC: {str(e)}")

@app.get("/windows/roc")
async def get_roc():
    """Get active Region-of-Control."""
    try:
        active_roc = roc.get_roc()
        if active_roc:
            return {
                "success": True,
                "roc": active_roc
            }
        else:
            return {
                "success": False,
                "message": "No active ROC"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ROC: {str(e)}")

@app.get("/windows/roc/windows")
async def list_windows():
    """List all visible windows for ROC selection."""
    try:
        windows = roc.list_windows()
        return {
            "windows": windows,
            "total": len(windows)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing windows: {str(e)}")


# Panic Stop & Automation Indicator APIs (V2 - Sprint 3.3)

@app.post("/windows/panic/stop")
async def trigger_panic_stop(automation_id: Optional[str] = None):
    """Trigger panic stop for automation(s)."""
    try:
        result = panic_stop.trigger_panic_stop(automation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering panic stop: {str(e)}")

@app.get("/windows/panic/status")
async def get_panic_status():
    """Get panic stop status and active automations."""
    try:
        return {
            "panic_active": panic_stop.is_panic_stopped(),
            "active_automations": panic_stop.get_active_automations(),
            "total_active": len(panic_stop.get_active_automations())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting panic status: {str(e)}")

@app.get("/windows/panic/incidents")
async def get_panic_incidents(limit: int = 10):
    """Get recent panic stop incidents."""
    try:
        incidents = panic_stop.get_incident_log(limit)
        return {
            "incidents": incidents,
            "total": len(incidents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting incidents: {str(e)}")

@app.post("/windows/automation/start")
async def start_automation(
    automation_id: str,
    action_description: str,
    total_steps: int = 1
):
    """Start tracking an automation."""
    try:
        success = automation_indicator.start_automation(
            automation_id, action_description, total_steps
        )
        if success:
            return {
                "success": True,
                "automation_id": automation_id,
                "status": "started"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start automation tracking")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting automation: {str(e)}")

@app.post("/windows/automation/update")
async def update_automation_step(step: int, step_description: Optional[str] = None):
    """Update current step in automation."""
    try:
        success = automation_indicator.update_step(step, step_description)
        if success:
            return {"success": True, "step": step}
        else:
            raise HTTPException(status_code=404, detail="No active automation")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating automation: {str(e)}")

@app.post("/windows/automation/pause")
async def pause_automation():
    """Pause current automation."""
    try:
        success = automation_indicator.pause_automation()
        if success:
            return {"success": True, "status": "paused"}
        else:
            raise HTTPException(status_code=404, detail="No active automation")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing automation: {str(e)}")

@app.post("/windows/automation/resume")
async def resume_automation():
    """Resume paused automation."""
    try:
        success = automation_indicator.resume_automation()
        if success:
            return {"success": True, "status": "resumed"}
        else:
            raise HTTPException(status_code=404, detail="No paused automation")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming automation: {str(e)}")

@app.post("/windows/automation/stop")
async def stop_automation(success: bool = True, error: Optional[str] = None):
    """Stop current automation."""
    try:
        success_result = automation_indicator.stop_automation(success, error)
        if success_result:
            return {"success": True, "status": "stopped"}
        else:
            raise HTTPException(status_code=404, detail="No active automation")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping automation: {str(e)}")

@app.get("/windows/automation/status")
async def get_automation_status():
    """Get current automation status."""
    try:
        status = automation_indicator.get_current_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting automation status: {str(e)}")

@app.get("/windows/automation/console")
async def get_automation_console(limit: int = 20):
    """Get automation console (current status + history)."""
    try:
        current_status = automation_indicator.get_current_status()
        history = automation_indicator.get_automation_history(limit)
        return {
            "current": current_status,
            "history": history,
            "total_history": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting automation console: {str(e)}")


# Multi-Agent CrewAI APIs (V2 - Sprint 3.4)

@app.post("/agents/execute")
async def execute_agent_task(
    task_description: str,
    user_id: str = "default",
    project_id: Optional[str] = None
):
    """Execute a multi-agent task using CrewAI orchestration."""
    try:
        manager = get_crewai_manager()
        result = manager.execute_task(
            task_description=task_description,
            user_id=user_id,
            project_id=project_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing agent task: {str(e)}")

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    try:
        manager = get_crewai_manager()
        return {
            "browser_agent": manager.orchestrator.browser_agent.get_agent() is not None,
            "os_agent": manager.orchestrator.os_agent.get_agent() is not None,
            "rag_agent": manager.orchestrator.rag_agent.get_agent() is not None,
            "crewai_available": manager.crew is not None
        }
    except Exception as e:
        # Return basic status if CrewAI manager fails
        return {
            "browser_agent": False,
            "os_agent": False,
            "rag_agent": False,
            "crewai_available": False,
            "error": str(e),
            "note": "CrewAI may not be fully configured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agents status: {str(e)}")


# Evaluation Suite APIs (V2 - Sprint 3.6)

@app.post("/eval/run")
async def run_evaluation_suite():
    """Run the full evaluation suite."""
    try:
        # In a real implementation, this would trigger the evaluation runner
        # For now, return a placeholder
        return {
            "status": "started",
            "message": "Evaluation suite started. Results will be available shortly.",
            "estimated_duration": "5-10 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running evaluation suite: {str(e)}")

@app.get("/eval/results")
async def get_evaluation_results():
    """Get latest evaluation test results."""
    try:
        # In a real implementation, this would return actual test results
        return {
            "results": [],
            "message": "No results available. Run evaluation suite first."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting evaluation results: {str(e)}")

@app.post("/eval/baseline/create")
async def create_evaluation_baseline(baseline_name: str = "default"):
    """Create a baseline from current test results."""
    try:
        # In a real implementation, this would create a baseline
        return {
            "success": True,
            "baseline_name": baseline_name,
            "message": "Baseline created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating baseline: {str(e)}")

@app.get("/eval/regression")
async def get_regression_report(baseline_name: str = "default"):
    """Get regression test report."""
    try:
        # In a real implementation, this would return regression comparison
        return {
            "baseline_found": False,
            "message": "No baseline found. Create baseline first."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting regression report: {str(e)}")

# Media Generation APIs

@app.post("/media/images/generate")
async def generate_image(
    request: ImageGenerationRequest,
    user_id: str = "default"
):
    """Generate image using DALL-E 3"""
    try:
        result = image_generator.generate_image(
            prompt=request.prompt,
            size=request.size,
            quality=request.quality,
            style=request.style,
            n=request.n,
            user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/media/images/edit")
async def edit_image(
    request: ImageEditRequest,
    user_id: str = "default"
):
    """Edit image (creates variations for DALL-E 3)"""
    try:
        # Get image path from storage
        image_path = media_storage.get_image_path(request.image_id)
        if not image_path:
            raise HTTPException(status_code=404, detail="Image not found")
        
        result = image_generator.edit_image(
            image_path=str(image_path),
            mask_path=request.mask_path,
            prompt=request.prompt,
            size=request.size,
            n=request.n,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image editing failed: {str(e)}")

@app.post("/media/images/variations")
async def create_image_variations(
    request: ImageVariationsRequest,
    user_id: str = "default"
):
    """Create image variations"""
    try:
        image_path = media_storage.get_image_path(request.image_id)
        if not image_path:
            raise HTTPException(status_code=404, detail="Image not found")
        
        result = image_generator.create_variations(
            image_path=str(image_path),
            n=request.n,
            size=request.size,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image variation creation failed: {str(e)}")

@app.post("/media/images/analyze")
async def analyze_image(
    request: ImageAnalysisRequest,
    user_id: str = "default"
):
    """Analyze image using GPT-4 Vision"""
    try:
        image_path = media_storage.get_image_path(request.image_id)
        if not image_path:
            raise HTTPException(status_code=404, detail="Image not found")
        
        result = image_generator.analyze_image(
            image_path=str(image_path),
            prompt=request.prompt,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.get("/media/images/{image_id}")
async def get_image(image_id: str):
    """Get generated image"""
    try:
        image_path = media_storage.get_image_path(image_id)
        if not image_path or not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        metadata = media_storage.get_image_metadata(image_id)
        
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        return Response(
            content=image_data,
            media_type="image/png",
            headers={
                "X-Image-ID": image_id,
                "X-Prompt": metadata.get("prompt", "") if metadata else ""
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image: {str(e)}")

@app.get("/media/images")
async def list_user_images(user_id: str = "default"):
    """List all images for a user"""
    try:
        images = media_storage.list_user_images(user_id)
        return {
            "images": images,
            "count": len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@app.post("/media/videos/generate")
async def generate_video(
    request: VideoGenerationRequest,
    user_id: str = "default"
):
    """Generate video from text prompt"""
    try:
        result = video_generator.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution,
            fps=request.fps,
            user_id=user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.post("/media/videos/edit")
async def edit_video(
    video_id: str,
    operations: List[Dict],
    user_id: str = "default"
):
    """Edit video using FFmpeg"""
    try:
        video_path = media_storage.get_image_path(video_id)  # Reuse method
        if not video_path:
            raise HTTPException(status_code=404, detail="Video not found")
        
        result = video_generator.edit_video(
            video_path=str(video_path),
            operations=operations,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video editing failed: {str(e)}")

@app.post("/media/videos/summarize")
async def summarize_video(
    video_id: str,
    frame_sample_rate: float = 1.0,
    user_id: str = "default"
):
    """Summarize video by analyzing frames"""
    try:
        video_path = media_storage.get_image_path(video_id)  # Reuse method
        if not video_path:
            raise HTTPException(status_code=404, detail="Video not found")
        
        result = video_generator.summarize_video(
            video_path=str(video_path),
            frame_sample_rate=frame_sample_rate,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video summarization failed: {str(e)}")

@app.post("/media/charts/generate")
async def generate_chart(
    request: ChartGenerationRequest,
    user_id: str = "default",
    format: str = "png"
):
    """Generate chart from data"""
    try:
        result = chart_generator.generate_chart(
            chart_type=request.chart_type,
            data=request.data,
            title=request.title,
            x_label=request.x_label,
            y_label=request.y_label,
            options=request.options,
            user_id=user_id,
            format=format
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")

@app.get("/media/charts/{chart_id}")
async def get_chart(chart_id: str):
    """Get generated chart"""
    try:
        chart_path = media_storage.get_image_path(chart_id)  # Reuse method
        if not chart_path or not chart_path.exists():
            raise HTTPException(status_code=404, detail="Chart not found")
        
        metadata = media_storage.get_image_metadata(chart_id)
        format_type = metadata.get("format", "png") if metadata else "png"
        
        with open(chart_path, "rb") as f:
            chart_data = f.read()
        
        media_type_map = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf"
        }
        
        return Response(
            content=chart_data,
            media_type=media_type_map.get(format_type, "image/png"),
            headers={
                "X-Chart-ID": chart_id,
                "X-Title": metadata.get("title", "") if metadata else ""
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chart: {str(e)}")

# Spotify Integration APIs

@app.get("/spotify/auth")
async def spotify_auth(user_id: str = "default"):
    """Initiate Spotify OAuth flow"""
    try:
        client = get_spotify_client(user_id)
        auth_url = client.get_auth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify auth failed: {str(e)}")

@app.get("/spotify/callback")
async def spotify_callback(code: str, user_id: str = "default"):
    """Handle Spotify OAuth callback"""
    try:
        client = get_spotify_client(user_id)
        result = client.handle_callback(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify callback failed: {str(e)}")

@app.post("/spotify/playlists")
async def create_spotify_playlist(
    request: SpotifyPlaylistCreateRequest,
    user_id: str = "default"
):
    """Create Spotify playlist"""
    try:
        client = get_spotify_client(user_id)
        result = client.create_playlist(
            name=request.name,
            description=request.description,
            public=request.public,
            tracks=request.tracks
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Playlist creation failed: {str(e)}")

@app.get("/spotify/playlists")
async def list_spotify_playlists(user_id: str = "default"):
    """List user's Spotify playlists"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(
                status_code=401, 
                detail="Not authenticated with Spotify. Please authenticate first via /spotify/auth endpoint."
            )
        
        playlists = client.client.current_user_playlists()
        return {
            "playlists": playlists.get("items", []),
            "count": len(playlists.get("items", []))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list playlists: {str(e)}")

@app.get("/spotify/playlists/{playlist_id}")
async def get_spotify_playlist(playlist_id: str, user_id: str = "default"):
    """Get Spotify playlist details"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        playlist = client.client.playlist(playlist_id)
        return playlist
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get playlist: {str(e)}")

@app.put("/spotify/playlists/{playlist_id}")
async def update_spotify_playlist(
    playlist_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    public: Optional[bool] = None,
    user_id: str = "default"
):
    """Update Spotify playlist"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        client.client.playlist_change_details(
            playlist_id,
            name=name,
            description=description,
            public=public
        )
        return {"success": True, "playlist_id": playlist_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update playlist: {str(e)}")

@app.delete("/spotify/playlists/{playlist_id}")
async def delete_spotify_playlist(playlist_id: str, user_id: str = "default"):
    """Delete Spotify playlist"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        client.client.user_playlist_unfollow("me", playlist_id)
        return {"success": True, "playlist_id": playlist_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete playlist: {str(e)}")

@app.post("/spotify/playlists/{playlist_id}/tracks")
async def add_playlist_tracks(
    playlist_id: str,
    tracks: List[str],
    user_id: str = "default"
):
    """Add tracks to Spotify playlist"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        client.client.playlist_add_items(playlist_id, tracks)
        return {"success": True, "tracks_added": len(tracks)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add tracks: {str(e)}")

@app.delete("/spotify/playlists/{playlist_id}/tracks")
async def remove_playlist_tracks(
    playlist_id: str,
    tracks: List[str],
    user_id: str = "default"
):
    """Remove tracks from Spotify playlist"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        client.client.playlist_remove_all_occurrences_of_items(playlist_id, tracks)
        return {"success": True, "tracks_removed": len(tracks)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove tracks: {str(e)}")

@app.post("/spotify/search")
async def spotify_search(
    query: str,
    type: str = "track",
    limit: int = 20,
    user_id: str = "default"
):
    """Search Spotify"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        result = client.search(query, type=type, limit=limit)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/spotify/playlists/smart-create")
async def smart_create_playlist(
    request: SmartPlaylistRequest,
    user_id: str = "default"
):
    """Create playlist using AI to interpret natural language"""
    try:
        client = get_spotify_client(user_id)
        if not client.client:
            raise HTTPException(status_code=401, detail="Not authenticated with Spotify")
        
        result = client.smart_create_playlist(
            description=request.description,
            track_count=request.track_count,
            include_genres=request.include_genres,
            exclude_genres=request.exclude_genres,
            user_id=user_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart playlist creation failed: {str(e)}")

# Authentication removed - all endpoints are public

# Legacy user endpoints removed - authentication disabled

# Advanced Browser Automation APIs

@app.post("/browser/sessions/{session_id}/forms/fill")
async def fill_browser_form(
    session_id: str,
    form_data: Dict[str, str],
    credential_name: Optional[str] = None
):
    """Auto-fill form in browser session"""
    try:
        if session_id not in active_browser_sessions:
            raise HTTPException(status_code=404, detail="Browser session not found")
        
        browser_session = active_browser_sessions[session_id]
        from browser.advanced.form_fill import FormFiller
        
        filler = FormFiller(browser_session)
        result = await filler.fill_form(form_data, credential_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Form fill failed: {str(e)}")

@app.post("/browser/sessions/{session_id}/workflows/record")
async def start_workflow_recording(session_id: str):
    """Start recording browser workflow"""
    try:
        if session_id not in active_browser_sessions:
            raise HTTPException(status_code=404, detail="Browser session not found")
        
        browser_session = active_browser_sessions[session_id]
        if not hasattr(browser_session, "workflow_recorder"):
            from browser.advanced.workflow_recorder import WorkflowRecorder
            browser_session.workflow_recorder = WorkflowRecorder()
        
        browser_session.workflow_recorder.start_recording()
        return {"status": "recording_started", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start recording: {str(e)}")

@app.post("/browser/sessions/{session_id}/workflows/replay")
async def replay_workflow(session_id: str, workflow: Dict):
    """Replay recorded workflow"""
    try:
        if session_id not in active_browser_sessions:
            raise HTTPException(status_code=404, detail="Browser session not found")
        
        browser_session = active_browser_sessions[session_id]
        from browser.actions import ActionExecutor
        
        executor = ActionExecutor(browser_session.page)
        executed_count = 0
        
        for step in workflow.get("steps", []):
            try:
                action_type = step["action_type"]
                selector = step["selector"]
                value = step.get("value")
                
                if action_type == "click":
                    await executor.click_element(selector)
                elif action_type == "type":
                    await executor.type_text(selector, value or "")
                elif action_type == "navigate":
                    await browser_session.page.goto(selector)
                
                executed_count += 1
            except Exception as e:
                # Continue with next step on error
                continue
        
        return {
            "status": "completed",
            "executed_steps": executed_count,
            "total_steps": len(workflow.get("steps", []))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow replay failed: {str(e)}")

# Smart Document Processing APIs

@app.post("/documents/ocr")
async def extract_text_ocr(
    file_path: str,
    language: Optional[str] = None,
    user_id: str = "default"
):
    """Extract text from image using OCR"""
    try:
        result = document_processor.extract_text_with_ocr(file_path, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

@app.post("/documents/tables")
async def extract_tables(
    pdf_path: str,
    user_id: str = "default"
):
    """Extract tables from PDF"""
    try:
        result = document_processor.extract_tables(pdf_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Table extraction failed: {str(e)}")

@app.post("/documents/summarize")
async def summarize_document(
    text: str,
    max_length: int = 300,
    user_id: str = "default"
):
    """Summarize document using LLM"""
    try:
        result = document_processor.summarize_document(text, max_length, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document summarization failed: {str(e)}")

@app.post("/documents/categorize")
async def categorize_document(
    text: str,
    user_id: str = "default"
):
    """Automatically categorize and tag document"""
    try:
        result = document_processor.categorize_document(text, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document categorization failed: {str(e)}")

# Analytics & Insights APIs

@app.get("/analytics/usage")
async def get_usage_statistics(
    user_id: str = "default",
    days: int = 30
):
    """Get usage statistics for a user"""
    try:
        result = analytics_dashboard.get_usage_statistics(user_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage statistics: {str(e)}")

@app.get("/analytics/cost")
async def get_cost_analysis(
    user_id: str = "default",
    days: int = 30
):
    """Get cost analysis and optimization suggestions"""
    try:
        result = analytics_dashboard.get_cost_analysis(user_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cost analysis: {str(e)}")

@app.get("/analytics/performance")
async def get_performance_metrics(
    user_id: str = "default",
    days: int = 30
):
    """Get performance metrics"""
    try:
        result = analytics_dashboard.get_performance_metrics(user_id, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

# Collaboration APIs

@app.post("/collaboration/sessions")
async def create_collaboration_session(
    owner_id: str,
    session_type: str = "browser",
    target_id: Optional[str] = None
):
    """Create new collaboration session"""
    try:
        result = collaboration_manager.create_session(owner_id, session_type, target_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collaboration session: {str(e)}")

@app.get("/collaboration/sessions")
async def list_collaboration_sessions(user_id: str):
    """List user's collaboration sessions"""
    try:
        sessions = collaboration_manager.list_user_sessions(user_id)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@app.get("/collaboration/sessions/{session_id}")
async def get_collaboration_session(session_id: str):
    """Get collaboration session details"""
    try:
        session = collaboration_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "owner_id": session.owner_id,
            "session_type": session.session_type,
            "members": session.get_members(),
            "state": session.state,
            "created_at": session.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session: {str(e)}")

@app.post("/collaboration/sessions/{session_id}/invite")
async def invite_to_session(
    session_id: str,
    user_id: str,
    role: str = "viewer"
):
    """Invite user to collaboration session"""
    try:
        session = collaboration_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        success = session.add_member(user_id, role)
        if not success:
            raise HTTPException(status_code=400, detail="User already in session")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": user_id,
            "role": role
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inviting user: {str(e)}")

@app.websocket("/collaboration/sessions/{session_id}/ws")
async def collaboration_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()
    
    try:
        session = collaboration_manager.get_session(session_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "message": "Session not found"
            })
            await websocket.close()
            return
        
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "members": session.get_members()
        })
        
        # Handle collaboration messages
        while True:
            try:
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                if msg_type == "cursor_update":
                    # Update cursor position
                    user_id = data.get("user_id")
                    position = data.get("position")
                    selection = data.get("selection")
                    
                    # Broadcast cursor update to other members
                    await websocket.send_json({
                        "type": "cursor_updated",
                        "user_id": user_id,
                        "position": position,
                        "selection": selection
                    })
                
                elif msg_type == "document_change":
                    # Apply document change
                    document_id = data.get("document_id")
                    user_id = data.get("user_id")
                    change_type = data.get("change_type")
                    position = data.get("position")
                    content = data.get("content")
                    length = data.get("length")
                    
                    editor = get_editor(document_id)
                    result = editor.apply_change(user_id, change_type, position, content, length)
                    
                    # Broadcast change to all members
                    await websocket.send_json({
                        "type": "document_changed",
                        "result": result
                    })
                
                elif msg_type == "close":
                    break
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Connection error: {str(e)}"
        })
    finally:
        await websocket.close()

# Advanced Memory Features APIs

@app.post("/memory/cluster")
async def cluster_memories(
    user_id: str,
    project_id: Optional[str] = None,
    num_clusters: Optional[int] = None
):
    """Cluster memories by semantic similarity"""
    try:
        result = memory_clustering.cluster_memories(user_id, project_id, num_clusters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory clustering failed: {str(e)}")

@app.get("/memory/conflicts")
async def detect_memory_conflicts(
    user_id: str,
    project_id: Optional[str] = None
):
    """Detect conflicting or contradictory memories"""
    try:
        result = memory_conflict_detector.detect_conflicts(user_id, project_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conflict detection failed: {str(e)}")

@app.post("/memory/templates")
async def create_memory_template(
    name: str,
    description: str,
    memory_type: str,
    fields: List[Dict]
):
    """Create new memory template"""
    try:
        result = memory_template_manager.create_template(name, description, memory_type, fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Template creation failed: {str(e)}")

@app.get("/memory/templates")
async def list_memory_templates():
    """List all available memory templates"""
    try:
        templates = memory_template_manager.list_templates()
        return {"templates": templates, "count": len(templates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing templates: {str(e)}")

@app.post("/memory/import")
async def import_memories(
    user_id: str,
    memories: List[Dict],
    project_id: Optional[str] = None
):
    """Import memories from external source"""
    try:
        from models import MemoryItem
        imported_count = 0
        
        for mem_data in memories:
            memory = MemoryItem.create(
                user_id=user_id,
                content=mem_data.get("content", ""),
                memory_type=mem_data.get("memory_type", "fact"),
                project_id=project_id
            )
            memory_storage.create(memory)
            imported_count += 1
        
        return {
            "success": True,
            "imported_count": imported_count,
            "total": len(memories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory import failed: {str(e)}")

@app.get("/memory/export")
async def export_memories(
    user_id: str,
    project_id: Optional[str] = None,
    format: str = "json"
):
    """Export memories to external format"""
    try:
        memories = memory_storage.list(user_id, project_id)
        
        if format == "json":
            export_data = [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "memory_type": mem.memory_type,
                    "project_id": mem.project_id,
                    "created_at": mem.created_at.isoformat(),
                    "updated_at": mem.updated_at.isoformat()
                }
                for mem in memories
            ]
            return {
                "format": "json",
                "memories": export_data,
                "count": len(export_data)
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory export failed: {str(e)}")

# API Marketplace & Integrations APIs

@app.get("/integrations")
async def list_integrations():
    """List all available integrations"""
    integrations = [
        {
            "name": "zapier",
            "type": "webhook",
            "status": "available",
            "description": "Webhook-based automation with Zapier"
        },
        {
            "name": "slack",
            "type": "bot",
            "status": "available" if os.getenv("SLACK_BOT_TOKEN") else "not_configured",
            "description": "Slack bot for notifications"
        },
        {
            "name": "email",
            "type": "notification",
            "status": "available" if os.getenv("SMTP_USER") else "not_configured",
            "description": "Email notifications"
        },
        {
            "name": "spotify",
            "type": "api",
            "status": "available",
            "description": "Spotify playlist management"
        }
    ]
    
    return {
        "integrations": integrations,
        "count": len(integrations)
    }

@app.post("/integrations/{name}/connect")
async def connect_integration(
    name: str,
    config: Dict
):
    """Connect an integration with configuration"""
    try:
        if name == "zapier":
            from integrations.zapier import zapier_integration
            webhook_url = config.get("webhook_url")
            event_type = config.get("event_type", "query")
            user_id = config.get("user_id", "default")
            
            result = zapier_integration.register_webhook(user_id, webhook_url, event_type)
            return result
        elif name == "slack":
            return {"status": "connected", "integration": name}
        elif name == "email":
            return {"status": "connected", "integration": name}
        else:
            raise HTTPException(status_code=404, detail=f"Integration '{name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integration connection failed: {str(e)}")

@app.get("/integrations/{name}/status")
async def get_integration_status(name: str):
    """Get integration connection status"""
    try:
        if name == "zapier":
            from integrations.zapier import zapier_integration
            return {
                "integration": name,
                "status": "connected",
                "webhook_count": len(zapier_integration.webhooks)
            }
        elif name == "slack":
            from integrations.slack import slack_integration
            return {
                "integration": name,
                "status": "connected" if slack_integration.client else "not_configured"
            }
        elif name == "email":
            from integrations.email import email_integration
            return {
                "integration": name,
                "status": "connected" if email_integration.smtp_user else "not_configured"
            }
        elif name == "spotify":
            return {
                "integration": name,
                "status": "available"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Integration '{name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting integration status: {str(e)}")

@app.post("/integrations/{name}/webhook")
async def handle_integration_webhook(
    name: str,
    payload: Dict
):
    """Handle incoming webhook from integration"""
    try:
        if name == "zapier":
            event_type = payload.get("event_type")
            data = payload.get("data", {})
            return {
                "status": "processed",
                "event_type": event_type
            }
        else:
            raise HTTPException(status_code=404, detail=f"Integration '{name}' does not support webhooks")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook handling failed: {str(e)}")

# Advanced Vision Reasoning APIs

@app.post("/vision/reason")
async def multi_step_vision_reasoning(
    images: List[str],  # base64 encoded
    query: str,
    steps: Optional[List[str]] = None,
    user_id: str = "default"
):
    """Perform multi-step visual reasoning"""
    try:
        result = vision_reasoning.multi_step_reasoning(images, query, steps, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision reasoning failed: {str(e)}")

@app.post("/vision/track")
async def track_object(
    images: List[str],  # base64 encoded frames
    object_description: str,
    user_id: str = "default"
):
    """Track object across video frames"""
    try:
        result = vision_reasoning.track_object(images, object_description, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Object tracking failed: {str(e)}")

@app.post("/vision/analyze-scene")
async def analyze_scene(
    image: str,  # base64 encoded
    analysis_type: str = "comprehensive",
    user_id: str = "default"
):
    """Comprehensive scene analysis"""
    try:
        result = vision_reasoning.analyze_scene(image, analysis_type, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scene analysis failed: {str(e)}")

# Agentic Autonomy APIs

@app.post("/agents/{agent_id}/learn")
async def learn_from_feedback(
    agent_id: str,
    feedback: str,
    pattern: Dict
):
    """Record feedback for agent learning"""
    try:
        agent_type = pattern.get("agent_type", "general")
        agent = agent_autonomy_manager.get_or_create_agent(agent_id, agent_type)
        agent.learn_from_feedback(feedback, pattern)
        
        return {
            "success": True,
            "agent_id": agent_id,
            "learned_patterns_count": len(agent.learned_patterns)
        }
    except Exception as e:
        # Return error response instead of raising to avoid 500
        return {
            "success": False,
            "agent_id": agent_id,
            "error": str(e),
            "learned_patterns_count": 0
        }

@app.post("/agents/{agent_id}/improve")
async def improve_agent(agent_id: str):
    """Trigger agent self-improvement"""
    try:
        agent = agent_autonomy_manager.get_or_create_agent(agent_id, "general")
        suggestions = agent.get_improvement_suggestions()
        
        return {
            "agent_id": agent_id,
            "success_rate": agent.success_rate,
            "total_tasks": agent.total_tasks,
            "suggestions": suggestions,
            "improvement_applied": len(suggestions) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent improvement failed: {str(e)}")

@app.get("/agents/marketplace")
async def get_agent_marketplace():
    """Get available agents from marketplace"""
    try:
        agents = agent_autonomy_manager.list_agents()
        
        marketplace_agents = [
            {
                "agent_id": "browser_expert",
                "name": "Browser Automation Expert",
                "description": "Specialized in web automation tasks",
                "type": "browser",
                "rating": 4.8
            },
            {
                "agent_id": "data_analyst",
                "name": "Data Analyst Agent",
                "description": "Analyzes data and generates insights",
                "type": "rag",
                "rating": 4.6
            }
        ]
        
        return {
            "custom_agents": agents,
            "marketplace_agents": marketplace_agents,
            "total": len(agents) + len(marketplace_agents)
        }
    except Exception as e:
        # Return basic marketplace if manager fails
        return {
            "custom_agents": [],
            "marketplace_agents": [
                {
                    "agent_id": "browser_expert",
                    "name": "Browser Automation Expert",
                    "description": "Specialized in web automation tasks",
                    "type": "browser",
                    "rating": 4.8
                },
                {
                    "agent_id": "data_analyst",
                    "name": "Data Analyst Agent",
                    "description": "Analyzes data and generates insights",
                    "type": "rag",
                    "rating": 4.6
                }
            ],
            "total": 2,
            "error": str(e),
            "note": "Using fallback marketplace data"
        }

# Voice Cloning APIs

@app.post("/voice/clone")
async def clone_voice(
    voice_name: str,
    audio_samples: List[bytes],
    description: Optional[str] = None,
    user_id: str = "default"
):
    """Clone voice from audio samples"""
    try:
        result = voice_cloning.clone_voice(voice_name, audio_samples, description, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

@app.get("/voice/voices")
async def list_custom_voices(user_id: str = "default"):
    """List custom voices"""
    try:
        result = voice_cloning.list_custom_voices(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list custom voices: {str(e)}")

# Companion API endpoints (integrated into rag-api)
@app.get("/companion/check-keys")
async def check_companion_keys():
    """
    Diagnostic endpoint to check if companion API keys are set.
    Returns which keys are present/missing (without exposing values).
    """
    # Debug: Check environment variables
    dg_key = os.getenv("DEEPGRAM_API_KEY")
    eleven_key = os.getenv("ELEVENLABS_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Debug: Get all environment variable names (to see what Railway provides)
    all_env_keys = sorted([k for k in os.environ.keys() if "API" in k.upper() or "KEY" in k.upper()])
    
    # Check if deepgram package is installed
    deepgram_package_installed = False
    deepgram_import_error = None
    try:
        import deepgram
        deepgram_package_installed = True
        deepgram_version = getattr(deepgram, '__version__', 'unknown')
    except ImportError as e:
        deepgram_import_error = str(e)
        deepgram_version = None
    
    # Also check deepgram_sdk
    deepgram_sdk_installed = False
    try:
        import deepgram_sdk
        deepgram_sdk_installed = True
    except ImportError:
        pass
    
    keys_status = {
        "DEEPGRAM_API_KEY": "set" if dg_key else "missing",
        "ELEVENLABS_API_KEY": "set" if eleven_key else "missing",
        "OPENAI_API_KEY": "set" if openai_key else "missing",
    }
    
    # Debug: Check for common typos
    debug_info = {
        "deepgram_variants": {
            "DEEPGRAM_API_KEY": bool(os.getenv("DEEPGRAM_API_KEY")),
            "DEEPGRAM_API-KEY": bool(os.getenv("DEEPGRAM_API-KEY")),
            "deepgram_api_key": bool(os.getenv("deepgram_api_key")),
        },
        "elevenlabs_variants": {
            "ELEVENLABS_API_KEY": bool(os.getenv("ELEVENLABS_API_KEY")),
            "ELEVENLABS_API-KEY": bool(os.getenv("ELEVENLABS_API-KEY")),
            "elevenlabs_api_key": bool(os.getenv("elevenlabs_api_key")),
        },
        "all_api_env_vars": all_env_keys[:20],  # First 20 to avoid exposing too much
        "dg_key_length": len(dg_key) if dg_key else 0,
        "eleven_key_length": len(eleven_key) if eleven_key else 0,
        "openai_key_length": len(openai_key) if openai_key else 0,
        "deepgram_package": {
            "installed": deepgram_package_installed,
            "version": deepgram_version,
            "import_error": deepgram_import_error,
        },
        "deepgram_sdk_package": {
            "installed": deepgram_sdk_installed,
        },
        "companion_module_available": COMPANION_AVAILABLE,
    }
    
    all_set = all(status == "set" for status in keys_status.values())
    
    return {
        "status": "ok" if all_set else "missing_keys",
        "keys": keys_status,
        "companion_available": COMPANION_AVAILABLE,
        "message": "All keys set" if all_set else f"Missing keys: {', '.join([k for k, v in keys_status.items() if v == 'missing'])}",
        "debug": debug_info
    }

@app.post("/companion/session/create")
async def create_companion_session():
    """
    Create a new companion session.
    Returns session_id for WebSocket connection.
    """
    if not COMPANION_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Companion functionality not available. Missing dependencies: DEEPGRAM_API_KEY, ELEVENLABS_API_KEY, or companion modules."
        )
    
    # Check for required API keys before creating session
    missing_keys = []
    if not os.getenv("DEEPGRAM_API_KEY"):
        missing_keys.append("DEEPGRAM_API_KEY")
    if not os.getenv("ELEVENLABS_API_KEY"):
        missing_keys.append("ELEVENLABS_API_KEY")
    if not os.getenv("OPENAI_API_KEY"):
        missing_keys.append("OPENAI_API_KEY")
    
    if missing_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required API keys: {', '.join(missing_keys)}. Please add these environment variables to your Railway deployment. Check /companion/check-keys endpoint to verify which keys are set."
        )
    
    try:
        # Verify WebCompanion is available (not None)
        if WebCompanion is None:
            raise HTTPException(
                status_code=503,
                detail="WebCompanion class is not available. Check that companion_web module imported successfully."
            )
        
        session_id = str(uuid.uuid4())
        # Create new companion instance (WebSocket will be set when connection is established)
        print(f"[Companion] Creating new session: {session_id}")
        companion = WebCompanion(websocket=None)
        active_companion_sessions[session_id] = companion
        print(f"[Companion] Session created successfully: {session_id}")
        
        return {
            "session_id": session_id,
            "status": "created",
            "message": "Companion session created. Connect via WebSocket at /companion/ws/{session_id}"
        }
    except ValueError as e:
        # Missing API keys (fallback check)
        print(f"[Companion] ValueError creating session: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except TypeError as e:
        # NoneType is not callable - WebCompanion might be None
        print(f"[Companion] TypeError creating session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating companion session: {str(e)}. WebCompanion may not be properly imported."
        )
    except Exception as e:
        print(f"[Companion] Exception creating session: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating companion session: {str(e)}")

@app.get("/companion/memories")
async def get_companion_memories(session_id: str):
    """
    Get memory count for a companion session.
    Returns the number of memories associated with the session.
    """
    if session_id not in active_companion_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    companion = active_companion_sessions[session_id]
    
    try:
        # Get memory count from the companion's memory manager
        # MemoryManager has get_all_memories() method that returns a list
        memories = companion.memory.get_all_memories(limit=1000)  # Get up to 1000 memories
        count = len(memories) if memories else 0
        
        return {
            "session_id": session_id,
            "count": count,
            "status": "ok"
        }
    except Exception as e:
        print(f"[Companion] Error getting memories for session {session_id}: {e}")
        import traceback
        traceback.print_exc()
        # Return 0 if there's an error (non-blocking)
        return {
            "session_id": session_id,
            "count": 0,
            "status": "error",
            "message": str(e)
        }

@app.websocket("/companion/ws/{session_id}")
async def companion_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time companion interaction.
    Handles browser audio streams and streams back TTS audio.
    """
    await websocket.accept()
    
    if session_id not in active_companion_sessions:
        await websocket.send_json({
            "type": "error",
            "message": "Session not found. Create a session first via POST /companion/session/create"
        })
        await websocket.close()
        return
    
    companion = active_companion_sessions[session_id]
    companion.websocket = websocket  # Set WebSocket for companion
    companion_session_websockets[session_id] = websocket
    
    try:
        # Initialize Deepgram connection (now that WebSocket is set)
        await companion.initialize_deepgram()
        
        # Send session ready message
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session_id,
            "status": "connected"
        })
        
        # Start companion processing loop
        companion.processing_task = asyncio.create_task(companion.start_processing_loop())
        
        # Main message loop - receive audio/text from browser
        while True:
            try:
                # Receive message from browser
                data = await websocket.receive_json()
                msg_type = data.get("type")
                
                if msg_type == "audio_chunk":
                    # Browser sent audio chunk - forward to Deepgram
                    audio_data = data.get("audio", "")
                    if audio_data:
                        try:
                            print(f"[Companion WebSocket] Received audio_chunk message, data length: {len(audio_data)}")
                            # Decode base64 audio (Int16 PCM format)
                            audio_bytes = base64.b64decode(audio_data)
                            print(f"[Companion WebSocket] Decoded audio chunk: {len(audio_bytes)} bytes")
                            # Process audio chunk (send to Deepgram)
                            companion.process_audio_chunk(audio_bytes)
                        except Exception as e:
                            print(f"[Companion WebSocket] Error processing audio chunk: {e}")
                            import traceback
                            traceback.print_exc()
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Audio processing error: {str(e)}"
                            })
                    else:
                        print(f"[Companion WebSocket] Received audio_chunk message but audio_data is empty")
                
                elif msg_type == "text_input":
                    # Browser sent text input directly
                    text = data.get("text", "")
                    if text:
                        await companion.transcript_queue.put(text)
                
                elif msg_type == "interrupt":
                    # Browser requested interruption
                    if companion.current_playback_task and not companion.current_playback_task.done():
                        companion.current_playback_task.cancel()
                        await websocket.send_json({
                            "type": "interrupted",
                            "message": "AI response interrupted"
                        })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in companion WebSocket: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error: {str(e)}"
                })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Companion WebSocket error: {e}")
    finally:
        # Cleanup
        if companion.processing_task:
            companion.processing_task.cancel()
        if companion.dg_connection:
            try:
                companion.dg_connection.finish()
            except:
                pass
        if session_id in companion_session_websockets:
            del companion_session_websockets[session_id]
        if session_id in active_companion_sessions:
            del active_companion_sessions[session_id]

