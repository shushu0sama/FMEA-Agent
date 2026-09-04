"""Cross-platform verification entry for MVP-0.

Usage:
    python scripts/verify.py

Runs, in order, and fails fast:
    pytest
    ruff check .
    mypy src

Each step uses the same Python interpreter, so this works on Windows and WSL
without per-platform launchers.
"""

import subprocess
import sys


def main() -> int:
    commands = [
        ("pytest", [sys.executable, "-m", "pytest", "-q"]),
        ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
        ("mypy", [sys.executable, "-m", "mypy", "src"]),
    ]
    for name, command in commands:
        print(f"[verify] running: {' '.join(command)}", flush=True)
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"[verify] {name} FAILED (exit code {exc.returncode})", file=sys.stderr)
            return 1
    print("[verify] all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
