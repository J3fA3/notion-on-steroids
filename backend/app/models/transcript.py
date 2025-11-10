"""
Transcript model for storing Google Meet and other meeting transcripts.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.models.base import Base


class Transcript(Base):
    """
    Transcript model representing a meeting transcript (e.g., from Google Meet).

    Attributes:
        id: Primary key
        external_id: External transcript ID (e.g., Google Meet ID)
        platform: Platform where transcript originated (google_meet, zoom, etc.)
        meeting_title: Title of the meeting
        meeting_url: URL to the meeting recording/transcript
        participants: Comma-separated list of participant names
        content: Full transcript text
        duration_minutes: Meeting duration in minutes
        start_time: When meeting started
        end_time: When meeting ended
        processed: Whether transcript has been processed by AI
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "transcripts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # External identifiers
    external_id = Column(String(500), nullable=False, unique=True, index=True)
    platform = Column(String(50), nullable=False, index=True)

    # Meeting metadata
    meeting_title = Column(String(1000), nullable=False)
    meeting_url = Column(Text, nullable=True)
    participants = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Transcript content
    content = Column(Text, nullable=False)

    # Meeting times
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)

    # Processing status
    processed = Column(Boolean, nullable=False, default=False, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        """String representation of Transcript."""
        return f"<Transcript(id={self.id}, platform='{self.platform}', title='{self.meeting_title}', processed={self.processed})>"
