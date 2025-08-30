"""
Authentication routes for SprintSync API

These routes provide user authentication, registration, and profile management.
"""

import traceback
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import jwt
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db.session import get_session
from app.utils.config import Config
from app.middleware.authorization import get_current_user, require_auth, require_admin
from app.controller.auth import AuthController

router = APIRouter(tags=["authentication"])
config = Config()

def get_controller(session: Session = Depends(get_session)):
    return AuthController(session=session)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    avatar: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserProfile(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    avatar: Optional[str] = None
    is_admin: bool = False

@router.post("/register", response_model=LoginResponse)
def register(request: RegisterRequest, controller: AuthController = Depends(get_controller)):
    """
    Register a new user
    
    Creates a new user account with secure password hashing and returns a JWT token.
    """
    try:
        # Create the user
        user = controller.create_user(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            avatar=request.avatar
        )
        
        # Generate token data
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.full_name,
            "is_admin": user.is_admin
        }
        
        # Create JWT token
        token = controller.create_token(token_data)
        
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            user=token.user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, controller: AuthController = Depends(get_controller)):
    """
    Login endpoint - authenticates user and returns JWT token
    
    Validates user credentials against the database and returns a JWT token if successful.
    """
    try:
        # Authenticate user
        user = controller.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Generate token data
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.full_name,
            "is_admin": user.is_admin
        }
        
        # Create JWT token
        token = controller.create_token(token_data)

        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            user=token.user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/profile", response_model=UserProfile)
def get_profile(request: Request, controller: AuthController = Depends(get_controller)):
    """
    Get current user profile - requires authentication
    
    This route is automatically protected by the JWT middleware
    if the path matches the protected_paths configuration.
    """
    user_data = get_current_user(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get full user details from database
    user = controller.get_user(int(user_data["user_id"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfile(
        user_id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        avatar=user.avatar,
        is_admin=user.is_admin
    )

@router.get("/protected")
def protected_route(user: dict = Depends(require_auth)):
    """
    Example protected route using the require_auth dependency
    """
    return {
        "message": f"Hello {user['email']}! This is a protected route.",
        "user_id": user["user_id"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/admin-only") 
def admin_only_route(admin: dict = Depends(require_admin)):
    """
    Example admin-only route using the require_admin dependency
    """
    return {
        "message": f"Hello admin {admin['email']}! This route requires admin privileges.",
        "admin_user_id": admin["user_id"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/public")
def public_route():
    """
    Public route that doesn't require authentication
    """
    return {
        "message": "This is a public route, no authentication required!",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/create-admin")
def create_admin_user(controller: AuthController = Depends(get_controller)):
    """
    Create an admin user for testing purposes
    
    This endpoint creates a default admin user if one doesn't exist.
    In production, this should be removed or secured.
    """
    try:
        # Check if admin already exists
        existing_admin = controller.get_user_by_email("admin@sprintsync.com")
        if existing_admin:
            return {"message": "Admin user already exists"}
        
        # Create admin user
        admin_user = controller.create_user(
            email="admin@sprintsync.com",
            password="Admin123!",
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        
        return {
            "message": "Admin user created successfully",
            "email": admin_user.email,
            "user_id": admin_user.id
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create admin user")
