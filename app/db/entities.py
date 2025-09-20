from typing import TypeVar

import bcrypt
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()

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
    current_organization_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("organizations.id"), nullable=True
    )

    def set_password(self, password: str) -> None:
        """
        Hash and set the user's password

        Args:
            password: Plain text password to hash and store
        """
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed.decode("utf-8")

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
            password_bytes = password.encode("utf-8")
            hash_bytes = self.password_hash.encode("utf-8")
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
            "is_admin": self.is_admin,
        }


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)


class UserOrganization(Base):
    __tablename__ = "user_organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id")
    )
    role: Mapped[str] = mapped_column(String, default="member")  # member, admin, owner
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class OrganizationConfig(Base):
    __tablename__ = "organization_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id")
    )
    config_key: Mapped[str] = mapped_column(String)
    config_value: Mapped[str] = mapped_column(String)


class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id")
    )
    name: Mapped[str] = mapped_column(
        String
    )  # e.g., "New", "In Progress", "Done", "QA"
    display_name: Mapped[str] = mapped_column(String)  # User-friendly name
    color: Mapped[str] = mapped_column(String, nullable=True)  # Hex color code for UI
    order_index: Mapped[int] = mapped_column(
        Integer, default=0
    )  # For ordering statuses
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Default status for new tasks


class TaskWorkflowTransition(Base):
    __tablename__ = "task_workflow_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id")
    )
    from_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_statuses.id"))
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_statuses.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


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
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_statuses.id"))
    priority: Mapped[str] = mapped_column(String)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    assigned_to: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organizations.id")
    )
    collaborators: Mapped[list[int]] = mapped_column(String, default=list)
    total_minutes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[list[str]] = mapped_column(String, default=list)
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)


class TaskStatusTransition(Base):
    __tablename__ = "task_status_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"))
    from_status_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("task_statuses.id"), nullable=True
    )
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_statuses.id"))
    changed_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    changed_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
