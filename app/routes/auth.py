"""
Authentication routes for SprintSync API

These routes demonstrate how to use the JWT authentication middleware
and provide endpoints for login, protected routes, etc.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from typing import Optional

from app.utils.config import Config
from app.middleware.authorization import get_current_user, require_auth, require_admin

router = APIRouter()
config = Config()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserProfile(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    is_admin: bool = False


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - generates JWT token
    
    In a real application, you would:
    1. Validate credentials against database
    2. Hash and compare passwords
    3. Return user data from database
    
    This is a demo implementation.
    """
    
    # Demo implementation - replace with real authentication
    if request.email == "admin@sprintsync.com" and request.password == "admin123":
        user_data = {
            "user_id": "1",
            "email": "admin@sprintsync.com",
            "name": "Admin User",
            "is_admin": True
        }
    elif request.email == "user@sprintsync.com" and request.password == "user123":
        user_data = {
            "user_id": "2", 
            "email": "user@sprintsync.com",
            "name": "Regular User",
            "is_admin": False
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {
        **user_data,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(token_data, config.AUTH_SECRET_KEY, algorithm="HS256")
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=user_data
    )


@router.get("/profile", response_model=UserProfile)
async def get_profile(request: Request):
    """
    Get current user profile - requires authentication
    
    This route is automatically protected by the JWT middleware
    if the path matches the protected_paths configuration.
    """
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserProfile(
        user_id=user["user_id"],
        email=user["email"], 
        name=user.get("name"),
        is_admin=user.get("is_admin", False)
    )


@router.get("/protected")
async def protected_route(user: dict = Depends(require_auth)):
    """
    Example protected route using the require_auth dependency
    """
    return {
        "message": f"Hello {user['email']}! This is a protected route.",
        "user_id": user["user_id"],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/admin-only") 
async def admin_only_route(admin: dict = Depends(require_admin)):
    """
    Example admin-only route using the require_admin dependency
    """
    return {
        "message": f"Hello admin {admin['email']}! This route requires admin privileges.",
        "admin_user_id": admin["user_id"],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/public")
async def public_route():
    """
    Public route that doesn't require authentication
    """
    return {
        "message": "This is a public route, no authentication required!",
        "timestamp": datetime.utcnow().isoformat()
    }
