#!/usr/bin/env bash
# run.sh - Starts both the MAF backend and CopilotKit frontend for local development

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting MAF + CopilotKit Agentic Application...${NC}"

# Check for OpenAI API key
if ! grep -q "^OPENAI_API_KEY=sk-" agent/.env 2>/dev/null && [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not found!${NC}"
    echo "Please copy agent/.env.example to agent/.env and set your OPENAI_API_KEY."
    exit 1
fi

# Function to clean up background processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    echo -e "${GREEN}Shutdown complete.${NC}"
}
trap cleanup EXIT

# Function to free up ports
free_port() {
    local PORT=$1
    local PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo -e "${RED}Port $PORT is currently in use by PID $PID. Killing it...${NC}"
        kill -9 $PID 2>/dev/null || true
    fi
}

# Clear ports before starting
free_port 8000
free_port 3000

# Start the Backend (FastAPI + MAF)
echo -e "${GREEN}Starting Agent Backend (Port 8000)...${NC}"
cd agent
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
uvicorn server:app --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to initialize
sleep 2

# Start the Frontend (Next.js + CopilotKit)
echo -e "${GREEN}Starting Web Frontend (Port 3000)...${NC}"
cd web
if command -v pnpm &> /dev/null; then
    pnpm dev
elif command -v npm &> /dev/null; then
    npm run dev
else
    echo -e "${RED}Error: Neither pnpm nor npm is installed.${NC}"
    exit 1
fi
