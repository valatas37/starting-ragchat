#!/usr/bin/env python3
"""Quality check script that runs all code quality tools."""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n[CHECK] {description}")
    print(f"Running: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print(f"[PASS] {description} passed")
            return True
        else:
            print(f"[FAIL] {description} failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running {description}: {e}")
        return False


def main():
    """Run all quality checks."""
    print("Running code quality checks...")

    checks = [
        (["uv", "run", "black", "--check", "."], "Black code formatting check"),
        (["uv", "run", "isort", "--check-only", "."], "Import sorting check"),
        (["uv", "run", "flake8", "backend/", "scripts/"], "Flake8 linting"),
        (["uv", "run", "mypy", "backend/"], "MyPy type checking"),
    ]

    all_passed = True

    for command, description in checks:
        success = run_command(command, description)
        if not success:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All quality checks passed!")
        sys.exit(0)
    else:
        print("[FAILURE] Some quality checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
