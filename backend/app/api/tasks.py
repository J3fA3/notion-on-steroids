"""
Tasks API endpoints.
"""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import Task, TaskStatus, get_db
from app.models.message import Message

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Pydantic Schemas
# ============================================


class TaskCreate(BaseModel):
    """Schema for creating a task manually."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    context: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Optional[int] = Field(None, ge=1, le=5)
    confidence_score: float = Field(100.0, ge=0, le=100)
    source_type: str = "manual"
    source_id: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    context: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str]
    context: Optional[str]
    status: str
    priority: Optional[int]
    confidence_score: float
    source_type: str
    source_id: Optional[str]
    due_date: Optional[datetime]
    inferred_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InferTasksRequest(BaseModel):
    """Schema for task inference request."""

    content: str = Field(..., min_length=10, max_length=50000)
    source: str = Field(default="manual_text", max_length=50)


class InferTasksResponse(BaseModel):
    """Schema for task inference response."""

    message: str
    tasks_inferred: int
    tasks: List[TaskResponse]


# ============================================
# Endpoints
# ============================================


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    List all tasks with optional status filter.

    Args:
        status: Filter by status (todo, in_progress, done)
        limit: Maximum number of tasks to return
        db: Database session

    Returns:
        List of tasks
    """
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).limit(limit).all()

    return tasks


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a single task by ID.

    Args:
        task_id: Task ID
        db: Database session

    Returns:
        Task details
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task with id {task_id} does not exist",
                "resolution": "Check task ID or fetch all tasks with GET /api/tasks",
            },
        )

    return task


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task manually.

    Args:
        task_data: Task creation data
        db: Database session

    Returns:
        Created task
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        context=task_data.context,
        status=task_data.status.value,
        priority=task_data.priority,
        confidence_score=task_data.confidence_score,
        source_type=task_data.source_type,
        source_id=task_data.source_id,
        due_date=task_data.due_date,
        inferred_at=datetime.utcnow(),
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(f"Created task: {task.id} - {task.title}")

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing task.

    Args:
        task_id: Task ID
        task_data: Task update data
        db: Database session

    Returns:
        Updated task
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task with id {task_id} does not exist",
            },
        )

    # Update fields if provided
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value:
            setattr(task, field, value.value if isinstance(value, TaskStatus) else value)
        else:
            setattr(task, field, value)

    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    logger.info(f"Updated task: {task.id} - {task.title}")

    return task


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.

    Args:
        task_id: Task ID
        db: Database session
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "TASK_NOT_FOUND",
                "message": f"Task with id {task_id} does not exist",
            },
        )

    db.delete(task)
    db.commit()

    logger.info(f"Deleted task: {task_id}")

    return None


@router.post("/infer-tasks", response_model=InferTasksResponse)
async def infer_tasks(
    request: InferTasksRequest,
    db: Session = Depends(get_db),
):
    """
    Infer tasks from text content using AI.

    This endpoint:
    1. Stores the raw content in the messages table
    2. Passes content to TaskInferenceAgent for analysis
    3. Creates tasks in database
    4. Returns inferred tasks

    Args:
        request: Text content and source
        db: Database session

    Returns:
        List of inferred tasks
    """
    logger.info(f"Received inference request: {len(request.content)} characters from {request.source}")

    # Store raw content in messages table for learning/debugging
    message = Message(
        external_id=f"{request.source}_{datetime.utcnow().timestamp()}",
        platform=request.source,
        channel_id="manual_input",
        user_id="user",
        user_name="Manual Input",
        content=request.content,
        timestamp=datetime.utcnow(),
        processed=False,
        is_actionable=None,  # Will be determined by agent
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    try:
        # Import here to avoid circular dependencies
        from app.agents.task_inference import infer_tasks_from_text

        # Run inference
        inferred_tasks = await infer_tasks_from_text(request.content, request.source, message.id, db)

        # Mark message as processed
        message.processed = True
        message.is_actionable = len(inferred_tasks) > 0
        db.commit()

        logger.info(f"Successfully inferred {len(inferred_tasks)} tasks from message {message.id}")

        return InferTasksResponse(
            message="Tasks inferred successfully",
            tasks_inferred=len(inferred_tasks),
            tasks=[TaskResponse.model_validate(task) for task in inferred_tasks],
        )

    except Exception as e:
        logger.error(f"Failed to infer tasks: {e}", exc_info=True)
        message.processed = True
        message.is_actionable = False
        db.commit()

        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "INFERENCE_FAILED",
                "message": f"Failed to infer tasks: {str(e)}",
                "resolution": "Check server logs for details. Ensure Claude API key is set and valid.",
            },
        )


@router.post("/upload-file")
async def upload_file(file: bytes = None, db: Session = Depends(get_db)):
    """
    Upload and parse a file (TXT or PDF).

    Extracts text content and returns it for processing.
    Frontend can then send the extracted text to /infer-tasks.

    Args:
        file: Uploaded file bytes
        db: Database session

    Returns:
        Extracted text and filename
    """
    from fastapi import File, UploadFile
    from PyPDF2 import PdfReader
    import io

    # Note: This endpoint needs proper typing, simplified for now
    logger.info("File upload endpoint called (not fully implemented yet)")

    return {
        "extracted_text": "PDF parsing endpoint is a placeholder. Install PyPDF2 and implement.",
        "filename": "unknown",
    }
