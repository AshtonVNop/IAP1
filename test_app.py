import subprocess
import sys
from pathlib import Path


APP_PATH = Path(__file__).with_name("app.py")


def test_cli_adds_and_displays_tasks_in_deadline_order() -> None:
    result = subprocess.run(
        [sys.executable, str(APP_PATH)],
        input=(
            "Study for biology\n"
            "2026-09-12 16:00\n"
            "Submit essay\n"
            "2026-09-12 15:00\n"
            "q\n"
        ),
        capture_output=True,
        check=True,
        text=True,
    )

    earlier_task = result.stdout.index("- 2026-09-12 15:00 | Submit essay")
    later_task = result.stdout.index("- 2026-09-12 16:00 | Study for biology")

    assert "Objective added." in result.stdout
    assert earlier_task < later_task