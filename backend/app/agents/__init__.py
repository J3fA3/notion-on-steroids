"""
Agentic AI components package.
"""
from app.agents.llm_clients import get_claude_client, get_ollama_client
from app.agents.task_inference import infer_tasks_from_text

__all__ = [
    "get_claude_client",
    "get_ollama_client",
    "infer_tasks_from_text",
]
