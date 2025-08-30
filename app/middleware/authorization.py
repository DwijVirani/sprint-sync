"""
JWT Authentication Middleware for FastAPI

This middleware handles JWT token validation and user authentication
for protected routes in the SprintSync application.
"""

import jwt
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from app.utils.config import Config

logger = logging.getLogger("sprintsync.auth_middleware")
config = Config()


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware
    
    Validates JWT tokens from Authorization header and sets user context
    in request state for all routes except those explicitly excluded.
    
    By default, all routes require authentication except those listed in excluded_paths.
    The middleware extracts user information from JWT tokens and makes it available
    in request.state for use in route handlers.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        excluded_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.secret_key = secret_key or config.AUTH_SECRET_KEY
        self.algorithm = algorithm
        # Paths that don't require authentication
        self.excluded_paths = excluded_paths or [
            "/",
            "/health-check",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/create-admin",
            "/api/v1/auth/public"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and validate JWT if required"""
        
        # Check if path requires authentication
        if not self._requires_auth(request.url.path):
            return await call_next(request)
        
        # Extract and validate JWT token
        token = self._extract_token(request)
        if not token:
            return self._unauthorized_response("Missing authorization token")
        
        # Decode and validate token
        user_data = self._decode_token(token)
        if not user_data:
            return self._unauthorized_response("Invalid or expired token")
        
        # Set user context in request state
        request.state.current_user = user_data
        request.state.user_id = user_data.get("user_id") or user_data.get("sub")
        request.state.user_email = user_data.get("email")
        
        logger.info(f"Authenticated user {request.state.user_id} for {request.url.path}")
        
        # Continue with the request
        response = await call_next(request)
        return response

    def _requires_auth(self, path: str) -> bool:
        """Check if the given path requires authentication"""
        
        # Check excluded paths first (no auth required)
        for excluded_path in self.excluded_paths:
            # For exact matches or if path starts with excluded_path followed by '/' or end of string
            if path == excluded_path or (path.startswith(excluded_path) and 
                                       (len(path) == len(excluded_path) or path[len(excluded_path)] == '/')):
                return False
        
        # All other paths require authentication by default
        return True

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get("authorization")
        
        if not auth_header:
            return None
        
        # Support both "Bearer token" and "token" formats
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1]
        elif auth_header.startswith("bearer "):
            return auth_header.split(" ", 1)[1]
        else:
            # Assume the entire header is the token
            return auth_header

    def _decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Validate required fields
            if not payload.get("user_id") and not payload.get("sub"):
                logger.warning("JWT token missing user_id/sub field")
                return None
            
            # Return user data
            return {
                "user_id": payload.get("user_id") or payload.get("sub"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "is_admin": payload.get("is_admin", False),
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error decoding JWT token: {str(e)}")
            return None

    def _unauthorized_response(self, message: str) -> JSONResponse:
        """Return unauthorized response"""
        logger.warning(f"Unauthorized access attempt: {message}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "message": message,
                "code": "AUTH_001"
            }
        )


# Dependency function to get current user from request state
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Dependency function to get current authenticated user from request state
    
    Usage in FastAPI route:
    @app.get("/protected")
    async def protected_route(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return {"user": user}
    """
    if hasattr(request.state, 'current_user'):
        return request.state.current_user
    return None


def get_current_user_id(request: Request) -> Optional[str]:
    """
    Dependency function to get current user ID from request state
    
    Usage:
    @app.get("/my-data")
    async def get_my_data(request: Request):
        user_id = get_current_user_id(request)
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        # Use user_id to fetch user-specific data
    """
    if hasattr(request.state, 'user_id'):
        return str(request.state.user_id)
    return None


def require_auth(request: Request) -> Dict[str, Any]:
    """
    Dependency that raises HTTPException if user is not authenticated
    
    Usage:
    @app.get("/protected")
    async def protected_route(user: dict = Depends(require_auth)):
        return {"message": f"Hello {user['email']}"}
    """
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def require_admin(request: Request) -> Dict[str, Any]:
    """
    Dependency that requires admin privileges
    
    Usage:
    @app.delete("/admin/users/{user_id}")
    async def delete_user(user_id: int, admin: dict = Depends(require_admin)):
        # Only admins can access this endpoint
    """
    user = require_auth(request)
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user