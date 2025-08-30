from typing import Any, Dict, Optional

from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session

from app.db.entities import User
from app.models.auth import TokenResponse
from app.repository.auth import AuthRepository
from app.utils.password import hash_password, validate_password_strength


class AuthController:
    def __init__(self, session: Session):
        self.session = session
        self.auth_repository: AuthRepository = AuthRepository(session)

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.auth_repository.get_user(user_id)

    def create_user(self, email: str, password: str, first_name: str, last_name: str, 
                   is_admin: bool = False, avatar: str = None) -> User:
        """
        Create a new user with password validation and hashing
        
        Args:
            email: User's email address
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            is_admin: Whether user has admin privileges
            avatar: Optional avatar URL
            
        Returns:
            User: Created user object
            
        Raises:
            HTTPException: If email exists or password is invalid
        """
        # Check if email already exists
        if self.auth_repository.email_exists(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password strength
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(errors)}"
            )
        
        # Create user with hashed password
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            avatar=avatar
        )
        
        # Set password (this will hash it automatically)
        user.set_password(password)
        
        # Save to database
        return self.auth_repository.create_user(user)

    def create_token(self, token_data: dict[str, Any]) -> TokenResponse:
        """Create JWT token for user"""
        return self.auth_repository.create_token(token_data)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User: Authenticated user or None if invalid
        """
        user = self.auth_repository.get_user_by_email(email)
        if user and user.verify_password(password):
            return user
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.auth_repository.get_user_by_email(email)