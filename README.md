# IAP1
EECE-4081-002 Individual Project

Date Started: 8/31/26

Declared stack - 
Langauge: Python
IDE: VS Code
OS/Platform: macOS

Concept - 
Planner for college students
One paragraph concept brief - 
I would like to make a simple planner for college students to use. It will allow the user to add what they need to do, and allow them to put a due date to said objective. It will automatically organize the student's planner based on chronologic order. Example, if you add an obective that is due at 04:00 PM, but add an objective at 03:00 PM, the 3pm objective will be shown above the 04:00 PM. 

Toolchain -
Language runtime: python3
Package manager: pip
Test runner: pytest
version control: GitHub

## Current implementation

The planner currently includes:

- A `Task` domain model with a title and due date/time.
- A `Planner` that validates objectives and returns them in chronological order.
- A command-line interface for adding objectives and displaying the sorted planner.
- Pytest coverage for chronological ordering, equal deadlines, and empty titles.

## Run the planner

Activate the virtual environment and run:

```bash
source .venv/bin/activate
python app.py
```

Enter due dates using `YYYY-MM-DD HH:MM`. Enter `q` when you are finished adding objectives.

## Run tests

```bash
python -m pytest
```