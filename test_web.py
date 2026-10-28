import threading
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import HTTPServer

import pytest

from planner import Planner
from web import add_from_form, make_handler, render_page

NOW = datetime(2026, 9, 12, 12, 0)


@pytest.fixture
def server_url():
    server = HTTPServer(("127.0.0.1", 0), make_handler(Planner(), clock=lambda: NOW))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()


def post_task(base_url: str, title: str, due_at: str) -> tuple[int, str]:
    data = urllib.parse.urlencode({"title": title, "due_at": due_at}).encode()
    try:
        with urllib.request.urlopen(f"{base_url}/tasks", data=data) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()


def test_form_values_go_through_the_same_path_as_the_cli() -> None:
    planner = Planner()

    added, message = add_from_form(planner, "  Submit essay ", "2026-09-12T15:00")

    assert added
    assert message == "Objective added."
    assert planner.tasks()[0].title == "Submit essay"
    assert planner.tasks()[0].due_at == datetime(2026, 9, 12, 15, 0)


def test_blank_title_is_rejected_with_the_cli_message() -> None:
    planner = Planner()

    added, message = add_from_form(planner, "   ", "2026-09-12T15:00")

    assert not added
    assert message == "Invalid task: Task title cannot be empty"
    assert planner.tasks() == []


def test_task_titles_are_html_escaped() -> None:
    planner = Planner()
    planner.add_task("<script>alert(1)</script>", datetime(2026, 9, 12, 15, 0))

    page = render_page(planner.tasks(), NOW)

    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_website_adds_tasks_and_lists_them_in_deadline_order(server_url: str) -> None:
    status, _ = post_task(server_url, "Study for biology", "2026-09-12T16:00")
    assert status == 200  # 303 redirect followed back to the planner page

    status, page = post_task(server_url, "Submit essay", "2026-09-12T15:00")

    assert status == 200
    assert "Objective added." in page
    assert page.index("Submit essay") < page.index("Study for biology")


def test_website_rejects_invalid_task_and_keeps_what_was_typed(server_url: str) -> None:
    status, page = post_task(server_url, "   ", "2026-09-12T15:00")

    assert status == 400
    assert "Invalid task: Task title cannot be empty" in page
    assert 'value="2026-09-12T15:00"' in page
