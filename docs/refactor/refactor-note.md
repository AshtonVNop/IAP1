# M7 Refactor Note: Separating CLI I/O from CLI Logic

## What was wrong

**Smell: a mixed-responsibility function with hard-wired console I/O. `read_task()` in `app.py` was also a command-query separation (CQS) violation.**

`read_task(planner) -> bool` did five separate jobs in one function:

1. prompting the user (`input()` called directly),
2. detecting the quit command (`"q"`, written as a literal in two places),
3. parsing the date text into a `datetime`,
4. changing the domain (`planner.add_task`),
5. reporting the result (`print()` called directly).

Then it returned a `bool` meaning "should the loop keep going?" So one call both **changed state** (it added a task) and **answered a control-flow question**, and that answer was unrelated to whether the task was actually added. `display_tasks()` had the same problem in a smaller form: building each output line and printing it were the same step.

Because `input` and `print` were global calls buried inside the logic, there was **no seam**. The only way to test any CLI behaviour was to start the whole program as a subprocess and search through its stdout, which is why `test_app.py` is written that way. The bad-date and blank-title paths had no automated coverage because each would have needed another subprocess test.

## What I did

I split `app.py` into functions that each do one job, and moved all console I/O to the edge:

| New function | Responsibility | Does I/O? |
| --- | --- | --- |
| `prompt_for_task(read)` | Ask for one entry; return `(title, due_text)` or `None` on quit | Only through the injected `read` |
| `submit_task(planner, title, due_text) -> str` | Parse, call the domain, return the feedback message | No |
| `format_task(task) -> str` | Build one display line | No |
| `render_planner(tasks) -> list[str]` | Build the planner display | No |
| `run_session(planner, read=input, write=print)` | The loop that wires the pieces together | Only through the injected `read`/`write` |

The quit sentinel now lives in a single constant, `QUIT_COMMAND`. The boolean control flag is gone: "the user quit" is now `None` from `prompt_for_task`, so the loop condition reads as what it means. `main()` is now one line. `planner.py` was not touched.

This is a structural change. Responsibilities moved into new units, and the I/O dependency was inverted so it is passed in as a parameter instead of called directly. No names were simply changed, and no code was reformatted.

## Proof that behaviour did not change

- **Same tests, unchanged, pass before and after.** The same 4 tests pass in both runs (`test-output-before.txt`, `test-output-after.txt`). The SHA-256 checksums of `test_app.py` and `test_planner.py` are the same in both files, and `git diff` on the test files is empty.
- **Extra before/after output comparison (not part of the test set).** `compare_cli.py` runs the original and refactored `app.py` on 13 input scripts. These include quitting with `Q`, padded input, bad dates, blank titles, equal deadlines, and the end-of-input crash path. It compares stdout byte for byte, the exit code and the final stderr line: 13/13 are identical (`cli-equivalence-check.txt`). To check that the comparison can fail, I changed one character (`""` → `" "`) in a copy of the new `app.py`, and the comparison flagged 9 of 13 scenarios as different.

## What is now easier, and why

- **Testing CLI behaviour without a subprocess.** The CLI logic no longer calls `input`/`print` itself, so a test can pass in fakes:
  ```python
  answers = iter(["Essay", "2026-09-12 15:00", "q"]); out = []
  run_session(Planner(), read=lambda _: next(answers), write=out.append)
  ```
  The error paths can be tested with a one-line call: `submit_task(Planner(), "Essay", "next Tuesday")` returns the `"Invalid task: ..."` message as a string. These tests would run in-process in microseconds, instead of starting a Python interpreter for each case. That also helps NFR 2 (suite runtime) as the test suite grows.
- **Changing the display format.** Display formatting is now only in `format_task`. Future features from the requirements, such as colour output or `.ics` export, can add another formatter or renderer without touching input handling or the loop.
- **Changing the input source.** Input now comes in through the `read` and `write` parameters, so another front end (a file of tasks, a GUI, a test) can supply them. Before, you would have had to rewrite `read_task`.
- **Reading the control flow.** The loop says "while there is an entry, submit it," with no hidden boolean contract to remember.

New tests that use these seams belong in the next milestone. They were deliberately **not** added here, so the test set stays identical between the before and after runs.
