"""
Device Pairing System
Implements Ed25519 key exchange + revocation model for secure device pairing.
"""
import os
import uuid
from typing import Optional, Dict
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import base64
import json

# For Windows DPAPI (will use pywin32 or ctypes)
try:
    import win32crypt
    import win32con
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False
    # Fallback: Use environment variable or file-based storage (less secure)
    print("Warning: pywin32 not available. Using file-based storage (less secure).")


class DevicePairing:
    """
    Manages device pairing with Ed25519 key exchange.
    
    Security Model:
    - Windows app generates local Ed25519 keypair
    - Cloud signs device certificate
    - Device certificate stored in Windows DPAPI (hardware-backed if TPM)
    - Revocation check on app startup: GET /api/devices/{device_id}/status
    - If revoked: Clear all local credentials and exit immediately (< 2 seconds)
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize device pairing system.
        
        Args:
            storage_path: Optional path for device storage (default: registry/DPAPI)
        """
        self.storage_path = storage_path or os.path.join(
            os.getenv("APPDATA", "."), "Jarvis", "devices"
        )
        os.makedirs(self.storage_path, exist_ok=True)
        
        # In-memory device registry (in production, use database)
        self.device_registry: Dict[str, Dict] = {}
    
    def generate_device_keypair(self) -> tuple[bytes, bytes]:
        """
        Generate Ed25519 keypair for device.
        
        Returns:
            Tuple of (private_key_bytes, public_key_bytes)
        """
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_key_bytes, public_key_bytes
    
    def store_device_key(self, device_id: str, private_key_bytes: bytes) -> bool:
        """
        Store device private key using Windows DPAPI.
        
        Args:
            device_id: Unique device identifier
            private_key_bytes: Private key bytes to store
            
        Returns:
            True if successful
        """
        if DPAPI_AVAILABLE:
            try:
                # Encrypt with DPAPI (hardware-backed if TPM available)
                # CRYPT_USERDATA = 0x01 (user data protection)
                encrypted = win32crypt.CryptProtectData(
                    private_key_bytes,
                    f"Jarvis Device Key {device_id}",
                    None,
                    None,
                    None,
                    0x01  # CRYPT_USERDATA flag
                )
                
                # Store in registry (HKLM\Software\Jarvis\Devices\{device_id})
                # For MVP: Store in file (production: use registry)
                key_path = os.path.join(self.storage_path, f"{device_id}.key")
                with open(key_path, "wb") as f:
                    f.write(encrypted)
                
                return True
            except Exception as e:
                print(f"Error storing device key with DPAPI: {e}")
                return False
        else:
            # Fallback: Store encrypted (less secure)
            key_path = os.path.join(self.storage_path, f"{device_id}.key")
            # Simple base64 encoding (not secure, but works for MVP)
            with open(key_path, "wb") as f:
                f.write(base64.b64encode(private_key_bytes))
            return True
    
    def load_device_key(self, device_id: str) -> Optional[bytes]:
        """
        Load device private key from Windows DPAPI.
        
        Args:
            device_id: Unique device identifier
            
        Returns:
            Private key bytes or None if not found
        """
        key_path = os.path.join(self.storage_path, f"{device_id}.key")
        
        if not os.path.exists(key_path):
            return None
        
        try:
            with open(key_path, "rb") as f:
                encrypted = f.read()
            
            if DPAPI_AVAILABLE:
                try:
                    # Decrypt with DPAPI (5th arg must be int, 0 = default flags)
                    decrypted, _ = win32crypt.CryptUnprotectData(
                        encrypted,
                        None,
                        None,
                        None,
                        0
                    )
                    return decrypted
                except Exception as e:
                    print(f"Error decrypting device key: {e}")
                    return None
            else:
                # Fallback: Decode base64
                return base64.b64decode(encrypted)
        except Exception as e:
            print(f"Error loading device key: {e}")
            return None
    
    def create_device_certificate(self, device_id: str, public_key_bytes: bytes) -> Dict:
        """
        Create device certificate (signed by cloud).
        
        Args:
            device_id: Unique device identifier
            public_key_bytes: Device public key
            
        Returns:
            Device certificate dict
        """
        certificate = {
            "device_id": device_id,
            "public_key": base64.b64encode(public_key_bytes).decode('utf-8'),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "signed_by": "jarvis-cloud"  # In production: actual signature
        }
        
        # Store in registry
        self.device_registry[device_id] = certificate
        
        return certificate
    
    def register_device(self, device_id: Optional[str] = None) -> Dict:
        """
        Register a new device.
        
        Args:
            device_id: Optional device ID (generated if not provided)
            
        Returns:
            Device registration response with certificate
        """
        if device_id is None:
            device_id = str(uuid.uuid4())
        
        # Generate keypair
        private_key_bytes, public_key_bytes = self.generate_device_keypair()
        
        # Store private key (DPAPI)
        if not self.store_device_key(device_id, private_key_bytes):
            raise Exception("Failed to store device key")
        
        # Create certificate
        certificate = self.create_device_certificate(device_id, public_key_bytes)
        
        return {
            "device_id": device_id,
            "certificate": certificate,
            "status": "registered",
            "message": "Device registered successfully. Store device_id securely."
        }
    
    def check_device_status(self, device_id: str) -> Dict:
        """
        Check device status (for revocation check).
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device status dict
        """
        if device_id not in self.device_registry:
            return {
                "device_id": device_id,
                "status": "not_found",
                "revoked": False
            }
        
        device = self.device_registry[device_id]
        
        return {
            "device_id": device_id,
            "status": device.get("status", "unknown"),
            "revoked": device.get("status") == "revoked",
            "created_at": device.get("created_at")
        }
    
    def revoke_device(self, device_id: str) -> bool:
        """
        Revoke a device (marks as revoked in registry).
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if successful
        """
        if device_id not in self.device_registry:
            return False
        
        self.device_registry[device_id]["status"] = "revoked"
        self.device_registry[device_id]["revoked_at"] = datetime.now().isoformat()
        
        return True
    
    def clear_device_credentials(self, device_id: str) -> bool:
        """
        Clear all local credentials for a device (called on revocation).
        
        Args:
            device_id: Device identifier
            
        Returns:
            True if successful
        """
        # Delete device key
        key_path = os.path.join(self.storage_path, f"{device_id}.key")
        if os.path.exists(key_path):
            try:
                os.remove(key_path)
            except Exception as e:
                print(f"Error deleting device key: {e}")
                return False
        
        # Clear from registry
        if device_id in self.device_registry:
            del self.device_registry[device_id]
        
        return True


# Global device pairing instance
device_pairing = DevicePairing()

