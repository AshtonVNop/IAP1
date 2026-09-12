from datetime import datetime

import pytest

from planner import Planner


def test_tasks_are_returned_in_chronological_order() -> None:
    planner = Planner()
    planner.add_task("Study for biology", datetime(2026, 9, 12, 16, 0))
    planner.add_task("Submit essay", datetime(2026, 9, 12, 15, 0))

    assert [task.title for task in planner.tasks()] == [
        "Submit essay",
        "Study for biology",
    ]


def test_tasks_with_equal_deadlines_keep_addition_order() -> None:
    planner = Planner()
    deadline = datetime(2026, 9, 12, 15, 0)
    planner.add_task("First task", deadline)
    planner.add_task("Second task", deadline)

    assert [task.title for task in planner.tasks()] == ["First task", "Second task"]


def test_empty_task_title_is_rejected() -> None:
    planner = Planner()

    with pytest.raises(ValueError, match="Task title cannot be empty"):
        planner.add_task("   ", datetime(2026, 9, 12, 15, 0))