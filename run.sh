#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"
SCRIPT="run_pipeline.py"

# Ensure pyenv is available
if ! command -v pyenv >/dev/null 2>&1; then
    echo "Error: pyenv is not installed."
    exit 1
fi

# Ensure a project Python version is configured
if [ ! -f ".python-version" ]; then
    echo "Error: No .python-version file found."
    echo "Run: pyenv local 3.13.7"
    exit 1
fi

PYTHON="$(pyenv which python)"

echo "Using Python:"
"$PYTHON" --version

# Recreate broken or missing virtual environment
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Creating virtual environment..."
    rm -rf "$VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing dependencies..."
python -m pip install -r requirements.txt
pip show corvium-core

echo "Running pipeline..."
python "$SCRIPT" "$@"