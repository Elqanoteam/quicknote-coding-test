"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class NoteCreate(BaseModel):
    """Schema for creating a new note."""
    title: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1, max_length=10000)


class TaskOut(BaseModel):
    """Schema for task output."""
    id: int
    text: str
    status: str


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    status: str = Field(pattern="^(open|done)$")


class NoteOut(BaseModel):
    """Schema for note output."""
    id: int
    title: str
    body: str
    summary: str
    tags: List[str]
    created_at: datetime
    tasks: List[TaskOut]
    similarity: Optional[float] = None

    class Config:
        from_attributes = True


class NotesSearchResponse(BaseModel):
    """Schema for notes search response."""
    notes: List[NoteOut]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = "ok"
