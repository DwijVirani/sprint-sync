from typing import Any, Optional
import jwt
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import User
from app.models.auth import TokenResponse
from app.utils.config import Config

config = Config()

class AuthRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter(User.id == user_id).first()

    def create_user(self, user: User) -> User:
        """Create a new user"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def create_token(self, token_data: dict[str, Any]) -> TokenResponse:
        """Create JWT token for user"""
        # Add expiration and issued at timestamps
        token_payload = {
            **token_data,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        # Generate JWT token
        access_token = jwt.encode(token_payload, config.AUTH_SECRET_KEY, algorithm="HS256")
        
        # Return token response
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=token_data
        )

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.session.query(User).filter(User.email == email).first()

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.session.query(User).filter(User.email == email).first() is not None