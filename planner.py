"""Core domain model for the college student planner."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Task:
    """An objective a student wants to complete by a specific time."""

    title: str
    due_at: datetime


class Planner:
    """Stores tasks and presents them in chronological order."""

    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def add_task(self, title: str, due_at: datetime) -> Task:
        """Add and return a task after validating its required fields."""
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        task = Task(title=title.strip(), due_at=due_at)
        self._tasks.append(task)
        return task

    def tasks(self) -> list[Task]:
        """Return a new list ordered from the earliest deadline to the latest."""
        return sorted(self._tasks, key=lambda task: task.due_at)