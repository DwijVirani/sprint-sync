from pydantic import BaseModel
import bcrypt

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from typing import TypeVar

Base=declarative_base()

T = TypeVar("T", bound=BaseModel)


def from_entity(entity: object, model_class: type[T]) -> T:
    """Convert SQLAlchemy entity to Pydantic model"""
    # Convert SQLAlchemy entity to dict, filtering only model fields
    data = {
        field: getattr(entity, field)
        for field in model_class.model_fields
        if hasattr(entity, field)
    }
    return model_class.model_validate(data)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)  # Store hashed password
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password
        
        Args:
            password: Plain text password to hash and store
        """
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
            
        try:
            password_bytes = password.encode('utf-8')
            hash_bytes = self.password_hash.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception:
            return False

    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding password hash)"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "avatar": self.avatar,
            "is_admin": self.is_admin
        }

class AiSuggestion(Base):
    __tablename__ = "ai_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    prompt: Mapped[str] = mapped_column(String)
    response: Mapped[str] = mapped_column(String)

class AiPrompts(Base):
    __tablename__ = "ai_prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    prompt: Mapped[str] = mapped_column(String)

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assigned_to: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    collaborators: Mapped[list[int]] = mapped_column(String, default=list)
    total_minutes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[list[str]] = mapped_column(String, default=list)
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)
