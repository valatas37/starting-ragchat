#!/usr/bin/env python3
"""Code formatting script that applies all formatting tools."""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n[FORMAT] {description}")
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
            print(f"[DONE] {description} completed")
            return True
        else:
            print(f"[FAIL] {description} failed")
            return False
    except Exception as e:
        print(f"[ERROR] Error running {description}: {e}")
        return False


def main():
    """Apply all code formatting."""
    print("Formatting code...")

    formatters = [
        (["uv", "run", "isort", "."], "Organizing imports with isort"),
        (["uv", "run", "black", "."], "Formatting code with black"),
    ]

    all_passed = True

    for command, description in formatters:
        success = run_command(command, description)
        if not success:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] Code formatting completed successfully!")
        sys.exit(0)
    else:
        print("[FAILURE] Code formatting encountered errors!")
        sys.exit(1)


if __name__ == "__main__":
    main()
