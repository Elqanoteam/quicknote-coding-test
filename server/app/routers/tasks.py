"""API routes for task management."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..db import get_session
from ..models import Task
from ..schemas import TaskOut, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """
    Update a task's status.
    
    Allows toggling task status between 'open' and 'done'.
    """
    try:
        logger.info(f"Updating task {task_id} to status: {task_update.status}")
        
        # Get the task
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task status
        task.status = task_update.status
        session.add(task)
        session.commit()
        session.refresh(task)
        
        logger.info(f"Successfully updated task {task_id}")
        
        return TaskOut(
            id=task.id,
            text=task.text,
            status=task.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific task by ID."""
    try:
        logger.info(f"Fetching task {task_id}")
        
        statement = select(Task).where(Task.id == task_id)
        task = session.exec(statement).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskOut(
            id=task.id,
            text=task.text,
            status=task.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task")
