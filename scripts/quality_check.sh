#!/bin/bash
# Quality check script for Unix-like systems

cd "$(dirname "$0")/.."

echo "🚀 Running code quality checks..."

# Black formatting check
echo -e "\n🔍 Black code formatting check"
uv run black --check .
BLACK_EXIT=$?

# Import sorting check
echo -e "\n🔍 Import sorting check"
uv run isort --check-only .
ISORT_EXIT=$?

# Flake8 linting
echo -e "\n🔍 Flake8 linting"
uv run flake8 .
FLAKE8_EXIT=$?

# MyPy type checking
echo -e "\n🔍 MyPy type checking"
uv run mypy backend/
MYPY_EXIT=$?

echo -e "\n${'='*50}"

if [ $BLACK_EXIT -eq 0 ] && [ $ISORT_EXIT -eq 0 ] && [ $FLAKE8_EXIT -eq 0 ] && [ $MYPY_EXIT -eq 0 ]; then
    echo "🎉 All quality checks passed!"
    exit 0
else
    echo "💥 Some quality checks failed!"
    exit 1
fi