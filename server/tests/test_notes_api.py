"""Tests for the notes API endpoints."""

import json
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import patch, MagicMock

from app.main import app
from app.db import get_session
from app.models import Note, Task


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Mock AI responses for testing
MOCK_ANALYSIS = {
    "summary": "A test note about project planning and task management.",
    "tags": ["planning", "project", "management"],
    "followups": [
        "Review project requirements",
        "Create task breakdown",
        "Schedule team meeting"
    ]
}

MOCK_EMBEDDING = [0.1] * 1536  # Mock embedding vector


class TestNotesAPI:
    """Test cases for notes API endpoints."""

    @patch('app.ai.analyze_note')
    @patch('app.ai.generate_embedding')
    def test_create_note_success(self, mock_embedding, mock_analysis, client):
        """Test successful note creation with AI analysis."""
        # Setup mocks
        mock_analysis.return_value = MOCK_ANALYSIS
        mock_embedding.return_value = MOCK_EMBEDDING
        
        # Test data
        note_data = {
            "title": "Test Note",
            "body": "This is a test note about project planning."
        }
        
        # Make request
        response = client.post("/api/notes/", json=note_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check note data
        assert data["title"] == note_data["title"]
        assert data["body"] == note_data["body"]
        assert data["summary"] == MOCK_ANALYSIS["summary"]
        assert data["tags"] == MOCK_ANALYSIS["tags"]
        assert len(data["tasks"]) == 3
        
        # Check tasks
        for i, task in enumerate(data["tasks"]):
            assert task["text"] == MOCK_ANALYSIS["followups"][i]
            assert task["status"] == "open"
            assert "id" in task
        
        # Verify AI functions were called
        mock_analysis.assert_called_once_with(note_data["title"], note_data["body"])
        mock_embedding.assert_called_once_with(note_data["body"])

    @patch('app.ai.analyze_note')
    @patch('app.ai.generate_embedding')
    def test_create_note_ai_error(self, mock_embedding, mock_analysis, client):
        """Test note creation when AI analysis fails."""
        # Setup mock to raise error
        from app.ai import AIError
        mock_analysis.side_effect = AIError("OpenAI API error")
        
        note_data = {
            "title": "Test Note",
            "body": "This is a test note."
        }
        
        response = client.post("/api/notes/", json=note_data)
        
        assert response.status_code == 422
        assert "AI processing failed" in response.json()["detail"]

    def test_create_note_validation_error(self, client):
        """Test note creation with invalid data."""
        note_data = {
            "title": "",  # Empty title should fail validation
            "body": "This is a test note."
        }
        
        response = client.post("/api/notes/", json=note_data)
        
        assert response.status_code == 422

    @patch('app.ai.analyze_note')
    @patch('app.ai.generate_embedding')
    def test_get_note_by_id(self, mock_embedding, mock_analysis, client, session):
        """Test retrieving a specific note by ID."""
        # Setup mocks
        mock_analysis.return_value = MOCK_ANALYSIS
        mock_embedding.return_value = MOCK_EMBEDDING
        
        # Create a note first
        note_data = {
            "title": "Test Note",
            "body": "This is a test note."
        }
        create_response = client.post("/api/notes/", json=note_data)
        note_id = create_response.json()["id"]
        
        # Get the note
        response = client.get(f"/api/notes/{note_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == note_id
        assert data["title"] == note_data["title"]
        assert data["body"] == note_data["body"]

    def test_get_note_not_found(self, client):
        """Test retrieving a non-existent note."""
        response = client.get("/api/notes/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"

    @patch('app.ai.analyze_note')
    @patch('app.ai.generate_embedding')
    def test_list_notes_without_search(self, mock_embedding, mock_analysis, client):
        """Test listing notes without search query."""
        # Setup mocks
        mock_analysis.return_value = MOCK_ANALYSIS
        mock_embedding.return_value = MOCK_EMBEDDING
        
        # Create a few notes
        for i in range(3):
            note_data = {
                "title": f"Test Note {i}",
                "body": f"This is test note number {i}."
            }
            client.post("/api/notes/", json=note_data)
        
        # List notes
        response = client.get("/api/notes/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["notes"]) == 3
        assert data["limit"] == 10
        assert data["offset"] == 0
        
        # Check that similarity is not included (no search)
        for note in data["notes"]:
            assert note["similarity"] is None

    @patch('app.ai.analyze_note')
    @patch('app.ai.generate_embedding')
    @patch('app.ai.embed_query')
    def test_list_notes_with_search(self, mock_embed_query, mock_embedding, mock_analysis, client):
        """Test semantic search functionality."""
        # Setup mocks
        mock_analysis.return_value = MOCK_ANALYSIS
        mock_embedding.return_value = MOCK_EMBEDDING
        mock_embed_query.return_value = MOCK_EMBEDDING  # Same embedding for simplicity
        
        # Create a note
        note_data = {
            "title": "Project Planning",
            "body": "This note covers project planning and management."
        }
        client.post("/api/notes/", json=note_data)
        
        # Search for notes
        response = client.get("/api/notes/?search=project")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["notes"]) >= 1
        
        # Check that similarity scores are included
        for note in data["notes"]:
            assert note["similarity"] is not None
            assert isinstance(note["similarity"], float)
            assert -1 <= note["similarity"] <= 1
        
        # Verify search embedding was called
        mock_embed_query.assert_called_once_with("project")

    def test_list_notes_pagination(self, client):
        """Test notes pagination."""
        response = client.get("/api/notes/?limit=5&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0
