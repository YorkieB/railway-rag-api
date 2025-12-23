"""
Trust Boundaries and Security
Enforces security boundaries for Windows Companion.
"""
import os
from typing import Dict, Optional
from datetime import datetime, timedelta


class TrustBoundaries:
    """
    Manages trust boundaries for Windows Companion.
    
    Security Rules:
    - Credentials (passwords, API keys, tokens): Windows Credential Manager + DPAPI, never leave device
    - Session keys: In-memory only, cleared on logout, never persisted to cloud
    - Automation logs: Local SQLite (encrypted), sent to cloud only on explicit user export (redacted for PII)
    - Screenshots/recordings: Temp folder (auto-delete after 24h), never sent upstream unless user explicitly enables recording
    - Device certificate: Registry HKLM\\Software\\Jarvis, DPAPI-encrypted, revocation checked via cloud on each session
    """
    
    def __init__(self):
        """Initialize trust boundaries."""
        self.session_keys: Dict[str, bytes] = {}  # In-memory only
        self.temp_files: Dict[str, datetime] = {}  # Track temp files for auto-delete
        self.temp_dir = os.path.join(
            os.getenv("TEMP", "."), "Jarvis", "temp"
        )
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def create_session_key(self, session_id: str) -> bytes:
        """
        Create session key (in-memory only, never persisted).
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session key bytes
        """
        import secrets
        session_key = secrets.token_bytes(32)
        self.session_keys[session_id] = session_key
        return session_key
    
    def get_session_key(self, session_id: str) -> Optional[bytes]:
        """
        Get session key (in-memory only).
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session key bytes or None if not found
        """
        return self.session_keys.get(session_id)
    
    def clear_session_key(self, session_id: str) -> bool:
        """
        Clear session key (called on logout).
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        if session_id in self.session_keys:
            del self.session_keys[session_id]
            return True
        return False
    
    def clear_all_session_keys(self):
        """Clear all session keys (called on app shutdown)."""
        self.session_keys.clear()
    
    def create_temp_file(self, filename: str, content: bytes) -> str:
        """
        Create temporary file (auto-deleted after 24h).
        
        Args:
            filename: Filename
            content: File content
            
        Returns:
            Full path to temp file
        """
        filepath = os.path.join(self.temp_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        # Track for auto-delete
        self.temp_files[filepath] = datetime.now()
        
        return filepath
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up temporary files older than max_age_hours.
        
        Args:
            max_age_hours: Maximum age in hours (default: 24)
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        files_to_delete = []
        for filepath, created_at in self.temp_files.items():
            if created_at < cutoff:
                files_to_delete.append(filepath)
        
        for filepath in files_to_delete:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                del self.temp_files[filepath]
            except Exception as e:
                print(f"Error deleting temp file {filepath}: {e}")
    
    def should_send_to_cloud(self, data_type: str, user_consent: bool = False) -> bool:
        """
        Check if data should be sent to cloud based on trust boundaries.
        
        Args:
            data_type: Type of data (credentials, logs, screenshots, etc.)
            user_consent: Whether user explicitly consented
            
        Returns:
            True if data can be sent to cloud
        """
        # Never send credentials
        if data_type in ["credentials", "passwords", "api_keys", "tokens"]:
            return False
        
        # Never send session keys
        if data_type == "session_keys":
            return False
        
        # Screenshots/recordings: Only if user explicitly enables recording
        if data_type in ["screenshots", "recordings"]:
            return user_consent
        
        # Automation logs: Only on explicit export (redacted)
        if data_type == "automation_logs":
            return user_consent
        
        # Device certificate: Only status check, never full certificate
        if data_type == "device_certificate":
            return False  # Only status, not full cert
        
        # Other data: Default to allowed (with user consent)
        return user_consent
    
    def redact_sensitive_data(self, data: str) -> str:
        """
        Redact sensitive patterns from data before logging/export.
        
        Args:
            data: Data to redact
            
        Returns:
            Redacted data
        """
        import re
        
        # Redact API keys (match sk- or pk_ followed by at least 10 alphanumeric/underscore/hyphen chars)
        data = re.sub(r'sk-[A-Za-z0-9_-]{10,}', '[API_KEY_REDACTED]', data)
        data = re.sub(r'pk_[A-Za-z0-9_-]{10,}', '[API_KEY_REDACTED]', data)
        
        # Redact credit cards
        data = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]', data)
        
        # Redact SSNs
        data = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', data)
        
        # Redact passwords (basic pattern)
        data = re.sub(r'(password|pwd|passwd)\s*[:=]\s*[^\s]+', r'\1: [REDACTED]', data, flags=re.IGNORECASE)
        
        return data


# Global trust boundaries instance
trust_boundaries = TrustBoundaries()

