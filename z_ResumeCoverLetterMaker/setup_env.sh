#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Creating virtual environment using uv..."
uv venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies from requirements.txt..."
uv pip install -r requirements.txt

echo "Setup complete! To activate the environment, run: source .venv/bin/activate"
