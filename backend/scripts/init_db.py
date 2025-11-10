#!/usr/bin/env python3
"""
Database initialization script.

Creates all database tables and optionally seeds with test data.

Usage:
    python scripts/init_db.py [--seed]
"""
import argparse
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta

from app.config import settings
from app.models.base import Base, engine
from app.models.message import Message
from app.models.task import Task, TaskStatus
from app.models.transcript import Transcript


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database tables created successfully at: {settings.DATABASE_URL}")


def seed_test_data():
    """Seed database with test data for development."""
    from sqlalchemy.orm import Session

    print("\nSeeding test data...")

    with Session(engine) as session:
        # Create test tasks
        test_tasks = [
            Task(
                title="Send Q4 report to stakeholders",
                description="Compile Q4 performance metrics and send to all stakeholders by EOD",
                status=TaskStatus.TODO.value,
                confidence_score=85.5,
                source_type="slack",
                source_id="slack_msg_001",
                due_date=datetime.utcnow() + timedelta(days=1),
                inferred_at=datetime.utcnow(),
                context="From Slack DM with Sarah: 'Can you send the Q4 report by tomorrow?'",
                priority=1,
            ),
            Task(
                title="Review PR #123 for new feature",
                description="Code review for authentication feature implementation",
                status=TaskStatus.IN_PROGRESS.value,
                confidence_score=92.0,
                source_type="slack",
                source_id="slack_msg_002",
                due_date=datetime.utcnow() + timedelta(hours=6),
                inferred_at=datetime.utcnow(),
                context="From Slack: 'Hey, could you review my PR when you get a chance?'",
                priority=2,
            ),
            Task(
                title="Schedule team sync for next week",
                description="Find a time for the team to sync on project progress",
                status=TaskStatus.DONE.value,
                confidence_score=78.0,
                source_type="google_meet",
                source_id="meet_transcript_001",
                completed_at=datetime.utcnow() - timedelta(hours=2),
                inferred_at=datetime.utcnow() - timedelta(days=1),
                context="From team meeting: 'Let's schedule a sync next week'",
                priority=3,
            ),
        ]

        # Create test messages
        test_messages = [
            Message(
                external_id="slack_msg_001",
                platform="slack",
                channel_id="D12345678",
                user_id="U98765432",
                user_name="Sarah Johnson",
                content="Hey! Can you send me the Q4 report by tomorrow? The board meeting is on Wednesday.",
                timestamp=datetime.utcnow() - timedelta(hours=3),
                processed=True,
                is_actionable=True,
            ),
            Message(
                external_id="slack_msg_002",
                platform="slack",
                channel_id="D87654321",
                user_id="U11111111",
                user_name="Alex Chen",
                content="Hey, could you review my PR when you get a chance? It's for the new auth feature.",
                timestamp=datetime.utcnow() - timedelta(hours=1),
                processed=True,
                is_actionable=True,
            ),
            Message(
                external_id="slack_msg_003",
                platform="slack",
                channel_id="D12345678",
                user_id="U98765432",
                user_name="Sarah Johnson",
                content="Thanks for the update! Looks great.",
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                processed=True,
                is_actionable=False,
            ),
        ]

        # Create test transcript
        test_transcripts = [
            Transcript(
                external_id="meet_transcript_001",
                platform="google_meet",
                meeting_title="Weekly Team Sync - Product Team",
                meeting_url="https://meet.google.com/abc-defg-hij",
                participants="John Doe, Sarah Johnson, Alex Chen, Maria Garcia",
                content="""
John: Alright everyone, let's get started. How's everyone doing on their tasks?

Sarah: I'm making good progress on the Q4 report. Should have it ready by tomorrow.

Alex: I just submitted my PR for the auth feature. Would love a review when someone has time.

Maria: I can review it after this meeting. Also, we should schedule another sync for next week to review the sprint.

John: Great idea. Let's do that. I'll send out a calendar invite.
                """.strip(),
                duration_minutes=30,
                start_time=datetime.utcnow() - timedelta(days=1, hours=2),
                end_time=datetime.utcnow() - timedelta(days=1, hours=1, minutes=30),
                processed=True,
            ),
        ]

        # Add all test data
        session.add_all(test_tasks)
        session.add_all(test_messages)
        session.add_all(test_transcripts)

        # Commit transaction
        session.commit()

        print(f"✓ Seeded {len(test_tasks)} tasks")
        print(f"✓ Seeded {len(test_messages)} messages")
        print(f"✓ Seeded {len(test_transcripts)} transcripts")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Initialize Lotus database")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with test data",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Lotus Database Initialization")
    print("=" * 60)

    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Create tables
    create_tables()

    # Seed test data if requested
    if args.seed:
        seed_test_data()
        print("\n✓ Database initialized with test data")
    else:
        print("\n✓ Database initialized (use --seed to add test data)")

    print("=" * 60)


if __name__ == "__main__":
    main()
