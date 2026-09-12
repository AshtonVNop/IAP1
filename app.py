"""Command-line interface for the college student planner."""

from datetime import datetime

from planner import Planner

DATE_FORMAT = "%Y-%m-%d %H:%M"


def read_task(planner: Planner) -> bool:
    """Read one task from the user and return whether the session should continue."""
    title = input("Objective (or 'q' to quit): ").strip()
    if title.lower() == "q":
        return False

    due_text = input(f"Due date and time ({DATE_FORMAT}): ").strip()
    try:
        due_at = datetime.strptime(due_text, DATE_FORMAT)
        planner.add_task(title, due_at)
    except ValueError as error:
        print(f"Invalid task: {error}")
    else:
        print("Objective added.")
    return True


def display_tasks(planner: Planner) -> None:
    """Print the planner in chronological order."""
    print("\nYour planner:")
    for task in planner.tasks():
        print(f"- {task.due_at.strftime(DATE_FORMAT)} | {task.title}")


def main() -> None:
    planner = Planner()
    print("College Student Planner")
    print("Add objectives and deadlines in chronological order.\n")

    while read_task(planner):
        print()

    display_tasks(planner)


if __name__ == "__main__":
    main()