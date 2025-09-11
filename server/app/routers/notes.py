"""API routes for notes management."""

import json
import logging
from typing import List, Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ..db import get_session
from ..models import Note, Task
from ..schemas import NoteCreate, NoteOut, NotesSearchResponse
from ..ai import analyze_note, generate_embedding, embed_query, AIError
from ..utils.similarity import calculate_similarity_scores

router = APIRouter(prefix="/notes", tags=["notes"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=NoteOut)
async def create_note(note_data: NoteCreate, session: Session = Depends(get_session)):
    """
    Create a new note with AI analysis.

    This endpoint:
    1. Analyzes the note content using OpenAI to generate summary, tags, and follow-ups
    2. Generates embeddings for semantic search
    3. Stores the note and associated tasks in the database
    """
    try:
        logger.info(f"Creating note: {note_data.title[:50]}...")

        # Analyze note content with OpenAI
        analysis = analyze_note(note_data.title, note_data.body)

        # Generate embedding for the note body
        embedding = generate_embedding(note_data.body)

        # Create note instance
        note = Note(
            title=note_data.title,
            body=note_data.body,
            summary=analysis["summary"],
            tags_json=json.dumps(analysis["tags"]),
            embedding_json=json.dumps(embedding),
        )

        # Add and flush to get the note ID
        session.add(note)
        session.flush()

        # Create tasks from follow-ups
        tasks = []
        for followup_text in analysis["followups"]:
            task = Task(note_id=note.id, text=followup_text, status="open")
            session.add(task)
            tasks.append(task)

        # Commit all changes
        session.commit()
        session.refresh(note)

        # Refresh tasks to get IDs
        for task in tasks:
            session.refresh(task)

        logger.info(f"Successfully created note {note.id} with {len(tasks)} tasks")

        # Return note with tasks
        return NoteOut(
            id=note.id,
            title=note.title,
            body=note.body,
            summary=note.summary,
            tags=json.loads(note.tags_json),
            created_at=note.created_at,
            tasks=[
                {"id": task.id, "text": task.text, "status": task.status}
                for task in tasks
            ],
        )

    except AIError as e:
        logger.error(f"AI processing error: {e}")
        raise HTTPException(status_code=422, detail=f"AI processing failed: {e}")
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create note")


@router.get("/", response_model=NotesSearchResponse)
async def list_notes(
    search: Optional[str] = Query(None, description="Search query for semantic search"),
    limit: int = Query(10, ge=1, le=100, description="Number of notes to return"),
    offset: int = Query(0, ge=0, description="Number of notes to skip"),
    session: Session = Depends(get_session),
):
    """
    List notes with optional semantic search.

    If search query is provided, performs semantic search using embeddings.
    Otherwise returns recent notes paginated.
    """
    try:
        if search:
            logger.info(f"Performing semantic search for: {search}")

            # Generate embedding for search query
            query_embedding = embed_query(search)

            # Get all notes with embeddings
            statement = select(Note)
            all_notes = session.exec(statement).all()

            if not all_notes:
                return NotesSearchResponse(
                    notes=[], total=0, limit=limit, offset=offset
                )

            # Prepare embeddings for similarity calculation
            note_embeddings: List[Tuple[int, List[float]]] = []
            for note in all_notes:
                try:
                    embedding = json.loads(note.embedding_json)
                    note_embeddings.append((note.id, embedding))
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Invalid embedding for note {note.id}: {e}")
                    continue

            # Calculate similarities
            similarities = calculate_similarity_scores(query_embedding, note_embeddings)

            # Get top results with pagination
            paginated_similarities = similarities[offset : offset + limit]

            # Fetch notes by IDs and preserve order
            note_ids = [note_id for note_id, _ in paginated_similarities]
            similarity_map = {note_id: sim for note_id, sim in paginated_similarities}

            if note_ids:
                statement = select(Note).where(Note.id.in_(note_ids))
                found_notes = session.exec(statement).all()

                # Sort notes by similarity order and add similarity scores
                notes_with_similarity = []
                for note in found_notes:
                    # Get tasks for this note
                    tasks_statement = select(Task).where(Task.note_id == note.id)
                    tasks = session.exec(tasks_statement).all()

                    note_out = NoteOut(
                        id=note.id,
                        title=note.title,
                        body=note.body,
                        summary=note.summary,
                        tags=json.loads(note.tags_json),
                        created_at=note.created_at,
                        tasks=[
                            {"id": task.id, "text": task.text, "status": task.status}
                            for task in tasks
                        ],
                        similarity=round(similarity_map[note.id], 0),
                    )
                    notes_with_similarity.append(note_out)

                # Sort by similarity
                notes_with_similarity.sort(
                    key=lambda x: x.similarity or 0, reverse=True
                )

                return NotesSearchResponse(
                    notes=notes_with_similarity,
                    total=len(similarities),
                    limit=limit,
                    offset=offset,
                )
            else:
                return NotesSearchResponse(
                    notes=[], total=0, limit=limit, offset=offset
                )

        else:
            # Regular pagination without search
            logger.info(f"Listing notes with limit={limit}, offset={offset}")

            # Get total count
            count_statement = select(Note)
            total_notes = len(session.exec(count_statement).all())

            # Get paginated notes (newest first)
            statement = (
                select(Note)
                .order_by(Note.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            notes = session.exec(statement).all()

            # Convert to response format
            notes_out = []
            for note in notes:
                # Get tasks for this note
                tasks_statement = select(Task).where(Task.note_id == note.id)
                tasks = session.exec(tasks_statement).all()

                note_out = NoteOut(
                    id=note.id,
                    title=note.title,
                    body=note.body,
                    summary=note.summary,
                    tags=json.loads(note.tags_json),
                    created_at=note.created_at,
                    tasks=[
                        {"id": task.id, "text": task.text, "status": task.status}
                        for task in tasks
                    ],
                )
                notes_out.append(note_out)

            return NotesSearchResponse(
                notes=notes_out, total=total_notes, limit=limit, offset=offset
            )

    except AIError as e:
        logger.error(f"AI error during search: {e}")
        raise HTTPException(status_code=422, detail=f"Search failed: {e}")
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notes")


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(note_id: int, session: Session = Depends(get_session)):
    """Get a specific note by ID."""
    try:
        logger.info(f"Fetching note {note_id}")

        # Get note
        statement = select(Note).where(Note.id == note_id)
        note = session.exec(statement).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Get tasks for this note
        tasks_statement = select(Task).where(Task.note_id == note_id)
        tasks = session.exec(tasks_statement).all()

        return NoteOut(
            id=note.id,
            title=note.title,
            body=note.body,
            summary=note.summary,
            tags=json.loads(note.tags_json),
            created_at=note.created_at,
            tasks=[
                {"id": task.id, "text": task.text, "status": task.status}
                for task in tasks
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching note {note_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve note")


@router.delete("/{note_id}")
async def delete_note(
    note_id: int, note_name: str, session: Session = Depends(get_session)
):
    """Delete a specific note by ID."""
    try:
        logger.info(f"Deleting note {note_name}: {note_id}")

        # Get note to ensure it exists
        statement = select(Note).where(Note.id == note_id)
        note = session.exec(statement).first()

        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Delete associated tasks first (due to foreign key constraint)
        tasks_statement = select(Task).where(Task.note_id == note_id)
        tasks = session.exec(tasks_statement).all()
        for task in tasks:
            session.delete(task)

        # Delete the note
        session.delete(note)
        session.commit()

        logger.info(
            f"Successfully deleted note {note_id} and {len(tasks)} associated tasks"
        )

        return {"message": "Note deleted successfully", "id": note_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete note")
