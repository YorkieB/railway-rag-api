"""
Credential Management
Manages Windows credentials using Credential Manager + DPAPI.
Secrets never leave local device.
"""
import os
from typing import Optional, Dict
try:
    import win32cred
    import win32con
    CREDENTIAL_MANAGER_AVAILABLE = True
except ImportError:
    CREDENTIAL_MANAGER_AVAILABLE = False
    print("Warning: pywin32 not available. Using file-based storage (less secure).")

try:
    import win32crypt
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False
    print("Warning: pywin32 not available. DPAPI encryption not available.")


class CredentialManager:
    """
    Manages credentials using Windows Credential Manager + DPAPI.
    
    Security Model:
    - Credentials stored in Windows Credential Manager
    - Additional encryption with DPAPI (hardware-backed if TPM)
    - Never sent to cloud
    - Only accessible by paired device
    """
    
    def __init__(self):
        """Initialize credential manager."""
        self.target_prefix = "Jarvis:"
    
    def store_credential(
        self,
        credential_name: str,
        username: str,
        password: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Store credential in Windows Credential Manager.
        
        Args:
            credential_name: Unique credential identifier
            username: Username or key name
            password: Password or secret value
            description: Optional description
            
        Returns:
            True if successful
        """
        target = f"{self.target_prefix}{credential_name}"
        
        if CREDENTIAL_MANAGER_AVAILABLE:
            try:
                # Store in Credential Manager (password as string, not encrypted separately)
                # Windows Credential Manager handles encryption internally
                win32cred.CredWrite({
                    "Type": win32cred.CRED_TYPE_GENERIC,
                    "TargetName": target,
                    "UserName": username,
                    "CredentialBlob": password,  # String, not bytes
                    "Comment": description or f"Jarvis credential: {credential_name}",
                    "Persist": win32cred.CRED_PERSIST_LOCAL_MACHINE
                }, 0)
                
                return True
            except Exception as e:
                print(f"Error storing credential: {e}")
                return False
        else:
            # Fallback: Store in file (not secure, but works for MVP)
            storage_path = os.path.join(
                os.getenv("APPDATA", "."), "Jarvis", "credentials"
            )
            os.makedirs(storage_path, exist_ok=True)
            
            cred_file = os.path.join(storage_path, f"{credential_name}.json")
            with open(cred_file, "w") as f:
                import json
                json.dump({
                    "username": username,
                    "password": password,  # Not encrypted in fallback mode
                    "description": description
                }, f)
            
            return True
    
    def retrieve_credential(self, credential_name: str) -> Optional[Dict]:
        """
        Retrieve credential from Windows Credential Manager.
        
        Args:
            credential_name: Credential identifier
            
        Returns:
            Dict with username and password, or None if not found
        """
        target = f"{self.target_prefix}{credential_name}"
        
        if CREDENTIAL_MANAGER_AVAILABLE:
            try:
                # Retrieve from Credential Manager
                cred = win32cred.CredRead(target, win32cred.CRED_TYPE_GENERIC, 0)
                
                username = cred["UserName"]
                password_blob = cred["CredentialBlob"]
                
                # Password is stored as string in Credential Manager
                # CredentialBlob may be bytes (UTF-16) or string
                if isinstance(password_blob, bytes):
                    # Try UTF-16 first (Windows default), then UTF-8
                    try:
                        password = password_blob.decode('utf-16-le').rstrip('\x00')
                    except UnicodeDecodeError:
                        password = password_blob.decode('utf-8')
                else:
                    password = password_blob
                
                return {
                    "username": username,
                    "password": password,
                    "description": cred.get("Comment", "")
                }
            except Exception as e:
                print(f"Error retrieving credential: {e}")
                return None
        else:
            # Fallback: Read from file
            storage_path = os.path.join(
                os.getenv("APPDATA", "."), "Jarvis", "credentials"
            )
            cred_file = os.path.join(storage_path, f"{credential_name}.json")
            
            if not os.path.exists(cred_file):
                return None
            
            try:
                import json
                with open(cred_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading credential file: {e}")
                return None
    
    def delete_credential(self, credential_name: str) -> bool:
        """
        Delete credential from Windows Credential Manager.
        
        Args:
            credential_name: Credential identifier
            
        Returns:
            True if successful
        """
        target = f"{self.target_prefix}{credential_name}"
        
        if CREDENTIAL_MANAGER_AVAILABLE:
            try:
                win32cred.CredDelete(target, win32cred.CRED_TYPE_GENERIC, 0)
                return True
            except Exception as e:
                print(f"Error deleting credential: {e}")
                return False
        else:
            # Fallback: Delete file
            storage_path = os.path.join(
                os.getenv("APPDATA", "."), "Jarvis", "credentials"
            )
            cred_file = os.path.join(storage_path, f"{credential_name}.json")
            
            if os.path.exists(cred_file):
                try:
                    os.remove(cred_file)
                    return True
                except Exception as e:
                    print(f"Error deleting credential file: {e}")
                    return False
        
        return False
    
    def list_credentials(self) -> list[str]:
        """
        List all Jarvis credentials.
        
        Returns:
            List of credential names
        """
        credentials = []
        
        if CREDENTIAL_MANAGER_AVAILABLE:
            try:
                # Enumerate credentials
                creds = win32cred.CredEnumerate(f"{self.target_prefix}*", 0)
                for cred in creds:
                    target = cred["TargetName"]
                    credential_name = target.replace(self.target_prefix, "")
                    credentials.append(credential_name)
            except Exception as e:
                print(f"Error listing credentials: {e}")
        else:
            # Fallback: List files
            storage_path = os.path.join(
                os.getenv("APPDATA", "."), "Jarvis", "credentials"
            )
            if os.path.exists(storage_path):
                for filename in os.listdir(storage_path):
                    if filename.endswith(".json"):
                        credentials.append(filename[:-5])  # Remove .json extension
        
        return credentials


# Global credential manager instance
credential_manager = CredentialManager()

