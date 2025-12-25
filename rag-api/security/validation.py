"""
Input Validation and Sanitization

Provides utilities for validating and sanitizing user input.
"""

import re
from typing import Any, Optional
from html import escape
import bleach


def validate_input(
    value: Any,
    field_type: type = str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    required: bool = True
) -> Any:
    """
    Validate input value.
    
    Args:
        value: Value to validate
        field_type: Expected type
        min_length: Minimum length (for strings)
        max_length: Maximum length (for strings)
        pattern: Regex pattern to match
        required: Whether field is required
    
    Returns:
        Validated value
    
    Raises:
        ValueError if validation fails
    """
    if value is None:
        if required:
            raise ValueError("Field is required")
        return None
    
    # Type validation
    if not isinstance(value, field_type):
        try:
            value = field_type(value)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid type. Expected {field_type.__name__}")
    
    # String-specific validations
    if isinstance(value, str):
        if min_length is not None and len(value) < min_length:
            raise ValueError(f"Minimum length is {min_length}")
        
        if max_length is not None and len(value) > max_length:
            raise ValueError(f"Maximum length is {max_length}")
        
        if pattern and not re.match(pattern, value):
            raise ValueError(f"Value does not match required pattern")
    
    return value


def sanitize_input(value: str, allow_html: bool = False) -> str:
    """
    Sanitize string input to prevent XSS attacks.
    
    Args:
        value: String to sanitize
        allow_html: Whether to allow HTML tags (will be sanitized)
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    if allow_html:
        # Use bleach to sanitize HTML
        try:
            # Allow only safe tags and attributes
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
            allowed_attributes = {'a': ['href', 'title']}
            value = bleach.clean(
                value,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        except ImportError:
            # Fallback to HTML escaping if bleach not available
            value = escape(value)
    else:
        # Escape HTML entities
        value = escape(value)
    
    return value


def validate_email(email: str) -> str:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email address")
    return email


def validate_url(url: str) -> str:
    """Validate URL."""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        raise ValueError("Invalid URL")
    return url


def validate_uuid(uuid_string: str) -> str:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(pattern, uuid_string, re.IGNORECASE):
        raise ValueError("Invalid UUID format")
    return uuid_string


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal."""
    # Remove path components
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

