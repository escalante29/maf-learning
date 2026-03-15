"""FastAPI server — entry point for the MAF + CopilotKit backend.

Run with:
    uvicorn server:app --reload --port 8000
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agui_endpoint import mount_agui_endpoint
from config import settings

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("maf_copilotkit")
logger.setLevel(logging.INFO)

# ── FastAPI app ──────────────────────────────────────────────────────────
app = FastAPI(
    title="MAF CopilotKit Agent",
    description="Microsoft Agent Framework backend with AG-UI for CopilotKit",
    version="0.1.0",
)

# CORS — allow the Next.js frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount AG-UI endpoint for CopilotKit
mount_agui_endpoint(app, path="/copilotkit")


@app.get("/")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "MAF CopilotKit Agent"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=settings.port, reload=True)
