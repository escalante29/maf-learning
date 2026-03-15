"""AG-UI endpoint — exposes the PM Copilot workflow via the AG-UI protocol.

This module wraps the existing MAF HandoffBuilder workflow as an AG-UI-compatible
agent and mounts it on a FastAPI endpoint.

The `mount_agui_endpoint` function adds the AG-UI route to a FastAPI app.
"""

from __future__ import annotations

from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework_ag_ui._agent import AgentFrameworkAgent
from orchestration.handoff_workflow import build_pm_workflow

class StatelessWorkflowWrapper:
    """Wraps a MAF Workflow to behave statelessly for CopilotKit.
    
    CopilotKit sends the entire message history on every turn. 
    MAF HandoffBuilder normally stays paused in a stateful IDLE_WITH_PENDING_REQUESTS
    mode expecting a tool response from the user. Re-creating the workflow
    on every request ensures it evaluates the history cleanly from scratch.
    """
    def __init__(self, name: str = "default"):
        self.name = name

    async def run_agent(self, input_data: dict):
        workflow = build_pm_workflow()
        agent = workflow.as_agent()
        agent.name = self.name
        
        # Delegate to the standard AG-UI wrapper, but on a fresh instance
        wrapped = AgentFrameworkAgent(agent)
        async for event in wrapped.run_agent(input_data):
            yield event


def mount_agui_endpoint(app, path: str = "/copilotkit"):
    """Add the AG-UI endpoint to a FastAPI application.

    Creates a fresh workflow on every request, converting it to an agent 
    that satisfies the SupportsAgentRun protocol statelessly.
    """
    wrapper = StatelessWorkflowWrapper(name="default")

    add_agent_framework_fastapi_endpoint(app, wrapper, path)

    @app.get(f"{path}/info")
    async def get_agui_info():
        return {
            "version": "1.0.0",
            "agents": {
                wrapper.name: {
                    "name": wrapper.name,
                    "description": "PM Copilot Agent"
                }
            }
        }
