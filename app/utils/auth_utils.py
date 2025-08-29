import jwt
from typing import Optional, Dict, Any
from fastapi import Request
import logging

logger = logging.getLogger("sprintsync.auth")


def extract_user_from_jwt(token: str, secret_key: str = "your_auth_secret_key") -> Optional[Dict[str, Any]]:
    """Extract user information from JWT token."""
    try:
        # Decode JWT token
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return {
            "user_id": payload.get("user_id") or payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None
    except Exception as e:
        logger.warning(f"Failed to decode JWT token: {str(e)}")
        return None


async def extract_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request using various methods."""
    try:
        # Method 1: Check Authorization header for Bearer token
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user_info = extract_user_from_jwt(token)
            if user_info and user_info.get("user_id"):
                return str(user_info["user_id"])
        
        # Method 2: Check for user ID in request state (set by auth middleware)
        if hasattr(request.state, 'user_id'):
            return str(request.state.user_id)
        
        # Method 3: Check for user ID in request state under different name
        if hasattr(request.state, 'current_user'):
            user = request.state.current_user
            if hasattr(user, 'id'):
                return str(user.id)
            elif isinstance(user, dict) and 'id' in user:
                return str(user['id'])
        
        # Method 4: Check for API key or session-based auth
        api_key = request.headers.get("x-api-key")
        if api_key:
            # You could implement API key to user mapping here
            # For now, just return a placeholder
            return f"api_key_user_{api_key[:8]}"
            
    except Exception as e:
        logger.warning(f"Failed to extract user ID from request: {str(e)}")
    
    return None
