"""
Password utilities for user authentication

This module provides utility functions for password hashing and validation
using bcrypt for secure password storage.
"""

import bcrypt
from typing import Optional
import logging

logger = logging.getLogger("sprintsync.password_utils")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Base64 encoded hash string
        
    Raises:
        ValueError: If password is empty or invalid
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    if len(password.strip()) == 0:
        raise ValueError("Password cannot be empty or whitespace only")
    
    try:
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise ValueError("Failed to hash password")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        
    Returns:
        bool: True if password matches, False otherwise
    """
    if not password or not password_hash:
        return False
    
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        logger.warning(f"Error verifying password: {str(e)}")
        return False


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    if not password:
        errors.append("Password is required")
        return False, errors
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters long")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    # Check for special characters
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def generate_temporary_password(length: int = 12) -> str:
    """
    Generate a temporary password
    
    Args:
        length: Length of the password (default 12)
        
    Returns:
        str: Generated password
    """
    import secrets
    import string
    
    # Ensure we have at least one of each character type
    lowercase = secrets.choice(string.ascii_lowercase)
    uppercase = secrets.choice(string.ascii_uppercase) 
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*")
    
    # Fill the rest with random characters
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    random_chars = ''.join(secrets.choice(all_chars) for _ in range(remaining_length))
    
    # Combine and shuffle
    password_list = list(lowercase + uppercase + digit + special + random_chars)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)
