"""
Task Inference Agent using LangGraph.

This agent analyzes text content (Slack messages, emails, meeting notes) and
infers actionable tasks using a multi-node workflow.
"""
import json
import logging
import re
from datetime import datetime, timedelta
from typing import List, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from sqlalchemy.orm import Session

from app.agents.llm_clients import get_claude_client, get_ollama_client
from app.config import settings
from app.models.task import Task

logger = logging.getLogger(__name__)


# ============================================
# State Definition
# ============================================


class TaskInferenceState(TypedDict):
    """State passed between nodes in the task inference graph."""

    # Input
    content: str  # Raw text content
    source: str  # Source type (manual_text, slack, etc.)
    message_id: int  # Database message ID

    # Processing
    is_actionable: bool  # Whether content has actionable items
    extracted_tasks: List[dict]  # Raw task data from LLM
    validated_tasks: List[dict]  # Tasks after validation
    confidence_scores: List[float]  # Confidence for each task

    # Output
    created_tasks: List[Task]  # Final SQLAlchemy task objects
    errors: List[str]  # Any errors encountered


# ============================================
# Node Functions
# ============================================


async def analyze_message(state: TaskInferenceState) -> TaskInferenceState:
    """
    Node 1: Analyze if content contains actionable items.

    Uses local LLM (Ollama) for fast classification.
    """
    logger.info(f"[AnalyzeMessage] Processing {len(state['content'])} characters")

    try:
        if settings.USE_LOCAL_LLM_FOR_CLASSIFICATION:
            ollama = get_ollama_client()
            is_actionable = await ollama.is_actionable(state["content"])
        else:
            # Skip classification, assume all content is actionable
            is_actionable = True

        state["is_actionable"] = is_actionable
        logger.info(f"[AnalyzeMessage] Content is {'actionable' if is_actionable else 'not actionable'}")

    except Exception as e:
        logger.warning(f"[AnalyzeMessage] Classification failed: {e}. Assuming actionable.")
        state["is_actionable"] = True

    return state


async def extract_tasks(state: TaskInferenceState) -> TaskInferenceState:
    """
    Node 2: Extract task parameters from content.

    Uses Claude for complex reasoning and parameter extraction.
    """
    if not state["is_actionable"]:
        logger.info("[ExtractTasks] Skipping - content not actionable")
        state["extracted_tasks"] = []
        return state

    logger.info("[ExtractTasks] Extracting tasks using Claude")

    claude = get_claude_client()

    system_prompt = """You are a task inference assistant. Analyze the provided text and extract ALL actionable tasks.

For each task, extract:
- title: Clear, concise task title (imperative form, e.g., "Send Q4 report")
- description: Detailed description with context
- due_date: If mentioned, convert to ISO format (YYYY-MM-DD). Parse relative dates like "tomorrow", "next week", "EOD"
- priority: 1 (urgent) to 5 (low priority). Base on urgency indicators.
- confidence: How confident you are this is a real task (0-100)

Important rules:
- Each task should be ONE specific action
- Split compound tasks into separate tasks
- Include implicit commitments (e.g., "I'll send the report" → task: "Send report")
- Include requests to the user (e.g., "Can you review my PR?" → task: "Review PR")
- Ignore greetings, acknowledgments, pure questions
- Return ONLY valid JSON array of tasks

Example output:
[
  {
    "title": "Send Q4 report to stakeholders",
    "description": "Compile Q4 performance metrics and send to all stakeholders by EOD",
    "due_date": "2025-11-11",
    "priority": 1,
    "confidence": 85,
    "context": "From message: 'Can you send me the Q4 report by tomorrow?'"
  },
  {
    "title": "Review PR #123",
    "description": "Code review for authentication feature implementation",
    "due_date": null,
    "priority": 2,
    "confidence": 90,
    "context": "From message: 'Could you review my PR when you get a chance?'"
  }
]

Return ONLY the JSON array, no additional text."""

    user_prompt = f"""Analyze this text and extract all actionable tasks:

{state['content']}

Today's date: {datetime.now().strftime('%Y-%m-%d')}

Return JSON array of tasks:"""

    try:
        response_json = await claude.generate_json(system_prompt, user_prompt, temperature=0.3)

        # Handle both array and object responses
        if isinstance(response_json, list):
            tasks = response_json
        elif isinstance(response_json, dict) and "tasks" in response_json:
            tasks = response_json["tasks"]
        else:
            logger.error(f"[ExtractTasks] Unexpected JSON structure: {response_json}")
            tasks = []

        state["extracted_tasks"] = tasks
        state["confidence_scores"] = [task.get("confidence", 50) for task in tasks]

        logger.info(f"[ExtractTasks] Extracted {len(tasks)} tasks")

    except Exception as e:
        logger.error(f"[ExtractTasks] Failed: {e}")
        state["extracted_tasks"] = []
        state["errors"] = state.get("errors", []) + [f"Task extraction failed: {e}"]

    return state


async def validate_tasks(state: TaskInferenceState) -> TaskInferenceState:
    """
    Node 3: Validate and filter tasks.

    - Remove duplicates
    - Filter by confidence threshold
    - Validate required fields
    """
    logger.info(f"[ValidateTasks] Validating {len(state['extracted_tasks'])} tasks")

    validated = []
    seen_titles = set()

    for task_data in state["extracted_tasks"]:
        # Check confidence threshold
        confidence = task_data.get("confidence", 0)
        if confidence < settings.MIN_CONFIDENCE_THRESHOLD:
            logger.info(f"[ValidateTasks] Skipping low-confidence task: {task_data.get('title')} ({confidence}%)")
            continue

        # Check required fields
        title = task_data.get("title", "").strip()
        if not title:
            logger.warning("[ValidateTasks] Skipping task with no title")
            continue

        # Check for duplicates (case-insensitive)
        title_lower = title.lower()
        if title_lower in seen_titles:
            logger.info(f"[ValidateTasks] Skipping duplicate task: {title}")
            continue

        seen_titles.add(title_lower)
        validated.append(task_data)

    state["validated_tasks"] = validated
    logger.info(f"[ValidateTasks] Validated {len(validated)} tasks")

    return state


def generate_tasks(state: TaskInferenceState, db: Session) -> TaskInferenceState:
    """
    Node 4: Generate Task objects and save to database.

    This is a sync function because it interacts with database.
    """
    logger.info(f"[GenerateTasks] Creating {len(state['validated_tasks'])} tasks in database")

    created_tasks = []

    for task_data in state["validated_tasks"]:
        try:
            # Parse due date
            due_date = None
            if task_data.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(task_data["due_date"])
                except (ValueError, TypeError):
                    # Try parsing relative dates
                    due_date = _parse_relative_date(task_data["due_date"])

            # Create task
            task = Task(
                title=task_data["title"][:500],  # Truncate if too long
                description=task_data.get("description"),
                context=task_data.get("context"),
                status="todo",
                priority=task_data.get("priority", 3),
                confidence_score=task_data.get("confidence", 50),
                source_type=state["source"],
                source_id=str(state["message_id"]),
                due_date=due_date,
                inferred_at=datetime.utcnow(),
            )

            db.add(task)
            created_tasks.append(task)

            logger.info(f"[GenerateTasks] Created task: {task.title}")

        except Exception as e:
            logger.error(f"[GenerateTasks] Failed to create task: {e}")
            state["errors"] = state.get("errors", []) + [f"Failed to create task: {e}"]

    # Commit all tasks
    try:
        db.commit()
        # Refresh all tasks to get IDs
        for task in created_tasks:
            db.refresh(task)
        logger.info(f"[GenerateTasks] Successfully committed {len(created_tasks)} tasks")
    except Exception as e:
        logger.error(f"[GenerateTasks] Failed to commit tasks: {e}")
        db.rollback()
        state["errors"] = state.get("errors", []) + [f"Database commit failed: {e}"]
        created_tasks = []

    state["created_tasks"] = created_tasks

    return state


# ============================================
# Helper Functions
# ============================================


def _parse_relative_date(date_str: str) -> datetime:
    """Parse relative dates like 'tomorrow', 'next week', 'EOD'."""
    date_str_lower = date_str.lower().strip()
    now = datetime.now()

    if "tomorrow" in date_str_lower:
        return now + timedelta(days=1)
    elif "next week" in date_str_lower:
        return now + timedelta(weeks=1)
    elif "eod" in date_str_lower or "end of day" in date_str_lower:
        return now.replace(hour=17, minute=0, second=0, microsecond=0)
    elif "next month" in date_str_lower:
        return now + timedelta(days=30)
    elif match := re.search(r"in (\d+) days?", date_str_lower):
        days = int(match.group(1))
        return now + timedelta(days=days)

    # Default: tomorrow
    return now + timedelta(days=1)


# ============================================
# LangGraph Workflow
# ============================================


def create_task_inference_graph(db: Session):
    """
    Create the task inference workflow graph.

    Workflow:
    1. AnalyzeMessage → Check if actionable
    2. ExtractTasks → Use Claude to extract task parameters
    3. ValidateTasks → Filter by confidence, remove duplicates
    4. GenerateTasks → Create Task objects in database
    """
    # Create graph
    workflow = StateGraph(TaskInferenceState)

    # Add nodes
    workflow.add_node("analyze", analyze_message)
    workflow.add_node("extract", extract_tasks)
    workflow.add_node("validate", validate_tasks)
    workflow.add_node("generate", lambda state: generate_tasks(state, db))

    # Define edges (sequential flow)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "extract")
    workflow.add_edge("extract", "validate")
    workflow.add_edge("validate", "generate")
    workflow.set_finish_point("generate")

    return workflow.compile()


# ============================================
# Public API
# ============================================


async def infer_tasks_from_text(
    content: str,
    source: str,
    message_id: int,
    db: Session,
) -> List[Task]:
    """
    Infer tasks from text content using LangGraph agent.

    Args:
        content: Raw text content
        source: Source type (manual_text, slack, etc.)
        message_id: Database message ID
        db: Database session

    Returns:
        List of created Task objects
    """
    logger.info(f"Starting task inference for message {message_id}")

    # Create initial state
    initial_state: TaskInferenceState = {
        "content": content,
        "source": source,
        "message_id": message_id,
        "is_actionable": False,
        "extracted_tasks": [],
        "validated_tasks": [],
        "confidence_scores": [],
        "created_tasks": [],
        "errors": [],
    }

    # Create and run graph
    graph = create_task_inference_graph(db)

    # Run asynchronously
    final_state = await graph.ainvoke(initial_state)

    # Log results
    if final_state["errors"]:
        logger.warning(f"Task inference completed with errors: {final_state['errors']}")

    logger.info(f"Task inference complete: {len(final_state['created_tasks'])} tasks created")

    return final_state["created_tasks"]
