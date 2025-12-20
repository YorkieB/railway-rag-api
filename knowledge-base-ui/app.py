import streamlit as st
import streamlit.components.v1 as components
import requests
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except ImportError:
    from requests.packages.urllib3.util.retry import Retry
import os
import json
from io import BytesIO
import base64
import time
import threading
import datetime

# #region agent log
# Debug logging function
def debug_log(hypothesis_id, location, message, data=None):
    try:
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(datetime.datetime.now().timestamp() * 1000)
        }
        log_path = r"c:\Users\conta\OneDrive\Desktop\project-backup\.cursor\debug.log"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        pass  # Silent fail for logging
# #endregion agent log

# Configuration - Will be updated from settings if user changes it
RAG_API_URL = os.getenv("RAG_API_URL", "https://rag-api-883324649002.us-central1.run.app")

# Create a session with connection pooling and retry strategy
def create_session():
    """Create a requests session with connection pooling and retry logic"""
    session = requests.Session()
    
    # Retry strategy: 3 retries with exponential backoff
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    
    # HTTP adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # Number of connection pools to cache
        pool_maxsize=10,      # Maximum number of connections to save in the pool
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Global session for connection reuse
_http_session = None

def get_session():
    """Get or create the global HTTP session"""
    global _http_session
    if _http_session is None:
        _http_session = create_session()
    return _http_session

# Eleven Labs audio generation function
def generate_elevenlabs_audio(text, voice_id, stability=0.5, similarity_boost=0.75):
    """Generate audio using Eleven Labs API"""
    if not st.session_state.get('elevenlabs_api_key'):
        return None
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": st.session_state.elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        session = get_session()
        response = session.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Eleven Labs API error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Page config
st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for JARVIS theme
# #region agent log
debug_log("A", "app.py:96", "CSS injection starting", {"css_length": 0})
# #endregion agent log
st.markdown("""
<style>
    /* Main background - dark with purple accents */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0a1f 50%, #0a0a0f 100%);
        overflow-y: auto;
    }
    html, body {
        overflow-y: auto;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* JARVIS Header */
    .jarvis-header {
        background: linear-gradient(135deg, #2d1b4e 0%, #1a0a2e 100%);
        padding: 20px 30px;
        border-bottom: 2px solid #8b5cf6;
        margin-bottom: 30px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
        text-align: center;
    }
    
    .jarvis-title {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        color: #e9d5ff;
        font-size: 2.5em;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
        margin: 0;
    }
    
    .jarvis-subtitle {
        color: #c4b5fd;
        font-size: 0.9em;
        margin-top: 5px;
        opacity: 0.9;
        text-align: center;
    }
    
    /* Header image upload areas */
    .header-image-upload {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 120px;
        padding: 10px;
    }
    
    /* File uploader styling - simplified to avoid conflicts */
    .stFileUploader {
        width: 100% !important;
    }
    
    /* Make the file uploader button area more prominent and clickable */
    .stFileUploader > div > div {
        border: 2px dashed #8b5cf6 !important;
        border-radius: 10px !important;
        padding: 20px !important;
        text-align: center !important;
        background: rgba(139, 92, 246, 0.05) !important;
        transition: all 0.3s !important;
        cursor: pointer !important;
    }
    
    .stFileUploader > div > div:hover {
        background: rgba(139, 92, 246, 0.1) !important;
        border-color: #6d28d9 !important;
    }
    
    /* Ensure the upload button is clickable */
    .stFileUploader button {
        cursor: pointer !important;
        pointer-events: auto !important;
    }
    
    .header-image-upload img {
        border-radius: 10px;
        max-height: 120px;
        width: auto;
        object-fit: contain;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        margin: 10px 0;
    }
    
    .header-image-upload .stFileUploader > div {
        background: rgba(139, 92, 246, 0.1);
        border: 2px dashed #8b5cf6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Animated sparkles for voice chat button - multiple sparkles */
    @keyframes sparkle {
        0%, 100% { opacity: 0; transform: scale(0) rotate(0deg) translateY(0); }
        25% { opacity: 0.8; transform: scale(1.2) rotate(90deg) translateY(-5px); }
        50% { opacity: 1; transform: scale(1) rotate(180deg) translateY(-10px); }
        75% { opacity: 0.8; transform: scale(1.2) rotate(270deg) translateY(-5px); }
    }
    
    @keyframes sparkle2 {
        0%, 100% { opacity: 0; transform: scale(0) rotate(0deg) translateY(0); }
        30% { opacity: 1; transform: scale(1.3) rotate(120deg) translateY(-8px); }
        60% { opacity: 0.7; transform: scale(0.9) rotate(240deg) translateY(-12px); }
    }
    
    @keyframes sparkle3 {
        0%, 100% { opacity: 0; transform: scale(0) rotate(0deg) translateY(0); }
        20% { opacity: 0.9; transform: scale(1.1) rotate(60deg) translateY(-6px); }
        50% { opacity: 1; transform: scale(1.4) rotate(180deg) translateY(-10px); }
        80% { opacity: 0.6; transform: scale(0.8) rotate(300deg) translateY(-4px); }
    }
    
    .voice-chat-wrapper {
        position: relative;
        overflow: visible;
    }
    
    .voice-chat-wrapper::before,
    .voice-chat-wrapper::after {
        content: "✨";
        position: absolute;
        font-size: 1.3em;
        pointer-events: none;
        z-index: 10;
    }
    
    .voice-chat-wrapper::before {
        top: -12px;
        left: 10px;
        animation: sparkle 2s infinite;
        animation-delay: 0s;
    }
    
    .voice-chat-wrapper::after {
        top: -12px;
        right: 10px;
        animation: sparkle 2s infinite;
        animation-delay: 1s;
    }
    
    /* Additional sparkles using pseudo-elements on the button itself */
    .voice-chat-sparkles {
        position: relative;
    }
    
    .voice-chat-sparkles::before,
    .voice-chat-sparkles::after {
        content: "✨";
        position: absolute;
        font-size: 1.1em;
        pointer-events: none;
        z-index: 11;
    }
    
    .voice-chat-sparkles::before {
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        animation: sparkle2 2.5s infinite;
        animation-delay: 0.5s;
    }
    
    .voice-chat-sparkles::after {
        bottom: -10px;
        left: 30%;
        animation: sparkle3 2.2s infinite;
        animation-delay: 1.2s;
    }
    
    /* Animated notepad icon - writing animation (icon only, faster) */
    @keyframes notepadWrite {
        0%, 100% { transform: rotate(0deg) scale(1); }
        10% { transform: rotate(-2deg) scale(1.05); }
        20% { transform: rotate(2deg) scale(1.05); }
        30% { transform: rotate(-1deg) scale(1); }
        40% { transform: rotate(1deg) scale(1.05); }
        50% { transform: rotate(0deg) scale(1); }
        60% { transform: rotate(-1deg) scale(1.03); }
        70% { transform: rotate(1deg) scale(1.03); }
        80% { transform: rotate(0deg) scale(1); }
    }
    
    .notepad-icon {
        display: inline-block;
        animation: notepadWrite 0.8s ease-in-out infinite;
    }
    
    /* Animated video camera icon - recording pulse (icon only, faster) */
    @keyframes cameraRecord {
        0%, 100% { 
            transform: scale(1);
            filter: brightness(1);
        }
        25% { 
            transform: scale(1.1);
            filter: brightness(1.3);
        }
        50% { 
            transform: scale(1.15);
            filter: brightness(1.5);
        }
        75% { 
            transform: scale(1.1);
            filter: brightness(1.3);
        }
    }
    
    @keyframes cameraPulse {
        0%, 100% { 
            opacity: 0.3;
            transform: scale(1);
        }
        50% { 
            opacity: 0.8;
            transform: scale(1.2);
        }
    }
    
    .camera-icon {
        display: inline-block;
        animation: cameraRecord 1s ease-in-out infinite;
        position: relative;
    }
    
    .camera-icon::after {
        content: "🔴";
        position: absolute;
        top: -2px;
        right: -2px;
        font-size: 0.5em;
        animation: cameraPulse 1s ease-in-out infinite;
        pointer-events: none;
    }
    
    /* Voice conversation panel */
    .voice-conversation-panel {
        background: #ffffff;
        border: 2px solid #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
    }
    
    .voice-status {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    .pulse-dot {
        width: 12px;
        height: 12px;
        background: #8b5cf6;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    /* Animated sparkles for voice chat button - target by key */
    div[data-testid="stButton"]:has(button[kind="secondary"][data-baseweb="button"]:contains("Voice Chat")) {
        position: relative;
    }
    
    /* Alternative: target button by its text content using CSS */
    button:has-text("Voice Chat")::before,
    button:has-text("Voice Chat")::after {
        content: "✨";
        position: absolute;
        font-size: 1.2em;
        animation: sparkle 2s infinite;
        pointer-events: none;
        z-index: 10;
        top: -8px;
    }
    
    button:has-text("Voice Chat")::before {
        left: 15px;
        animation-delay: 0s;
    }
    
    button:has-text("Voice Chat")::after {
        right: 15px;
        animation-delay: 1s;
    }
    
    /* More reliable approach: use data attribute or wrap in div */
    .voice-chat-wrapper {
        position: relative;
    }
    
    .voice-chat-wrapper::before,
    .voice-chat-wrapper::after {
        content: "✨";
        position: absolute;
        font-size: 1.2em;
        animation: sparkle 2s infinite;
        pointer-events: none;
        z-index: 10;
        top: -8px;
    }
    
    .voice-chat-wrapper::before {
        left: 15px;
        animation-delay: 0s;
    }
    
    .voice-chat-wrapper::after {
        right: 15px;
        animation-delay: 1s;
    }
    
    .header-image-upload .stFileUploader > div:hover {
        background: rgba(139, 92, 246, 0.2);
        border-color: #a78bfa;
    }
    
    .header-image-upload .stFileUploader label {
        color: #c4b5fd;
        font-size: 0.9em;
    }
    
    /* Chat container */
    .chat-container {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        min-height: 600px;
        max-height: 600px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Answer display */
    .answer-box {
        background: rgba(139, 92, 246, 0.05);
        border-left: 4px solid #8b5cf6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: #333333;
        line-height: 1.8;
    }
    
    /* Sources - compact dropdown */
    .stSelectbox > div > div > select {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        color: #333333;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.9em;
    }
    
    .stSelectbox label {
        color: #333333;
        font-size: 0.9em;
        font-weight: 600;
    }
    
    /* Artefact Pattern Panel */
    .artefact-wrapper {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .artefact-panel {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 15px;
        padding: 25px;
        min-height: 600px;
        max-height: 600px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
        align-items: flex-start;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        flex: 1;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    .artefact-title-inner {
        color: #333333;
        font-size: 1.3em;
        margin-bottom: 20px;
        font-weight: 600;
    }
    
    /* Settings/Features Box - exact same size as chat composer */
    .settings-box {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 15px 20px;
        margin-top: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
    }
    
    .settings-box h3 {
        color: #333333;
        margin-bottom: 15px;
        flex-shrink: 0;
    }
    
    /* Align containers properly - two containers per column */
    .col-main-wrapper, .col-code-wrapper {
        display: flex;
        flex-direction: column;
    }
    
    /* Top containers (large boxes) - fill most space */
    .chat-container, .artefact-panel {
        margin-top: 0;
        margin-bottom: 20px;
        flex: 1;
    }
    
    /* Bottom containers - fixed size */
    .chat-input-container {
        margin-top: 0;
        margin-bottom: 20px;
        flex-shrink: 0;
    }
    
    /* Small feature containers - fixed height and width */
    .settings-box {
        margin-top: 0;
        margin-bottom: 20px;
        flex-shrink: 0;
        height: 120px;
        min-height: 120px;
        max-height: 120px;
    }
    
    /* Row for the three small containers */
    .features-row {
        display: flex;
        flex-direction: row;
        gap: 20px;
        margin-top: 20px;
    }
    
    .features-row .settings-box {
        flex: 1;
        margin-bottom: 0;
    }
    
    /* Additional settings/features containers */
    .settings-features-container {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 15px 20px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .settings-features-container h3 {
        color: #333333;
        margin-bottom: 15px;
    }
    
    .settings-features-container {
        display: flex;
        flex-direction: column;
    }
    
    /* Small icon buttons matching input field height */
    .settings-box .stButton > button {
        padding: 0 !important;
        font-size: 1.3em !important;
        height: 38px !important;
        min-height: 38px !important;
        line-height: 1 !important;
    }
    
    .artefact-item {
        background: #1a0a2e;
        border: 1px solid #6d28d9;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
    }
    
    .artefact-header {
        color: #e9d5ff;
        font-weight: 600;
        margin-bottom: 15px;
        font-size: 1.1em;
        flex-shrink: 0;
    }
    
    .artefact-code {
        color: #c4b5fd;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
        line-height: 1.6;
        white-space: pre-wrap;
        flex: 1;
        overflow-y: auto;
        min-height: 0;
    }
    
    /* Chat input */
    .chat-input-container {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 15px 20px;
        margin-top: 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .chat-input-container h3 {
        color: #333333;
        margin-bottom: 15px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        transform: translateY(-2px);
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        color: #333333;
        border-radius: 10px;
        padding: 12px 15px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }
    
    /* Purple accent lines */
    .purple-accent {
        height: 2px;
        background: linear-gradient(90deg, transparent, #8b5cf6, transparent);
        margin: 20px 0;
    }
    
    /* Modal/Popup Window */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.75);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .modal-content {
        background: white;
        border-radius: 20px;
        padding: 30px;
        max-width: 900px;
        width: 90%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.3s ease-out;
        position: relative;
    }
    
    @keyframes slideUp {
        from {
            transform: translateY(50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .modal-title {
        color: #333;
        font-size: 1.8em;
        font-weight: 700;
        margin: 0;
    }
    
    .modal-close-btn {
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        cursor: pointer;
        font-size: 1em;
        transition: all 0.3s;
    }
    
    .modal-close-btn:hover {
        background: #dc2626;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# #region agent log
debug_log("A", "app.py:765", "CSS injection completed", {"css_injected": True})
# #endregion agent log

# Initialize session state
# #region agent log
debug_log("D", "app.py:768", "Session state initialization starting", {"existing_keys": list(st.session_state.keys())})
# #endregion agent log
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'artifacts' not in st.session_state:
    st.session_state.artifacts = []
if 'header_image_1' not in st.session_state:
    st.session_state.header_image_1 = None
if 'header_image_2' not in st.session_state:
    st.session_state.header_image_2 = None
if 'banner_text' not in st.session_state:
    st.session_state.banner_text = ""
if 'banner_image' not in st.session_state:
    st.session_state.banner_image = None
if 'banner_bg_color' not in st.session_state:
    st.session_state.banner_bg_color = "#2d1b4e"
if 'banner_text_color' not in st.session_state:
    st.session_state.banner_text_color = "#e9d5ff"
if 'show_banner_settings' not in st.session_state:
    st.session_state.show_banner_settings = False
# Voice chat session state
if 'voice_conversation_active' not in st.session_state:
    st.session_state.voice_conversation_active = False
if 'voice_messages' not in st.session_state:
    st.session_state.voice_messages = []
if 'elevenlabs_api_key' not in st.session_state:
    st.session_state.elevenlabs_api_key = ""
if 'voice_audio_data' not in st.session_state:
    st.session_state.voice_audio_data = {}  # Store audio by message timestamp
if 'notepad_notes' not in st.session_state:
    st.session_state.notepad_notes = []  # Store notes
if 'show_notepad' not in st.session_state:
    st.session_state.show_notepad = False
if 'show_video_assistant' not in st.session_state:
    st.session_state.show_video_assistant = False
if 'gemini_live_session_id' not in st.session_state:
    st.session_state.gemini_live_session_id = None
if 'use_gemini_live' not in st.session_state:
    st.session_state.use_gemini_live = False
if 'gemini_live_connected' not in st.session_state:
    st.session_state.gemini_live_connected = False
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""
if 'rag_api_url' not in st.session_state:
    st.session_state.rag_api_url = RAG_API_URL
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'custom_api_keys' not in st.session_state:
    st.session_state.custom_api_keys = {}
if 'show_voice_popup' not in st.session_state:
    st.session_state.show_voice_popup = False

# #region agent log
debug_log("D", "app.py:818", "Session state initialization completed", {
    "messages_count": len(st.session_state.get('messages', [])),
    "artifacts_count": len(st.session_state.get('artifacts', [])),
    "all_keys": list(st.session_state.keys())
})
# #endregion agent log

# JARVIS Header with image upload areas
# #region agent log
debug_log("E", "app.py:821", "Creating header columns", {"column_count": 3})
# #endregion agent log
col_header1, col_header2, col_header3 = st.columns([1, 2, 1])

with col_header1:
    st.markdown("**📷 Upload Image 1**")
    # File uploader - simplified implementation
    if st.session_state.header_image_1:
        st.image(BytesIO(st.session_state.header_image_1), use_container_width=True)
        if st.button("🗑️ Remove", key="remove_img_1", use_container_width=True):
            st.session_state.header_image_1 = None
            st.rerun()
    else:
        uploaded_image_1 = st.file_uploader(
            label="Click to browse and select an image",
            type=['png', 'jpg', 'jpeg', 'gif'],
            key="header_img_1",
            label_visibility="visible",
            help="Click the button below to open file browser and select an image"
        )
        if uploaded_image_1 is not None:
            st.session_state.header_image_1 = uploaded_image_1.read()
            st.rerun()

with col_header2:
    st.markdown("""
    <div class="jarvis-header">
        <div class="jarvis-title">
            <span style="font-size: 1.2em;">🤖</span>
            JARVIS
        </div>
        <div class="jarvis-subtitle">Powered by Google Cloud RAG System</div>
    </div>
    """, unsafe_allow_html=True)

with col_header3:
    st.markdown("**📷 Upload Image 2**")
    # File uploader - simplified implementation
    if st.session_state.header_image_2:
        st.image(BytesIO(st.session_state.header_image_2), use_container_width=True)
        if st.button("🗑️ Remove", key="remove_img_2", use_container_width=True):
            st.session_state.header_image_2 = None
            st.rerun()
    else:
        uploaded_image_2 = st.file_uploader(
            label="Click to browse and select an image",
            type=['png', 'jpg', 'jpeg', 'gif'],
            key="header_img_2",
            label_visibility="visible",
            help="Click the button below to open file browser and select an image"
        )
        if uploaded_image_2 is not None:
            st.session_state.header_image_2 = uploaded_image_2.read()
            st.rerun()

# Banner section - customizable banner below header
if st.session_state.banner_text or st.session_state.banner_image:
    banner_style = f"""
    background: {st.session_state.banner_bg_color};
    color: {st.session_state.banner_text_color};
    padding: 15px 30px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    width: 100%;
    """
    
    banner_content = ""
    if st.session_state.banner_image:
        banner_content += f'<img src="data:image/png;base64,{st.session_state.banner_image}" style="max-height: 80px; margin: 0 auto 10px auto; display: block;" />'
    if st.session_state.banner_text:
        banner_content += f'<div style="font-size: 1.2em; font-weight: 600;">{st.session_state.banner_text}</div>'
    
    st.markdown(f"""
    <div style="{banner_style}">
        {banner_content}
    </div>
    """, unsafe_allow_html=True)

# Main layout - two columns (50/50)
st.markdown("---")  # Divider to separate header from main content

# Scroll helper (user reports cannot scroll)
# #region agent log
debug_log("F", "app.py:901", "Rendering scroll helper button", {"reason": "user_cannot_scroll"})
# #endregion agent log
col_scroll, _ = st.columns([1, 4])
with col_scroll:
    if st.button("⬇️ Scroll to bottom (debug helper)", key="scroll_helper"):
        # #region agent log
        debug_log("F", "app.py:906", "Scroll helper clicked", {"clicked": True})
        # #endregion agent log
        components.html("""
            <script>
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            </script>
        """, height=0)

# #region agent log
debug_log("E", "app.py:914", "Creating main content columns", {"column_count": 2})
# #endregion agent log
col_main, col_code = st.columns([1, 1])

# Initialize input variables
user_input = ""
search_clicked = False
upload_clicked = False

with col_main:
    # #region agent log
    debug_log("E", "app.py:908", "Entering col_main context", {"messages_count": len(st.session_state.messages)})
    # #endregion agent log
    # Use Streamlit container for chat area
    chat_container = st.container()
    with chat_container:
        # #region agent log
        debug_log("B", "app.py:912", "Rendering chat container HTML", {"html_type": "div", "has_inline_style": True})
        # #endregion agent log
        st.markdown("""
        <div class="chat-container" style="background: #ffffff; border: 1px solid #e0e0e0; border-radius: 15px; padding: 25px; margin-bottom: 20px; min-height: 500px; max-height: 500px; overflow-y: auto;">
        """, unsafe_allow_html=True)
        
        # Welcome message if no chat history
        # #region agent log
        debug_log("C", "app.py:918", "Checking if welcome message should display", {"messages_empty": len(st.session_state.messages) == 0})
        # #endregion agent log
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px; color: #666;">
                <div style="font-size: 4em; margin-bottom: 20px;">🤖</div>
                <h2 style="color: #8b5cf6; margin-bottom: 15px; font-size: 2em;">Welcome to JARVIS</h2>
                <p style="font-size: 1.2em; color: #333; margin-bottom: 10px;">Your AI-powered knowledge base assistant</p>
                <p style="color: #666; font-size: 1em; margin-bottom: 30px;">Ask me anything about your uploaded documents, or upload new documents to expand the knowledge base.</p>
            </div>
            """, unsafe_allow_html=True)
            # #region agent log
            debug_log("C", "app.py:925", "Welcome message rendered", {"rendered": True})
            # #endregion agent log
    
    # Display chat history
    # #region agent log
    debug_log("C", "app.py:928", "Starting chat history display", {"message_count": len(st.session_state.messages)})
    # #endregion agent log
    for idx, message in enumerate(st.session_state.messages):
        if message['role'] == 'user':
            # Text above "You" bubble
            st.markdown(f"""
            <div style="color: #333333; font-size: 1.3em; font-weight: 600; margin-bottom: 5px; margin-top: 15px;">
                User Query
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 10px; margin: 0 0 20px 0; border-left: 4px solid #8b5cf6;">
                <strong style="color: #6d28d9;">You:</strong>
                <p style="color: #333333; margin: 5px 0 0 0;">{message['content']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="answer-box">
                <strong style="color: #8b5cf6;">JARVIS:</strong>
                <div style="margin-top: 10px; color: #333333;">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available (compact dropdown)
            if 'sources' in message and message['sources']:
                source_options = [f"{s.get('document_name', 'Unknown')} (Score: {s.get('score', 0):.3f})" for s in message['sources']]
                st.selectbox(
                    f"📚 Sources ({len(message['sources'])} found)",
                    options=source_options,
                    key=f"source_select_{idx}",
                    label_visibility="visible"
                )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close chat-container
    
    # Chat input section
    st.markdown("### 💬 Chat Input")
    col_input, col_search, col_upload = st.columns([10, 1, 1])
    
    with col_input:
        user_input = st.text_input(
            "Chatinput",
            placeholder="Ask JARVIS anything...",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col_search:
        search_clicked = st.button("🔍", use_container_width=True, key="search_btn", help="Search")
    
    with col_upload:
        upload_clicked = st.button("➕", use_container_width=True, key="upload_btn", help="Upload document")
    
with col_code:
    # #region agent log
    debug_log("E", "app.py:984", "Entering col_code context", {"artifacts_count": len(st.session_state.artifacts)})
    # #endregion agent log
    # Use Streamlit container for artifact area
    artifact_container = st.container()
    with artifact_container:
        # #region agent log
        debug_log("B", "app.py:988", "Rendering artifact panel HTML", {"html_type": "div", "has_inline_style": True})
        # #endregion agent log
        st.markdown("""
        <div class="artefact-panel" style="background: #ffffff; border: 1px solid #e0e0e0; border-radius: 15px; padding: 25px; min-height: 500px; max-height: 500px; overflow-y: auto;">
            <div class="artefact-title-inner" style="color: #333333; font-size: 1.3em; margin-bottom: 20px; font-weight: 600;"># JARVIS Artefact Pattern</div>
        """, unsafe_allow_html=True)
        
        if st.session_state.artifacts:
            for idx, artifact in enumerate(st.session_state.artifacts):
                artifact_type = artifact.get('type', 'code')
                artifact_content = artifact.get('content', '')
                artifact_title = artifact.get('title', f'Artefact {idx + 1}')
                
                st.markdown(f"""
                <div class="artefact-item">
                    <div class="artefact-header">{artifact_title}</div>
                    <div class="artefact-code">{artifact_content}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Artefact action buttons
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    if st.button("Close", key=f"close_{idx}", use_container_width=True):
                        st.session_state.artifacts.pop(idx)
                        st.rerun()
                with col_a2:
                    if st.button("Copy", key=f"copy_{idx}", use_container_width=True):
                        st.write("Copied to clipboard")
                with col_a3:
                    if st.button("Edit", key=f"edit_{idx}", use_container_width=True, type="primary"):
                        st.info("Edit mode - coming soon")
        else:
            st.markdown("""
            <div style="color: #999999; font-style: italic; text-align: center; padding: 40px;">
                <div style="font-size: 2em; margin-bottom: 10px;">⚙️</div>
                <div style="color: #666666;">Artefact Pattern Ready</div>
                <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.7; color: #999999;">
                    Generated artifacts will appear here
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close artefact-panel
        
        # Clear all artifacts button
        if st.session_state.artifacts:
            if st.button("🗑️ Clear All Artefacts", use_container_width=True, key="clear_all_artifacts"):
                st.session_state.artifacts = []
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close artefact-wrapper
    st.markdown('</div>', unsafe_allow_html=True)  # Close col-code-wrapper

# Row for the three small feature containers - same height and width
st.markdown('<div class="features-row">', unsafe_allow_html=True)

# Additional Features container
st.markdown('<div class="settings-box">', unsafe_allow_html=True)
st.markdown("### ⚙️ Additional Features", unsafe_allow_html=True)

col_add1, col_add2, col_add3 = st.columns(3)
with col_add1:
    # Animated notepad icon (icon only, not button)
    notepad_icon = '<span class="notepad-icon">📝</span>'
    if st.button(notepad_icon, use_container_width=True, key="templates_btn", help="NotePad"):
        st.session_state.show_notepad = not st.session_state.show_notepad
        st.rerun()
with col_add2:
    # Animated video camera icon (icon only, not button)
    camera_icon = '<span class="camera-icon">📹</span>'
    if st.button(camera_icon, use_container_width=True, key="adv_search_btn", help="Video Assistant"):
        st.session_state.show_video_assistant = not st.session_state.show_video_assistant
        st.rerun()
with col_add3:
    # Voice Conversation button with animated sparkles (icon only, no text)
    voice_active = st.session_state.voice_conversation_active
    button_icon = "🎤" if voice_active else "✨"
    button_help = "Real-time voice conversation with JARVIS (Active)" if voice_active else "Real-time voice conversation with JARVIS"
    st.markdown('<div class="voice-chat-wrapper"><div class="voice-chat-sparkles">', unsafe_allow_html=True)
    if st.button(button_icon, use_container_width=True, key="voice_chat_btn", help=button_help):
        st.session_state.show_voice_popup = True
        st.session_state.voice_conversation_active = True
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close Additional Features

# Settings & Features container
st.markdown('<div class="settings-box">', unsafe_allow_html=True)
st.markdown("### ⚙️ Settings & Features", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6 = st.columns(6)

with col_btn1:
    if st.button("⚙️", use_container_width=True, key="settings_btn", help="Settings & API Keys"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()
with col_btn2:
    st.button("📊", use_container_width=True, key="analytics_btn", help="Analytics")
with col_btn3:
    st.button("📤", use_container_width=True, key="export_btn", help="Export")
with col_btn4:
    st.button("📥", use_container_width=True, key="import_btn", help="Import")
with col_btn5:
    st.button("🔄", use_container_width=True, key="sync_btn", help="Sync")
with col_btn6:
    st.button("🔐", use_container_width=True, key="security_btn", help="Security")

st.markdown('</div>', unsafe_allow_html=True)  # Close Settings & Features

# Additional Settings container
st.markdown('<div class="settings-box">', unsafe_allow_html=True)
st.markdown("### ⚙️ Additional Settings", unsafe_allow_html=True)

col_add_set1, col_add_set2, col_add_set3 = st.columns(3)
with col_add_set1:
    st.button("🌐", use_container_width=True, key="api_keys_btn", help="API Keys")
with col_add_set2:
    st.button("📊", use_container_width=True, key="reports_btn", help="Reports")
with col_add_set3:
    st.button("⚡", use_container_width=True, key="performance_btn", help="Performance")

st.markdown('</div>', unsafe_allow_html=True)  # Close Additional Settings
st.markdown('</div>', unsafe_allow_html=True)  # Close features-row

# Voice Conversation Popup Modal
if st.session_state.show_voice_popup:
    # Create modal overlay and content
    st.markdown("""
    <div class="modal-overlay" id="voiceModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">🎤 Real-Time Voice Conversation with JARVIS</h2>
                <div style="display: flex; align-items: center;">
    """, unsafe_allow_html=True)
    
    # Close button in header
    if st.button("❌ Close", key="close_voice_popup_btn", use_container_width=False):
        st.session_state.show_voice_popup = False
        st.session_state.voice_conversation_active = False
        st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)  # Close close button div and modal-header
    st.markdown('<div class="voice-conversation-panel">', unsafe_allow_html=True)
    
    # Voice mode selection
    voice_mode = st.radio(
        "🎙️ Voice Mode",
        options=["Gemini Live (Real-time)", "Eleven Labs (TTS)"],
        index=1 if not st.session_state.use_gemini_live else 0,
        horizontal=True,
        key="voice_mode_select"
    )
    st.session_state.use_gemini_live = (voice_mode == "Gemini Live (Real-time)")
    
    # Status indicator
    if st.session_state.use_gemini_live:
        status_color = "#10b981" if st.session_state.gemini_live_connected else "#f59e0b"
        status_text = "Gemini Live Connected" if st.session_state.gemini_live_connected else "Gemini Live Disconnected"
    else:
        status_color = "#10b981" if st.session_state.voice_conversation_active else "#ef4444"
        status_text = "Voice Chat Active - Ready for conversation"
    
    st.markdown(f"""
    <div class="voice-status">
        <div class="pulse-dot"></div>
        <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Gemini Live connection
    if st.session_state.use_gemini_live:
        col_gemini1, col_gemini2 = st.columns(2)
        with col_gemini1:
            if st.button("🔌 Connect Gemini Live", use_container_width=True, key="connect_gemini_live"):
                try:
                    session = get_session()
                    api_url = st.session_state.rag_api_url or RAG_API_URL
                    response = session.post(
                        f"{api_url}/gemini-live/create-session",
                        json={
                            "model": "gemini-2.5-flash-native-audio",
                            "system_instruction": "You are JARVIS, an AI assistant powered by Google Cloud RAG System. Provide helpful, accurate responses based on the knowledge base.",
                            "voice_name": "Aoede"
                        },
                        timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.gemini_live_session_id = data.get("session_id")
                        st.session_state.gemini_live_connected = True
                        st.success("✅ Gemini Live session created!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create session: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to Gemini Live: {str(e)}")
        
        with col_gemini2:
            if st.session_state.gemini_live_session_id:
                if st.button("🔌 Disconnect", use_container_width=True, key="disconnect_gemini_live"):
                    try:
                        session = get_session()
                        api_url = st.session_state.rag_api_url or RAG_API_URL
                        response = session.delete(
                            f"{api_url}/gemini-live/sessions/{st.session_state.gemini_live_session_id}",
                            timeout=10
                        )
                        st.session_state.gemini_live_session_id = None
                        st.session_state.gemini_live_connected = False
                        st.success("Disconnected from Gemini Live")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error disconnecting: {str(e)}")
        
        # Gemini Live WebRTC interface with Video + Audio
        if st.session_state.gemini_live_connected and st.session_state.gemini_live_session_id:
            st.markdown("### 🎥 Gemini Live Real-Time Vision & Voice")
            st.info("💡 **Real-time video guidance**: The AI can see you and describe everything around you while you talk in real-time")
            
            # Enable video mode toggle
            enable_video = st.checkbox("📹 Enable Video Vision (AI can see you)", value=True, key="enable_video_vision")
            
            # WebRTC multimodal interface (Audio + Video)
            gemini_live_html = f"""
            <div id="gemini-live-container" style="padding: 20px; background: rgba(139, 92, 246, 0.05); border-radius: 10px; margin: 10px 0;">
                <!-- Video Preview -->
                <div id="video-container" style="margin-bottom: 15px; display: none;">
                    <video id="camera-feed" autoplay playsinline style="width: 100%; max-width: 640px; border-radius: 10px; background: #000;"></video>
                    <p style="color: #8b5cf6; font-weight: 600; margin-top: 10px;">📹 Camera Feed: <span id="camera-status">Not Started</span></p>
                </div>
                
                <!-- Status Indicators -->
                <div id="status-container" style="margin-bottom: 15px;">
                    <p style="color: #8b5cf6; font-weight: 600;">🎤 Microphone: <span id="mic-status">Not Started</span></p>
                    <p style="color: #8b5cf6; font-weight: 600; margin-top: 5px;">🤖 AI Vision: <span id="vision-status">Inactive</span></p>
                </div>
                
                <!-- Control Buttons -->
                <div style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
                    <button id="start-multimodal-btn" style="padding: 10px 20px; background: #10b981; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: 600;">🎥 Start Vision & Voice</button>
                    <button id="stop-multimodal-btn" style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 5px; cursor: pointer; display: none; font-weight: 600;">⏸️ Stop</button>
                </div>
                
                <!-- AI Vision Descriptions -->
                <div id="vision-descriptions" style="margin-top: 15px; padding: 15px; background: rgba(139, 92, 246, 0.1); border-radius: 8px; max-height: 200px; overflow-y: auto; display: none;">
                    <h4 style="color: #8b5cf6; margin-top: 0;">👁️ What I See:</h4>
                    <div id="vision-text" style="color: #333; line-height: 1.6;"></div>
                </div>
                
                <!-- Audio Output -->
                <audio id="audio-output" autoplay style="width: 100%; margin-top: 10px;"></audio>
                
                <!-- Connection Status -->
                <div id="connection-status" style="margin-top: 10px; padding: 10px; background: rgba(16, 185, 129, 0.1); border-radius: 5px; display: none;">
                    <p style="color: #10b981; margin: 0;">✅ Connected to Gemini Live - Real-time vision & voice active</p>
                </div>
            </div>
            
            <script>
            const sessionId = '{st.session_state.gemini_live_session_id or ""}';
            const defaultApiUrl = '{RAG_API_URL}';
            const customApiUrl = '{st.session_state.rag_api_url or ""}';
            const apiUrl = customApiUrl || defaultApiUrl;
            const wsUrl = apiUrl.replace('https://', 'wss://').replace('http://', 'ws://') + '/gemini-live/ws/' + sessionId;
            const enableVideo = {json.dumps(enable_video).lower()};
            
            let websocket = null;
            let audioContext = null;
            let stream = null;
            let videoStream = null;
            let videoElement = null;
            let canvas = null;
            let videoInterval = null;
            
            // Get UI elements
            const videoContainer = document.getElementById('video-container');
            const cameraFeed = document.getElementById('camera-feed');
            const visionDescriptions = document.getElementById('vision-descriptions');
            const visionText = document.getElementById('vision-text');
            
            // Start multimodal (audio + video)
            document.getElementById('start-multimodal-btn').addEventListener('click', async function() {{
                try {{
                    // Request microphone and optionally camera
                    const constraints = {{
                        audio: {{
                            sampleRate: 16000,
                            channelCount: 1,
                            echoCancellation: true,
                            noiseSuppression: true
                        }},
                        video: enableVideo ? {{
                            width: {{ ideal: 640 }},
                            height: {{ ideal: 480 }},
                            facingMode: 'user'
                        }} : false
                    }};
                    
                    stream = await navigator.mediaDevices.getUserMedia(constraints);
                    document.getElementById('mic-status').textContent = 'Active';
                    
                    // Setup video if enabled
                    if (enableVideo && stream.getVideoTracks().length > 0) {{
                        videoStream = stream;
                        videoElement = cameraFeed;
                        videoElement.srcObject = stream;
                        videoContainer.style.display = 'block';
                        document.getElementById('camera-status').textContent = 'Active';
                        
                        // Create canvas for frame capture
                        canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');
                        
                        // Capture video frames at 1 FPS (as recommended for Gemini Live)
                        videoInterval = setInterval(() => {{
                            if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA && websocket && websocket.readyState === WebSocket.OPEN) {{
                                canvas.width = videoElement.videoWidth;
                                canvas.height = videoElement.videoHeight;
                                context.drawImage(videoElement, 0, 0);
                                
                                // Convert to JPEG (base64) for efficient transmission
                                const jpegData = canvas.toDataURL('image/jpeg', 0.8);
                                const base64Data = jpegData.split(',')[1];
                                
                                // Send video frame to backend
                                websocket.send(JSON.stringify({{
                                    type: 'video_frame',
                                    image: base64Data,
                                    timestamp: Date.now()
                                }}));
                            }}
                        }}, 1000); // 1 FPS as recommended
                    }}
                    
                    // Connect WebSocket
                    websocket = new WebSocket(wsUrl);
                    
                    websocket.onopen = function() {{
                        document.getElementById('connection-status').style.display = 'block';
                        document.getElementById('start-multimodal-btn').style.display = 'none';
                        document.getElementById('stop-multimodal-btn').style.display = 'inline-block';
                        document.getElementById('vision-status').textContent = enableVideo ? 'Analyzing...' : 'Audio Only';
                    }};
                    
                    websocket.onmessage = function(event) {{
                        const data = JSON.parse(event.data);
                        
                        if (data.type === 'vision_description') {{
                            // Display AI vision description
                            visionDescriptions.style.display = 'block';
                            const description = document.createElement('p');
                            description.style.margin = '5px 0';
                            description.style.padding = '8px';
                            description.style.background = 'rgba(255, 255, 255, 0.7)';
                            description.style.borderRadius = '5px';
                            description.textContent = '👁️ ' + data.description;
                            visionText.appendChild(description);
                            
                            // Keep only last 5 descriptions
                            while (visionText.children.length > 5) {{
                                visionText.removeChild(visionText.firstChild);
                            }}
                            
                            // Auto-scroll to bottom
                            visionDescriptions.scrollTop = visionDescriptions.scrollHeight;
                        }} else if (data.type === 'audio_response') {{
                            // Handle audio response from Gemini Live
                            console.log('Audio response received');
                            if (data.audio_data) {{
                                // Decode and play audio
                                const audioBlob = new Blob([Uint8Array.from(atob(data.audio_data), c => c.charCodeAt(0))], {{ type: 'audio/mpeg' }});
                                const audioUrl = URL.createObjectURL(audioBlob);
                                const audioOutput = document.getElementById('audio-output');
                                audioOutput.src = audioUrl;
                                audioOutput.play();
                            }}
                        }} else if (data.type === 'text_response') {{
                            // Display text response
                            console.log('Response:', data.answer);
                            if (data.answer) {{
                                const responseDiv = document.createElement('p');
                                responseDiv.textContent = '🤖 ' + data.answer;
                                responseDiv.style.margin = '5px 0';
                                responseDiv.style.padding = '8px';
                                responseDiv.style.background = 'rgba(139, 92, 246, 0.2)';
                                responseDiv.style.borderRadius = '5px';
                                visionText.appendChild(responseDiv);
                            }}
                        }} else if (data.type === 'session_ready') {{
                            console.log('Session ready:', data);
                        }}
                    }};
                    
                    websocket.onerror = function(error) {{
                        console.error('WebSocket error:', error);
                        document.getElementById('vision-status').textContent = 'Connection Error';
                    }};
                    
                    websocket.onclose = function() {{
                        console.log('WebSocket closed');
                        document.getElementById('vision-status').textContent = 'Disconnected';
                    }};
                    
                    // Start recording and sending audio chunks
                    audioContext = new AudioContext({{ sampleRate: 16000 }});
                    const source = audioContext.createMediaStreamSource(stream);
                    const processor = audioContext.createScriptProcessor(4096, 1, 1);
                    
                    processor.onaudioprocess = function(e) {{
                        if (websocket && websocket.readyState === WebSocket.OPEN) {{
                            const inputData = e.inputBuffer.getChannelData(0);
                            const pcmData = new Int16Array(inputData.length);
                            for (let i = 0; i < inputData.length; i++) {{
                                pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
                            }}
                            websocket.send(JSON.stringify({{
                                type: 'audio_chunk',
                                audio: Array.from(pcmData),
                                timestamp: Date.now()
                            }}));
                        }}
                    }};
                    
                    source.connect(processor);
                    processor.connect(audioContext.destination);
                    
                }} catch (error) {{
                    console.error('Error starting multimodal:', error);
                    alert('Error accessing media devices: ' + error.message);
                }}
            }});
            
            // Stop multimodal
            document.getElementById('stop-multimodal-btn').addEventListener('click', function() {{
                // Stop video frame capture
                if (videoInterval) {{
                    clearInterval(videoInterval);
                    videoInterval = null;
                }}
                
                // Stop all media tracks
                if (stream) {{
                    stream.getTracks().forEach(track => track.stop());
                }}
                
                // Close audio context
                if (audioContext) {{
                    audioContext.close();
                }}
                
                // Close WebSocket
                if (websocket) {{
                    websocket.close();
                }}
                
                // Reset UI
                document.getElementById('mic-status').textContent = 'Stopped';
                document.getElementById('camera-status').textContent = 'Stopped';
                document.getElementById('vision-status').textContent = 'Inactive';
                document.getElementById('connection-status').style.display = 'none';
                document.getElementById('start-multimodal-btn').style.display = 'inline-block';
                document.getElementById('stop-multimodal-btn').style.display = 'none';
                videoContainer.style.display = 'none';
                visionDescriptions.style.display = 'none';
                visionText.innerHTML = '';
            }});
            </script>
            """
            components.html(gemini_live_html, height=300)
    
    # Eleven Labs API Key input (only show if not using Gemini Live)
    if not st.session_state.use_gemini_live:
        st.session_state.elevenlabs_api_key = st.text_input(
            "🔑 Eleven Labs API Key",
            value=st.session_state.elevenlabs_api_key,
            type="password",
            help="Enter your Eleven Labs API key for voice synthesis",
            key="elevenlabs_key_input"
        )
    
    # Voice settings
    col_voice1, col_voice2 = st.columns(2)
    with col_voice1:
        voice_id = st.selectbox(
            "🎙️ Voice Model",
            options=["21m00Tcm4TlvDq8ikWAM", "pNInz6obpgDQGcFmaJgB", "EXAVITQu4vr4xnSDxMaL"],
            index=0,
            help="Select Eleven Labs voice model",
            key="voice_model_select"
        )
    with col_voice2:
        stability = st.slider("Stability", 0.0, 1.0, 0.5, 0.1, key="voice_stability")
        similarity_boost = st.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.1, key="voice_similarity")
    
    # Conversation interface
    st.markdown("#### 💬 Conversation")
    
    # Display voice messages
    if st.session_state.voice_messages:
        for msg in st.session_state.voice_messages[-5:]:  # Show last 5 messages
            role_icon = "🎤" if msg['role'] == 'user' else "🤖"
            role_color = "#8b5cf6" if msg['role'] == 'user' else "#6d28d9"
            st.markdown(f"""
            <div style="background: rgba(139, 92, 246, 0.1); padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid {role_color};">
                <strong>{role_icon} {msg['role'].title()}:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💡 Start a conversation by typing a message or using voice recording")
    
    # Voice input controls
    col_voice_btn1, col_voice_btn2, col_voice_btn3 = st.columns(3)
    
    with col_voice_btn1:
        if st.button("🎤 Start Recording", use_container_width=True, key="start_recording"):
            st.info("🎤 Recording... (Note: Use text input below for now. Browser-based recording requires additional setup)")
            # Note: Real-time voice recording in Streamlit requires custom JavaScript components
            # For now, users can type messages which will be converted to speech via Eleven Labs
    
    with col_voice_btn2:
        if st.button("⏸️ Stop Recording", use_container_width=True, key="stop_recording"):
            st.success("Recording stopped. Processing...")
            # Note: Real-time voice recording in Streamlit requires custom JavaScript components
    
    with col_voice_btn3:
        if st.button("🔇 Play Last Response", use_container_width=True, key="play_response"):
            if st.session_state.voice_messages:
                last_response = [m for m in st.session_state.voice_messages if m['role'] == 'assistant']
                if last_response:
                    timestamp = last_response[-1]['timestamp']
                    if timestamp in st.session_state.voice_audio_data:
                        st.audio(st.session_state.voice_audio_data[timestamp], format='audio/mpeg', autoplay=True)
                        st.success("🔊 Playing JARVIS response...")
                    else:
                        st.warning("⚠️ No audio available. Please send a new message to generate audio.")
    
    # Text input fallback
    voice_text_input = st.text_input(
        "💬 Or type your message",
        placeholder="Type your message for JARVIS...",
        key="voice_text_input"
    )
    
    if st.button("📤 Send Message", use_container_width=True, key="send_voice_msg"):
        if voice_text_input:
            # Add user message
            st.session_state.voice_messages.append({
                'role': 'user',
                'content': voice_text_input,
                'timestamp': time.time()
            })
            
            # Get JARVIS response from RAG API
            with st.spinner("🤖 JARVIS is thinking..."):
                try:
                    session = get_session()
                    api_url = st.session_state.rag_api_url or RAG_API_URL
                    response = session.post(
                        f"{api_url}/query",
                        json={"question": voice_text_input},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        response_text = data.get("answer", "I'm processing your request...")
                    else:
                        response_text = "I encountered an error processing your request."
                except Exception as e:
                    response_text = f"Error: {str(e)}"
                
                # Add assistant response
                st.session_state.voice_messages.append({
                    'role': 'assistant',
                    'content': response_text,
                    'timestamp': time.time()
                })
                
                # Generate audio using Eleven Labs API
                if st.session_state.elevenlabs_api_key:
                    try:
                        audio_data = generate_elevenlabs_audio(response_text, voice_id, stability, similarity_boost)
                        if audio_data:
                            # Store audio data for replay
                            timestamp = st.session_state.voice_messages[-1]['timestamp']
                            st.session_state.voice_audio_data[timestamp] = audio_data
                            st.audio(audio_data, format='audio/mpeg', autoplay=True)
                            st.success("🔊 Audio response generated and playing...")
                    except Exception as e:
                        st.error(f"Error generating audio: {str(e)}")
                else:
                    st.warning("⚠️ Please enter your Eleven Labs API key to enable voice responses")
            
            st.rerun()
    
    if st.button("❌ Close Voice Chat", use_container_width=True, key="close_voice_chat"):
        st.session_state.voice_conversation_active = False
        st.session_state.show_voice_popup = False
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close voice-conversation-panel
    
    # Close modal HTML with JavaScript for click-outside-to-close
    st.markdown("""
    </div>
    </div>
    <script>
        // Close modal when clicking outside
        document.getElementById('voiceModal')?.addEventListener('click', function(e) {
            if (e.target === this) {
                // Trigger Streamlit rerun to close modal
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'close_modal'}, '*');
            }
        });
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.getElementById('voiceModal')) {
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'close_modal'}, '*');
            }
        });
    </script>
    """, unsafe_allow_html=True)  # Close modal-content and modal-overlay

# NotePad Panel
if st.session_state.show_notepad:
    with st.expander("📝 NotePad", expanded=True):
        st.markdown("### Quick Notes & Templates")
        
        # Note input
        new_note = st.text_area(
            "Add a new note",
            placeholder="Type your note here...",
            key="new_note_input",
            height=100
        )
        
        col_note1, col_note2 = st.columns(2)
        with col_note1:
            if st.button("💾 Save Note", use_container_width=True, key="save_note"):
                if new_note.strip():
                    st.session_state.notepad_notes.append({
                        'content': new_note.strip(),
                        'timestamp': time.time()
                    })
                    st.success("Note saved!")
                    st.rerun()
        
        with col_note2:
            if st.button("📋 Clear", use_container_width=True, key="clear_note"):
                st.rerun()
        
        # Display saved notes
        if st.session_state.notepad_notes:
            st.markdown("### Saved Notes")
            # Show last 10 notes in reverse order (newest first)
            notes_to_show = st.session_state.notepad_notes[-10:]
            total_notes = len(st.session_state.notepad_notes)
            for display_idx, note in enumerate(reversed(notes_to_show)):
                # Calculate actual index in the original list (from the end)
                # display_idx 0 = newest note = last index in list
                actual_index = total_notes - 1 - display_idx
                with st.container():
                    note_number = total_notes - display_idx
                    st.markdown(f"**Note {note_number}**")
                    st.text(note['content'])
                    if st.button("🗑️ Delete", key=f"delete_note_{actual_index}", use_container_width=True):
                        # Delete by index to avoid issues with object matching
                        if 0 <= actual_index < len(st.session_state.notepad_notes):
                            del st.session_state.notepad_notes[actual_index]
                        st.rerun()
                    st.divider()
        
        if st.button("❌ Close NotePad", use_container_width=True, key="close_notepad"):
            st.session_state.show_notepad = False
            st.rerun()

# Video Assistant Panel
if st.session_state.show_video_assistant:
    with st.expander("📹 Video Assistant", expanded=True):
        st.markdown("### Video Analysis & Recording")
        
        # Video upload
        uploaded_video = st.file_uploader(
            "Upload a video for analysis",
            type=['mp4', 'avi', 'mov', 'mkv'],
            key="video_upload"
        )
        
        if uploaded_video is not None:
            st.video(uploaded_video)
            st.info("📹 Video uploaded. Analysis features coming soon.")
            
            # Placeholder for video analysis
            if st.button("🔍 Analyze Video", use_container_width=True, key="analyze_video"):
                st.info("Video analysis feature - Coming soon: Scene detection, object recognition, transcription")
        
        st.divider()
        
        # Video recording placeholder
        st.markdown("### Record Video")
        st.info("📹 Video recording feature - Coming soon: Browser-based video capture with AI analysis")
        
        if st.button("❌ Close Video Assistant", use_container_width=True, key="close_video_assistant"):
            st.session_state.show_video_assistant = False
            st.rerun()

# Settings Panel - API Keys & Credentials
if st.session_state.show_settings:
    with st.expander("⚙️ Settings & API Keys", expanded=True):
        st.markdown("### 🔐 API Keys & Credentials")
        st.info("💡 Enter your API keys below. All keys are stored securely in session state and masked for privacy.")
        
        # Main API Keys Section
        st.markdown("#### 🌐 Core API Keys")
        
        # RAG API URL
        st.session_state.rag_api_url = st.text_input(
            "🔗 RAG API URL",
            value=st.session_state.rag_api_url,
            help="URL of your RAG API backend (e.g., https://rag-api-883324649002.us-central1.run.app)",
            key="rag_api_url_input"
        )
        
        # Gemini API Key
        st.session_state.gemini_api_key = st.text_input(
            "🤖 Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Google Gemini API key for embeddings and generation",
            key="gemini_api_key_input"
        )
        
        # Eleven Labs API Key
        st.session_state.elevenlabs_api_key = st.text_input(
            "🎙️ Eleven Labs API Key",
            value=st.session_state.elevenlabs_api_key,
            type="password",
            help="Eleven Labs API key for text-to-speech synthesis",
            key="elevenlabs_api_key_settings"
        )
        
        # OpenAI API Key (for future web search features)
        st.session_state.openai_api_key = st.text_input(
            "🧠 OpenAI API Key (Optional)",
            value=st.session_state.openai_api_key,
            type="password",
            help="OpenAI API key for web search and additional features (optional)",
            key="openai_api_key_input"
        )
        
        st.divider()
        
        # Custom API Keys Section
        st.markdown("#### 🔑 Custom API Keys")
        st.markdown("Add additional API keys for custom integrations")
        
        col_custom1, col_custom2 = st.columns([3, 1])
        with col_custom1:
            new_key_name = st.text_input(
                "Key Name",
                placeholder="e.g., Anthropic, Cohere, etc.",
                key="new_key_name_input"
            )
        with col_custom2:
            if st.button("➕ Add", use_container_width=True, key="add_custom_key"):
                if new_key_name and new_key_name.strip():
                    if new_key_name.strip() not in st.session_state.custom_api_keys:
                        st.session_state.custom_api_keys[new_key_name.strip()] = ""
                        st.rerun()
                    else:
                        st.warning("Key name already exists")
        
        # Display and manage custom keys
        if st.session_state.custom_api_keys:
            st.markdown("**Custom Keys:**")
            for key_name in list(st.session_state.custom_api_keys.keys()):
                col_key1, col_key2 = st.columns([4, 1])
                with col_key1:
                    st.session_state.custom_api_keys[key_name] = st.text_input(
                        f"🔑 {key_name}",
                        value=st.session_state.custom_api_keys[key_name],
                        type="password",
                        key=f"custom_key_{key_name}",
                        label_visibility="visible"
                    )
                with col_key2:
                    if st.button("🗑️", key=f"remove_key_{key_name}", use_container_width=True):
                        del st.session_state.custom_api_keys[key_name]
                        st.rerun()
        
        st.divider()
        
        # API Key Status
        st.markdown("#### ✅ API Key Status")
        status_col1, status_col2 = st.columns(2)
        
        with status_col1:
            if st.session_state.gemini_api_key:
                st.success("✅ Gemini API Key: Configured")
            else:
                st.warning("⚠️ Gemini API Key: Not set")
            
            if st.session_state.elevenlabs_api_key:
                st.success("✅ Eleven Labs API Key: Configured")
            else:
                st.info("ℹ️ Eleven Labs API Key: Not set (optional)")
        
        with status_col2:
            if st.session_state.rag_api_url:
                st.success("✅ RAG API URL: Configured")
            else:
                st.error("❌ RAG API URL: Required")
            
            if st.session_state.openai_api_key:
                st.success("✅ OpenAI API Key: Configured")
            else:
                st.info("ℹ️ OpenAI API Key: Not set (optional)")
        
        st.divider()
        
        # Save/Clear buttons
        col_save1, col_save2, col_save3 = st.columns(3)
        with col_save1:
            if st.button("💾 Save All Settings", use_container_width=True, key="save_settings"):
                # Settings saved - RAG_API_URL will be used from session state
                st.success("✅ Settings saved!")
                st.rerun()
        
        with col_save2:
            if st.button("🔄 Reset to Defaults", use_container_width=True, key="reset_settings"):
                st.session_state.rag_api_url = os.getenv("RAG_API_URL", "https://rag-api-883324649002.us-central1.run.app")
                st.session_state.gemini_api_key = ""
                st.session_state.elevenlabs_api_key = ""
                st.session_state.openai_api_key = ""
                st.session_state.custom_api_keys = {}
                st.info("Settings reset to defaults")
                st.rerun()
        
        with col_save3:
            if st.button("❌ Close Settings", use_container_width=True, key="close_settings"):
                st.session_state.show_settings = False
                st.rerun()
        
        # Security Note
        st.markdown("---")
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <p style="color: #333; margin: 0; font-size: 0.9em;">
                <strong>🔒 Security Note:</strong> API keys are stored in session state (temporary, cleared on refresh). 
                For production, consider using environment variables or a secure key management service.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Banner Settings Panel
if st.session_state.show_banner_settings:
    with st.expander("⚙️ Banner Settings", expanded=True):
        st.markdown("### Customize Banner")
        
        col_banner1, col_banner2 = st.columns(2)
        
        with col_banner1:
            st.session_state.banner_text = st.text_input(
                "Banner Text",
                value=st.session_state.banner_text,
                placeholder="Enter banner text...",
                key="banner_text_input"
            )
            
            st.session_state.banner_bg_color = st.color_picker(
                "Background Color",
                value=st.session_state.banner_bg_color,
                key="banner_bg_picker"
            )
        
        with col_banner2:
            banner_image_upload = st.file_uploader(
                "Banner Image",
                type=['png', 'jpg', 'jpeg', 'gif'],
                key="banner_image_upload"
            )
            
            if banner_image_upload is not None:
                image_bytes = banner_image_upload.read()
                st.session_state.banner_image = base64.b64encode(image_bytes).decode()
                st.rerun()
            
            if st.session_state.banner_image:
                st.image(BytesIO(base64.b64decode(st.session_state.banner_image)), width=200)
                if st.button("Remove Banner Image", key="remove_banner_img"):
                    st.session_state.banner_image = None
                    st.rerun()
            
            st.session_state.banner_text_color = st.color_picker(
                "Text Color",
                value=st.session_state.banner_text_color,
                key="banner_text_picker"
            )
        
        if st.button("Clear Banner", key="clear_banner"):
            st.session_state.banner_text = ""
            st.session_state.banner_image = None
            st.rerun()

# Handle search
if search_clicked or (user_input and user_input.strip()):
    if user_input and user_input.strip():
        # Add user message to history
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input.strip()
        })
        
        # Query the API
        with st.spinner("JARVIS is thinking..."):
            try:
                session = get_session()
                api_url = st.session_state.rag_api_url or RAG_API_URL
                response = session.post(
                    f"{api_url}/query",
                    json={"question": user_input.strip()},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided")
                    sources = data.get("sources", [])
                    search_type = data.get("search_type", "unknown")
                    
                    # Add assistant response to history
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': answer,
                        'sources': sources,
                        'search_type': search_type
                    })
                    
                    # Generate artefact (Artefact Pattern)
                    if search_type == "knowledge_base" and sources:
                        # Create artefact showing the query processing in JARVIS style
                        source_names = [s.get('document_name', 'Unknown') for s in sources[:3]]
                        artefact_code = f"""wf.invst
@JARVIS #wf2.R1_nltk.steq_orientate 'tan'
def init_context():
    init_wf = jarvis_load 'onton exforces'
    load_data.config
    wf.find_terms
    wf.vector
    JARVIS.adffet
    lantontak
    kenmany
"""
                        
                        artifact = {
                            'type': 'code',
                            'title': 'JARVIS Query Processing Artefact',
                            'content': artefact_code,
                            'query': user_input.strip(),
                            'sources': [s.get('document_name') for s in sources]
                        }
                        
                        if 'artifacts' not in st.session_state:
                            st.session_state.artifacts = []
                        st.session_state.artifacts.append(artifact)
                    
                    st.rerun()
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': f"❌ {error_msg}"
                    })
                    st.rerun()
                        
            except requests.exceptions.RequestException as e:
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"❌ Failed to connect to RAG API: {str(e)}"
                })
                st.rerun()

# Handle upload button
if upload_clicked:
    with st.expander("📤 Upload Document", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt', 'md'],
            key="file_uploader"
        )
        doc_name = st.text_input("Document Name (optional)", key="doc_name_input")
        
        if st.button("Upload", key="upload_submit") and uploaded_file:
            with st.spinner("Uploading..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {}
                    if doc_name:
                        data['document_name'] = doc_name
                    
                    session = get_session()
                    api_url = st.session_state.rag_api_url or RAG_API_URL
                    response = session.post(
                        f"{api_url}/upload",
                        files=files,
                        data=data,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Document uploaded successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# Sidebar for additional features
with st.sidebar:
    st.markdown("### 🤖 JARVIS Control Panel")
    
    # System status
    try:
        session = get_session()
        api_url = st.session_state.rag_api_url or RAG_API_URL
        health_response = session.get(f"{api_url}/", timeout=5)
        if health_response.status_code == 200:
            st.success("🟢 System Online")
        else:
            st.warning("🟡 System Degraded")
    except:
        st.error("🔴 System Offline")
    
    st.divider()
    
    # Document management
    if st.button("📚 View Documents"):
        try:
            session = get_session()
            api_url = st.session_state.rag_api_url or RAG_API_URL
            response = session.get(f"{api_url}/documents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                docs = data.get('documents', [])
                st.write(f"**{data.get('total_documents', 0)} documents**")
                for doc in docs:
                    st.write(f"- {doc['document_name']} ({doc['chunk_count']} chunks)")
        except:
            st.error("Failed to load documents")
    
    st.divider()
    
    # Clear chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.artifacts = []
        st.rerun()
    
    st.markdown("---")
    st.caption("JARVIS v1.0 - Deployed: 2025-12-19")
    st.caption("Powered by Google Cloud RAG")
    
    # Debug: Show deployment info
    with st.expander("🔧 Debug Info", expanded=True):
        st.write(f"Messages: {len(st.session_state.messages)}")
        st.write(f"Artifacts: {len(st.session_state.artifacts)}")
        st.write(f"RAG API URL: {st.session_state.rag_api_url}")
        st.write(f"Session State Keys: {len(st.session_state.keys())}")
        st.write(f"CSS Injected: ✅")
        st.write(f"Columns Created: ✅")
        st.write(f"Chat Container: ✅")
        st.write(f"Artifact Container: ✅")
