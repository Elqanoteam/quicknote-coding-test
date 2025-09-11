"""SQLModel database models for the notes copilot application."""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    pass


class Note(SQLModel, table=True):
    """Note model representing a user's note with AI-generated metadata."""

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500)
    body: str = Field(max_length=10000)
    summary: str = Field(max_length=1000)
    tags_json: str = Field(max_length=2000)  # JSON-encoded list[str]
    embedding_json: str = Field(max_length=50000)  # JSON-encoded list[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="note")


class Task(SQLModel, table=True):
    """Task model representing follow-up actions generated from notes."""

    id: Optional[int] = Field(default=None, primary_key=True)
    note_id: int = Field(foreign_key="note.id")
    text: str = Field(max_length=500)
    status: str = Field(default="open", max_length=20)  # 'open' | 'done'

    # Relationship to note
    note: Optional[Note] = Relationship(back_populates="tasks")
