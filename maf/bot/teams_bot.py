"""Teams Bot — MS Teams activity handler bridging Teams ↔ MAF workflow.

This module provides the TeamsBot class that handles incoming Teams messages
and routes them through the PM Copilot Handoff workflow.

NOTE: This relies on the Microsoft 365 Agents SDK (`microsoft_agents`).
"""

from __future__ import annotations

import logging
from typing import Any

from microsoft_agents.hosting.core.activity_handler import ActivityHandler
from microsoft_agents.hosting.core.message_factory import MessageFactory
from microsoft_agents.activity import Activity

from agent_framework import AgentResponse
from agent_framework.orchestrations import HandoffAgentUserRequest
from orchestration.handoff_workflow import build_pm_workflow

logger = logging.getLogger(__name__)


class TeamsBot(ActivityHandler):
    """Activity handler that bridges MS Teams ↔ MAF Handoff workflow."""

    def __init__(self):
        super().__init__()
        # In a real app with concurrent users, workflow state should be persisted
        # (e.g. MemoryStorage, BlobStorage). Here we use an in-memory dict keyed by conv ID.
        self._active_workflows: dict[str, Any] = {}
        logger.info("TeamsBot initialized (microsoft_agents)")

    def _get_or_create_workflow(self, conversation_id: str) -> Any:
        if conversation_id not in self._active_workflows:
            logger.info(f"Creating new workflow for conversation {conversation_id}")
            self._active_workflows[conversation_id] = build_pm_workflow()
        return self._active_workflows[conversation_id]

    async def on_message_activity(self, turn_context: TurnContext) -> None:
        """Handle incoming message from Teams/WebChat."""
        user_text = turn_context.activity.text
        if not user_text:
            return

        conversation_id = turn_context.activity.conversation.id
        workflow = self._get_or_create_workflow(conversation_id)

        # To handle multi-turn conversations cleanly, we check if the workflow
        # is IDLE_WITH_PENDING_REQUESTS. For simplicity in this demo, we just
        # call workflow.run(), assuming it's either the first message or the workflow
        # manages its own resume state if we pass responses dict.
        #
        # Note: MAF's workflow.run() currently requires passing previous requests if pending.
        # Since this is a demo of the adapter, we start a fresh run or await the result.

        try:
            # Here we assume a simple synchronous progression for demo purposes
            events = await workflow.run(user_text)

            # Process output events to send back to the user
            for event in events:
                if event.type == "output" and isinstance(event.data, AgentResponse):
                    for msg in event.data.messages:
                        if msg.text:
                            # Use MessageFactory to create a rich response
                            reply = MessageFactory.text(msg.text)
                            reply.from_property = {"name": msg.author_name or msg.role}
                            await turn_context.send_activity(reply)

                elif event.type == "request_info" and isinstance(event.data, HandoffAgentUserRequest):
                    resp = event.data.agent_response
                    if resp and resp.messages:
                        for msg in resp.messages:
                            if msg.text:
                                reply = MessageFactory.text(msg.text)
                                reply.from_property = {"name": msg.author_name or msg.role}
                                await turn_context.send_activity(reply)
                            
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
            await turn_context.send_activity(
                MessageFactory.text("Sorry, an error occurred while processing your request.")
            )

    async def on_members_added_activity(self, members_added: list, turn_context: TurnContext) -> None:
        """Send welcome message when bot is added to a conversation."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text("Welcome to PM Copilot! How can I help you today?")
                )
