#!/bin/sh
set -e

# Check if UV is installed
if ! command -v uv >/dev/null 2>&1; then
  echo "UV is not installed. Please install UV using: pip install uv"
  exit 1
fi

# Install Python dependencies
uv pip install --system -e .

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed. Please follow the instructions in the README to install Node.js."
  exit 1
fi

# Install Node.js dependencies
npm install

# Set up pre-commit
uv pip install --system pre-commit
pre-commit install -t pre-commit -t commit-msg

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Development environment setup complete!"
