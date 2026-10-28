"""Command-line interface for the college student planner."""

from collections.abc import Callable, Iterable
from datetime import datetime

from planner import Planner, Task

DATE_FORMAT = "%Y-%m-%d %H:%M"
QUIT_COMMAND = "q"

ReadLine = Callable[[str], str]
WriteLine = Callable[[str], None]


def prompt_for_task(read: ReadLine) -> tuple[str, str] | None:
    """Ask for one objective; return (title, due text), or None if the user quits."""
    title = read(f"Objective (or '{QUIT_COMMAND}' to quit): ").strip()
    if title.lower() == QUIT_COMMAND:
        return None

    due_text = read(f"Due date and time ({DATE_FORMAT}): ").strip()
    return title, due_text


def submit_task(planner: Planner, title: str, due_text: str) -> str:
    """Parse raw user text, add the task, and return the feedback message to show."""
    try:
        due_at = datetime.strptime(due_text, DATE_FORMAT)
        planner.add_task(title, due_at)
    except ValueError as error:
        return f"Invalid task: {error}"
    return "Objective added."


def format_task(task: Task) -> str:
    """Return one planner line for a task."""
    return f"- {task.due_at.strftime(DATE_FORMAT)} | {task.title}"


def render_planner(tasks: Iterable[Task]) -> list[str]:
    """Return the lines that display the planner, in the order given."""
    return ["\nYour planner:", *(format_task(task) for task in tasks)]


def run_session(planner: Planner, read: ReadLine = input, write: WriteLine = print) -> None:
    """Run one interactive session; console I/O is injected so it can be replaced."""
    write("College Student Planner")
    write("Add objectives and deadlines in chronological order.\n")

    while (entry := prompt_for_task(read)) is not None:
        write(submit_task(planner, *entry))
        write("")

    for line in render_planner(planner.tasks()):
        write(line)


def main() -> None:
    run_session(Planner())


if __name__ == "__main__":
    main()
