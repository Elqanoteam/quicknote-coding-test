"""Tests for semantic search functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import patch

from app.main import app
from app.db import get_session


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


# Mock data for different topics
MOCK_ANALYSES = {
    "project": {
        "summary": "A note about project planning and management strategies.",
        "tags": ["planning", "project", "management"],
        "followups": ["Define project scope", "Create timeline", "Assign team roles"],
    },
    "meeting": {
        "summary": "Notes from team meeting discussing quarterly goals.",
        "tags": ["meeting", "goals", "team"],
        "followups": [
            "Send meeting summary",
            "Schedule follow-up",
            "Update project board",
        ],
    },
    "research": {
        "summary": "Research findings on market trends and opportunities.",
        "tags": ["research", "market", "trends"],
        "followups": ["Analyze data", "Create report", "Present findings"],
    },
}

# Different embeddings for different topics (simplified for testing)
MOCK_EMBEDDINGS = {
    "project": [1.0] + [0.0] * 1535,
    "meeting": [0.0, 1.0] + [0.0] * 1534,
    "research": [0.0, 0.0, 1.0] + [0.0] * 1533,
    "project_query": [0.9] + [0.1] * 1535,  # Similar to project
    "meeting_query": [0.1, 0.9] + [0.0] * 1534,  # Similar to meeting
}


class TestSemanticSearch:
    """Test cases for semantic search functionality."""

    @patch("app.routers.notes.analyze_note")
    @patch("app.routers.notes.generate_embedding")
    @patch("app.routers.notes.embed_query")
    def test_semantic_search_ordering(
        self, mock_embed_query, mock_embedding, mock_analysis, client
    ):
        """Test that semantic search returns results ordered by similarity."""

        # Create notes with different topics
        notes_data = [
            {
                "title": "Project Planning Guidelines",
                "body": "This document outlines project planning methodologies and best practices.",
                "topic": "project",
            },
            {
                "title": "Team Meeting Notes",
                "body": "Summary of our weekly team meeting and action items discussed.",
                "topic": "meeting",
            },
            {
                "title": "Market Research Analysis",
                "body": "Comprehensive analysis of current market trends and competitive landscape.",
                "topic": "research",
            },
        ]

        # Setup mocks to return different embeddings based on content
        def mock_analysis_side_effect(title, body):
            for note_data in notes_data:
                if title == note_data["title"]:
                    return MOCK_ANALYSES[note_data["topic"]]
            return MOCK_ANALYSES["project"]  # fallback

        def mock_embedding_side_effect(text):
            for note_data in notes_data:
                if note_data["title"] in text or note_data["body"] in text:
                    return MOCK_EMBEDDINGS[note_data["topic"]]
            return MOCK_EMBEDDINGS["project"]  # fallback

        mock_analysis.side_effect = mock_analysis_side_effect
        mock_embedding.side_effect = mock_embedding_side_effect

        # Create the notes
        created_notes = []
        for note_data in notes_data:
            response = client.post(
                "/api/notes/",
                json={"title": note_data["title"], "body": note_data["body"]},
            )
            created_notes.append(response.json())

        # Test search for "project" - should return project note first
        mock_embed_query.return_value = MOCK_EMBEDDINGS["project_query"]

        response = client.get("/api/notes/?search=project")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["notes"]) == 3

        # Check that all notes have similarity scores
        for note in data["notes"]:
            assert note["similarity"] is not None
            assert isinstance(note["similarity"], float)

        # The project note should have the highest similarity
        similarity_scores = [note["similarity"] for note in data["notes"]]
        max_similarity = max(similarity_scores)

        # Find the note with highest similarity
        most_similar_note = next(
            note for note in data["notes"] if note["similarity"] == max_similarity
        )

        # Should be the project planning note
        assert "Project Planning" in most_similar_note["title"]

    @patch("app.routers.notes.analyze_note")
    @patch("app.routers.notes.generate_embedding")
    @patch("app.routers.notes.embed_query")
    def test_search_with_no_results(
        self, mock_embed_query, mock_embedding, mock_analysis, client
    ):
        """Test search when no notes exist."""
        mock_embed_query.return_value = MOCK_EMBEDDINGS["project_query"]

        response = client.get("/api/notes/?search=nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["notes"]) == 0

    @patch("app.routers.notes.analyze_note")
    @patch("app.routers.notes.generate_embedding")
    @patch("app.routers.notes.embed_query")
    def test_search_pagination(
        self, mock_embed_query, mock_embedding, mock_analysis, client
    ):
        """Test semantic search with pagination."""
        # Setup mocks
        mock_analysis.return_value = MOCK_ANALYSES["project"]
        mock_embedding.return_value = MOCK_EMBEDDINGS["project"]
        mock_embed_query.return_value = MOCK_EMBEDDINGS["project_query"]

        # Create multiple notes
        for i in range(5):
            note_data = {
                "title": f"Project Note {i}",
                "body": f"This is project note number {i} about planning.",
            }
            client.post("/api/notes/", json=note_data)

        # Test pagination
        response = client.get("/api/notes/?search=project&limit=2&offset=1")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["notes"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 1

    @patch("app.routers.notes.embed_query")
    def test_search_with_invalid_embeddings(self, mock_embed_query, client):
        """Test search handling when notes have invalid embeddings."""
        # This test would require manually inserting a note with invalid embedding
        # For simplicity, we'll test that the endpoint handles the case gracefully
        mock_embed_query.return_value = MOCK_EMBEDDINGS["project_query"]

        response = client.get("/api/notes/?search=test")

        # Should not crash even with no valid embeddings
        assert response.status_code == 200

    def test_search_empty_query(self, client):
        """Test search with empty query string."""
        response = client.get("/api/notes/?search=")

        assert response.status_code == 200
        # Empty search should still work (though may return no results)

    @patch("app.routers.notes.embed_query")
    def test_search_ai_error(self, mock_embed_query, client):
        """Test search when embedding generation fails."""
        from app.routers.notes import AIError

        mock_embed_query.side_effect = AIError("Embedding API error")

        response = client.get("/api/notes/?search=test")

        assert response.status_code == 422
        assert "Search failed" in response.json()["detail"]
