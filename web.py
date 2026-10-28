"""Web interface for the college student planner.

Runs a small local web server using only the Python standard library:

    python web.py            # then open http://127.0.0.1:8000
    python web.py --port 8080

Tasks are kept in memory for as long as the server runs, matching ADR-001.
"""

from __future__ import annotations

import argparse
import html
import itertools
import webbrowser
from collections.abc import Iterable
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

from app import submit_task
from planner import Planner, Task


def browser_to_cli_format(value: str) -> str:
    """Turn a browser datetime-local value ('2026-09-12T15:00') into DATE_FORMAT text."""
    return value.strip().replace("T", " ", 1)


def add_from_form(planner: Planner, title: str, due_value: str) -> tuple[bool, str]:
    """Add a task from raw form values using the same path as the CLI.

    Returns (added, message), where message is exactly what the CLI would print.
    """
    count_before = len(planner.tasks())
    message = submit_task(planner, title.strip(), browser_to_cli_format(due_value))
    return len(planner.tasks()) > count_before, message


# ---------------------------------------------------------------- rendering

def _clock(moment: datetime) -> str:
    hour = moment.hour % 12 or 12
    return f"{hour}:{moment.minute:02d} {'AM' if moment.hour < 12 else 'PM'}"


def _day_heading(moment: datetime, now: datetime) -> str:
    days_away = (moment.date() - now.date()).days
    label = moment.strftime("%A, %B ") + str(moment.day)
    if days_away == 0:
        return f"Today · {label}"
    if days_away == 1:
        return f"Tomorrow · {label}"
    return label


def render_task_list(tasks: Iterable[Task], now: datetime) -> str:
    """Return the planner as HTML, grouped by day, in the order given."""
    tasks = list(tasks)
    if not tasks:
        return (
            '<p class="empty">Nothing planned yet. Add your first objective '
            "and its deadline above, and it will slot into place here.</p>"
        )

    next_up = next((task for task in tasks if task.due_at >= now), None)
    groups = []
    for day, day_tasks in itertools.groupby(tasks, key=lambda task: task.due_at.date()):
        day_tasks = list(day_tasks)
        rows = []
        for task in day_tasks:
            state = ""
            if task is next_up:
                state = '<span class="chip chip-next">Next up</span>'
            elif task.due_at < now:
                state = '<span class="chip chip-late">Overdue</span>'
            rows.append(
                f'<li class="task{" is-next" if task is next_up else ""}'
                f'{" is-late" if task.due_at < now else ""}">'
                f'<time datetime="{task.due_at.isoformat()}">{_clock(task.due_at)}</time>'
                f'<span class="title">{html.escape(task.title)}</span>{state}</li>'
            )
        groups.append(
            f'<section class="day"><h2>{_day_heading(day_tasks[0].due_at, now)}</h2>'
            f'<ol class="tasks">{"".join(rows)}</ol></section>'
        )
    return "".join(groups)


def render_page(
    tasks: Iterable[Task],
    now: datetime,
    notice: str | None = None,
    error: str | None = None,
    title_value: str = "",
    due_value: str = "",
) -> str:
    """Return the full planner page."""
    tasks = list(tasks)
    banner = ""
    if error:
        banner = f'<p class="banner banner-error" role="alert">{html.escape(error)}</p>'
    elif notice:
        banner = f'<p class="banner banner-ok" role="status">{html.escape(notice)}</p>'
    count = len(tasks)
    summary = f"{count} objective{'s' if count != 1 else ''}, earliest deadline first"
    return PAGE_TEMPLATE.format(
        banner=banner,
        title_value=html.escape(title_value, quote=True),
        due_value=html.escape(due_value, quote=True),
        summary=summary,
        task_list=render_task_list(tasks, now),
    )


# ------------------------------------------------------------------ server

def make_handler(planner: Planner, clock=datetime.now) -> type[BaseHTTPRequestHandler]:
    """Build a request handler bound to one in-memory planner."""

    class PlannerHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlsplit(self.path)
            if url.path != "/":
                self._send(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
                return
            notice = "Objective added." if parse_qs(url.query).get("added") else None
            self._send(HTTPStatus.OK, render_page(planner.tasks(), clock(), notice=notice))

        def do_POST(self) -> None:
            if urlsplit(self.path).path != "/tasks":
                self._send(HTTPStatus.NOT_FOUND, "<h1>Not found</h1>")
                return
            length = int(self.headers.get("Content-Length", 0))
            form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            title = form.get("title", [""])[0]
            due_value = form.get("due_at", [""])[0]

            added, message = add_from_form(planner, title, due_value)
            if added:
                # Redirect so refreshing the page does not add the task twice.
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/?added=1")
                self.end_headers()
                return
            page = render_page(
                planner.tasks(), clock(), error=message, title_value=title, due_value=due_value
            )
            self._send(HTTPStatus.BAD_REQUEST, page)

        def _send(self, status: HTTPStatus, body: str) -> None:
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args) -> None:  # keep the terminal quiet
            pass

    return PlannerHandler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the planner as a local website.")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="don't open a browser tab")
    args = parser.parse_args()

    server = HTTPServer(("127.0.0.1", args.port), make_handler(Planner()))
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"College Student Planner running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Tasks were kept in memory only and have been cleared.")
    finally:
        server.server_close()


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>College Student Planner</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
  /* Layout: one narrow column like a planner page; form card on top, the day-by-day agenda below. */
  :root {{
    --paper: #f3f6fb; --sheet: #ffffff; --ink: #172036; --muted: #5b6680;
    --rule: #d9e0ec; --accent: #2747d6; --accent-soft: #e4e9ff;
    --mark: #ffe066; --late: #b42318; --late-soft: #fde8e6; --ok: #146c43; --ok-soft: #e1f4ea;
    --display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", sans-serif;
    --body: "Atkinson Hyperlegible", "Helvetica Neue", Arial, sans-serif;
    --mono: "JetBrains Mono", ui-monospace, Menlo, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --paper: #0f1424; --sheet: #171e33; --ink: #e7ecf7; --muted: #9aa6c0;
      --rule: #2a3450; --accent: #8fa5ff; --accent-soft: #232d55;
      --mark: #8a7413; --late: #ff8a7a; --late-soft: #3a1d1d; --ok: #6fd3a0; --ok-soft: #173327;
      color-scheme: dark;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--paper); color: var(--ink);
    font: 17px/1.5 var(--body);
    background-image: linear-gradient(var(--rule) 1px, transparent 1px);
    background-size: 100% 32px; background-attachment: fixed;
  }}
  main {{ max-width: 680px; margin: 0 auto; padding: 48px max(16px, env(safe-area-inset-right, 0px)) 64px max(16px, env(safe-area-inset-left, 0px)); display: grid; gap: 28px; }}
  header h1 {{ font: 800 clamp(2rem, 6vw, 2.8rem)/1.05 var(--display); margin: 0; letter-spacing: -0.02em; text-wrap: balance; }}
  header p {{ margin: 8px 0 0; color: var(--muted); }}
  form {{
    background: var(--sheet); border: 1px solid var(--rule); border-radius: 14px;
    padding: 20px; display: grid; grid-template-columns: 1fr auto; gap: 14px 12px; align-items: end;
    box-shadow: 0 10px 30px -18px rgb(23 32 54 / 0.35);
  }}
  .field {{ display: grid; gap: 6px; min-width: 0; }}
  .field-title {{ grid-column: 1 / -1; }}
  label {{ font-size: 0.78rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }}
  input {{
    font: inherit; color: var(--ink); background: var(--paper); width: 100%;
    border: 1.5px solid var(--rule); border-radius: 10px; padding: 10px 12px;
  }}
  input:focus-visible, button:focus-visible {{ outline: 3px solid var(--accent); outline-offset: 2px; border-color: var(--accent); }}
  button {{
    font: 700 1rem var(--body); color: #fff; background: var(--accent); border: 0; border-radius: 10px;
    padding: 12px 20px; cursor: pointer;
  }}
  @media (prefers-color-scheme: dark) {{ button {{ color: #0f1424; }} }}
  button:hover {{ filter: brightness(1.08); }}
  .banner {{ margin: 0; padding: 12px 16px; border-radius: 10px; font-weight: 700; }}
  .banner-ok {{ background: var(--ok-soft); color: var(--ok); }}
  .banner-error {{ background: var(--late-soft); color: var(--late); }}
  .summary {{ margin: 0; color: var(--muted); font-size: 0.9rem; }}
  .day h2 {{ font: 600 1.15rem var(--display); margin: 0 0 8px; }}
  .agenda {{ display: grid; gap: 22px; }}
  .tasks {{ list-style: none; margin: 0; padding: 0; background: var(--sheet); border: 1px solid var(--rule); border-radius: 12px; }}
  .task {{ display: grid; grid-template-columns: 6.5em 1fr auto; gap: 12px; align-items: baseline; padding: 12px 16px; }}
  .task + .task {{ border-top: 1px solid var(--rule); }}
  .task time {{ font: 500 0.9rem var(--mono); color: var(--muted); font-variant-numeric: tabular-nums; }}
  .task .title {{ min-width: 0; overflow-wrap: anywhere; justify-self: start; }}
  .task.is-next .title {{ background: linear-gradient(transparent 55%, var(--mark) 55%); font-weight: 700; }}
  .task.is-late .title {{ color: var(--muted); text-decoration: line-through; text-decoration-color: var(--late); }}
  .chip {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }}
  .chip-next {{ background: var(--accent-soft); color: var(--accent); }}
  .chip-late {{ background: var(--late-soft); color: var(--late); }}
  .empty {{ margin: 0; padding: 20px; color: var(--muted); background: var(--sheet); border: 1.5px dashed var(--rule); border-radius: 12px; }}
  footer {{ color: var(--muted); font-size: 0.85rem; }}
  @media (max-width: 520px) {{
    form {{ grid-template-columns: 1fr; }}
    .task {{ grid-template-columns: 5.5em 1fr; }}
    .chip {{ grid-column: 2; justify-self: start; }}
  }}
</style>
</head>
<body>
<main>
  <header>
    <h1>College Student Planner</h1>
    <p>Add an objective and its deadline. Your list sorts itself, earliest first.</p>
  </header>
  {banner}
  <form method="post" action="/tasks">
    <div class="field field-title">
      <label for="title">Objective</label>
      <input id="title" name="title" value="{title_value}" placeholder="Submit history essay" required autofocus>
    </div>
    <div class="field">
      <label for="due_at">Due date and time</label>
      <input id="due_at" name="due_at" type="datetime-local" value="{due_value}" required>
    </div>
    <button type="submit">Add objective</button>
  </form>
  <p class="summary">{summary}</p>
  <div class="agenda">{task_list}</div>
  <footer>Tasks live in memory while the server runs; stopping it clears them.</footer>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    main()
