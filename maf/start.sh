#!/usr/bin/env bash

# Exit on error
set -e

echo "🚀 Starting PM Copilot Local Environment..."

# Ensure we are in the correct directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "⚠️  .venv not found. Please create it and install requirements."
    exit 1
fi

# Kill any existing process running on the targeted port (3978) to avoid Conflicts
echo "🔍 Checking for existing processes on port 3978..."
PID=$(lsof -t -i:3978 || true)
if [ -n "$PID" ]; then
    echo "🛑 Killing existing process $PID on port 3978..."
    kill -9 $PID
fi

# Run the unified server which hosts both the API and the Web UI
echo "🌐 Starting backend and frontend server..."
echo "👉 The Web UI will be available at: http://localhost:3978/chat"

# We execute the python binary directly from .venv to avoid issues with 
# broken 'activate' scripts that might have hardcoded paths from folder copies.
.venv/bin/python app.py --server
