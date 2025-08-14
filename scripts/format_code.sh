#!/bin/bash
# Code formatting script for Unix-like systems

cd "$(dirname "$0")/.."

echo "🎨 Formatting code..."

# Organize imports
echo -e "\n🔧 Organizing imports with isort"
uv run isort .

# Format code
echo -e "\n🔧 Formatting code with black"
uv run black .

echo -e "\n${'='*50}"
echo "🎉 Code formatting completed!"