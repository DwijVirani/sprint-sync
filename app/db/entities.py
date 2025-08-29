from pydantic import BaseModel, Field

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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
    avatar: Mapped[str] = mapped_column(String)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

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
