#!/bin/sh
set -e

# Check if Poetry is installed
if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry is not installed. Please follow the instructions in the README to install Poetry."
  exit 1
fi

# Install Python dependencies
poetry install

# Check if Node.js is installed
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed. Please follow the instructions in the README to install Node.js."
  exit 1
fi

# Install Node.js dependencies
npm install

# Set up pre-commit
poetry run pre-commit install -t pre-commit -t commit-msg

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
  cp .env.example .env
fi

echo "Development environment setup complete!"
