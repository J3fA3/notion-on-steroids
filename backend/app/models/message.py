"""
Message model for storing Slack messages and other chat messages.
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.models.base import Base


class Message(Base):
    """
    Message model representing a chat message (e.g., from Slack DMs).

    Attributes:
        id: Primary key
        external_id: External message ID (e.g., Slack message ID)
        platform: Platform where message originated (slack, teams, etc.)
        channel_id: Channel/conversation ID
        user_id: User ID who sent the message
        user_name: Display name of user
        content: Message text content
        timestamp: When message was sent
        processed: Whether message has been processed by AI
        is_actionable: Whether AI determined message contains actionable content
        created_at: Record creation timestamp
        updated_at: Record last update timestamp
    """

    __tablename__ = "messages"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # External identifiers
    external_id = Column(String(500), nullable=False, unique=True, index=True)
    platform = Column(String(50), nullable=False, index=True)
    channel_id = Column(String(500), nullable=False, index=True)

    # User information
    user_id = Column(String(500), nullable=False)
    user_name = Column(String(500), nullable=True)

    # Message content
    content = Column(Text, nullable=False)

    # Message metadata
    timestamp = Column(DateTime, nullable=False, index=True)
    processed = Column(Boolean, nullable=False, default=False, index=True)
    is_actionable = Column(Boolean, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        """String representation of Message."""
        return f"<Message(id={self.id}, platform='{self.platform}', external_id='{self.external_id}', processed={self.processed})>"
