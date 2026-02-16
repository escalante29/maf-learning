"""Teams Bot — MS Teams activity handler bridging Teams ↔ MAF workflow.

This module provides the TeamsBot class that handles incoming Teams messages
and routes them through the PM Copilot Handoff workflow.

NOTE: This is a scaffold for future Teams deployment. Console and DevUI modes
are fully functional without this module.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TeamsBot:
    """Activity handler that bridges MS Teams ↔ MAF Handoff workflow.

    Future implementation will:
    1. Receive activity from Bot Framework Adapter
    2. Extract user message from the activity
    3. Feed it into the HandoffBuilder workflow
    4. Stream or batch agent responses back to the Teams conversation
    5. Maintain per-conversation workflow state
    """

    def __init__(self):
        self._active_workflows: dict[str, Any] = {}
        logger.info("TeamsBot initialized (scaffold mode)")

    async def on_message_activity(self, turn_context: Any) -> None:
        """Handle incoming message from Teams.

        Args:
            turn_context: The Bot Framework TurnContext containing the activity.
        """
        # TODO: Implement when Bot Framework adapter is set up
        # 1. Extract conversation_id and user message
        # 2. Get or create workflow for this conversation
        # 3. Run workflow with user message
        # 4. Send agent responses back via turn_context.send_activity()
        logger.info("TeamsBot.on_message_activity called (scaffold)")

    async def on_members_added_activity(self, members_added: list, turn_context: Any) -> None:
        """Send welcome message when bot is added to a conversation."""
        # TODO: Send a welcome card with PM Copilot branding
        logger.info("TeamsBot.on_members_added_activity called (scaffold)")
