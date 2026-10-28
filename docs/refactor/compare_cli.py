"""Run the old and new app.py on the same stdin scripts and compare stdout + exit code."""
import subprocess
import sys
from pathlib import Path

before_dir, after_dir = Path(sys.argv[1]), Path(sys.argv[2])

CASES = {
    "two tasks, reverse order": "Study for biology\n2026-09-12 16:00\nSubmit essay\n2026-09-12 15:00\nq\n",
    "quit immediately": "q\n",
    "uppercase Q quits": "Q\n",
    "quit with spaces": "   q   \n",
    "bad date text": "Essay\nnext Tuesday\nq\n",
    "empty title": "   \n2026-09-12 15:00\nq\n",
    "empty title + bad date": "\nnope\nq\n",
    "title padded with spaces": "  Lab report  \n  2026-10-01 09:30  \nq\n",
    "equal deadlines keep order": "A\n2026-09-12 15:00\nB\n2026-09-12 15:00\nq\n",
    "mixed valid and invalid": "Read ch.3\n2026-09-13 08:00\nX\n2026-13-40 99:99\nQuiz\n2026-09-12 23:59\nq\n",
    "title 'quit' is a task": "quit\n2026-09-12 15:00\nq\n",
    "EOF without quit (crash path)": "Essay\n2026-09-12 15:00\n",
    "EOF mid-task (crash path)": "Essay\n",
}

def run(app_dir: Path, stdin: str):
    r = subprocess.run([sys.executable, str(app_dir / "app.py")], input=stdin,
                       capture_output=True, text=True, cwd=app_dir)
    last_err = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
    return r.stdout, r.returncode, last_err

failures = 0
for name, stdin in CASES.items():
    b, a = run(before_dir, stdin), run(after_dir, stdin)
    same = b == a
    failures += not same
    print(f"[{'SAME' if same else 'DIFF'}] {name:32} exit={a[1]} stdout={len(a[0])} bytes"
          + (f"  err={a[2]!r}" if a[2] else ""))
    if not same:
        print("  BEFORE:", b, "\n  AFTER: ", a)
print(f"\n{len(CASES) - failures}/{len(CASES)} scenarios byte-identical (stdout, exit code, final stderr line)")
sys.exit(1 if failures else 0)
