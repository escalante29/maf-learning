"""Mock task and document search tools for the Task Agent."""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool


@tool(approval_mode="never_require")
def get_tasks(project: Annotated[str, "The project name to fetch tasks for"] = "Project Alpha") -> str:
    """Retrieve current tasks for a project.

    Args:
        project: The project name to fetch tasks for.

    Returns:
        JSON string with task data.
    """
    tasks = [
        {
            "id": "TASK-101",
            "title": "Design system architecture",
            "status": "In Progress",
            "assignee": "Alice Chen",
            "due_date": "2026-03-20",
            "priority": "High",
        },
        {
            "id": "TASK-102",
            "title": "Implement authentication flow",
            "status": "To Do",
            "assignee": "Bob Martinez",
            "due_date": "2026-03-25",
            "priority": "High",
        },
        {
            "id": "TASK-103",
            "title": "Write API documentation",
            "status": "In Review",
            "assignee": "Carol Singh",
            "due_date": "2026-03-18",
            "priority": "Medium",
        },
        {
            "id": "TASK-104",
            "title": "Set up CI/CD pipeline",
            "status": "Done",
            "assignee": "Dave Kim",
            "due_date": "2026-03-15",
            "priority": "Medium",
        },
        {
            "id": "TASK-105",
            "title": "User acceptance testing",
            "status": "To Do",
            "assignee": "Eve Johnson",
            "due_date": "2026-04-01",
            "priority": "Low",
        },
    ]

    return json.dumps(
        {"project": project, "total": len(tasks), "tasks": tasks},
        indent=2,
    )


@tool(approval_mode="never_require")
def search_docs(query: Annotated[str, "The search query string"]) -> str:
    """Search project documents matching a query.

    Args:
        query: The search query string.

    Returns:
        JSON string with matching documents.
    """
    docs = [
        {
            "title": "Architecture Decision Record — Microservices",
            "type": "ADR",
            "modified": "2026-03-10",
            "summary": "Documents the decision to adopt a microservices architecture for the platform backend.",
        },
        {
            "title": "Sprint 12 Retrospective",
            "type": "Meeting Notes",
            "modified": "2026-03-08",
            "summary": "Key takeaways: improve deployment process, add more integration tests.",
        },
        {
            "title": "Q1 2026 Project Status Report",
            "type": "Report",
            "modified": "2026-03-01",
            "summary": "Overall project is 68% complete. On track for April delivery.",
        },
    ]

    return json.dumps(
        {"query": query, "results": len(docs), "documents": docs},
        indent=2,
    )
