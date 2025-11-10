"""
Task model for storing inferred tasks.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import validates

from app.models.base import Base


class TaskStatus(str, Enum):
    """Task status enum."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    """
    Task model representing an inferred task from messages or transcripts.

    Attributes:
        id: Primary key
        title: Short task title
        description: Detailed task description
        status: Current task status (todo, in_progress, done)
        confidence_score: AI inference confidence (0-100)
        source_type: Where task was inferred from (slack, google_meet, manual)
        source_id: ID of source message/transcript
        due_date: Optional due date
        inferred_at: When task was inferred by AI
        completed_at: When task was marked as done
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
        context: Additional context from AI agent
        priority: Task priority (1-5, 1=highest)
    """

    __tablename__ = "tasks"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Task content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    context = Column(Text, nullable=True)

    # Task metadata
    status = Column(
        String(20), nullable=False, default=TaskStatus.TODO.value, index=True
    )
    priority = Column(Integer, nullable=True, default=3)
    confidence_score = Column(Float, nullable=False, default=0.0)

    # Source tracking
    source_type = Column(String(50), nullable=False, index=True)
    source_id = Column(String(500), nullable=True, index=True)

    # Dates
    due_date = Column(DateTime, nullable=True)
    inferred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @validates("status")
    def validate_status(self, key, value):
        """Validate status is one of allowed values."""
        if value not in [s.value for s in TaskStatus]:
            raise ValueError(
                f"Invalid status: {value}. Must be one of: {[s.value for s in TaskStatus]}"
            )
        return value

    @validates("confidence_score")
    def validate_confidence_score(self, key, value):
        """Validate confidence score is between 0 and 100."""
        if value < 0 or value > 100:
            raise ValueError(f"Confidence score must be between 0 and 100, got: {value}")
        return value

    @validates("priority")
    def validate_priority(self, key, value):
        """Validate priority is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise ValueError(f"Priority must be between 1 and 5, got: {value}")
        return value

    def __repr__(self):
        """String representation of Task."""
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}', confidence={self.confidence_score})>"
