"""Microsoft Graph API client — shared authentication and client helper.

When GRAPH_MODE=mock (default), all Graph calls return realistic stub data
so the agent orchestration can be tested end-to-end without Azure credentials.

When GRAPH_MODE=live, an authenticated GraphServiceClient is created using
MSAL client-credentials flow.
"""

from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton
# ---------------------------------------------------------------------------
_graph_client: Any | None = None


def get_graph_client() -> Any:
    """Return a GraphServiceClient (live) or a MockGraphClient (mock)."""
    global _graph_client
    if _graph_client is not None:
        return _graph_client

    if settings.is_mock_mode:
        logger.info("Graph mode is MOCK — using stub responses.")
        _graph_client = MockGraphClient()
    else:
        _graph_client = _build_live_client()

    return _graph_client


# ---------------------------------------------------------------------------
# Live client (MSAL + msgraph-sdk)
# ---------------------------------------------------------------------------

def _build_live_client() -> Any:
    """Build an authenticated Microsoft Graph client using client credentials."""
    try:
        from azure.identity import ClientSecretCredential
        from msgraph import GraphServiceClient

        credential = ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
        )
        scopes = ["https://graph.microsoft.com/.default"]
        client = GraphServiceClient(credentials=credential, scopes=scopes)
        logger.info("Live Graph client initialised.")
        return client

    except ImportError as exc:
        raise RuntimeError(
            "msgraph-sdk and azure-identity must be installed for live Graph mode. "
            "Run: pip install msgraph-sdk azure-identity"
        ) from exc


# ---------------------------------------------------------------------------
# Mock client — returns realistic stubs
# ---------------------------------------------------------------------------

class MockGraphClient:
    """Drop-in mock that returns plausible data for every Graph operation."""

    # ── SharePoint ───────────────────────────────────────────────────────
    def create_site(self, name: str, description: str) -> dict:
        return {
            "id": f"mock-site-{name.lower().replace(' ', '-')}",
            "displayName": name,
            "description": description,
            "webUrl": f"https://contoso.sharepoint.com/sites/{name.replace(' ', '')}",
        }

    def list_sites(self) -> list[dict]:
        return [
            {"id": "site-001", "displayName": "Project Alpha", "webUrl": "https://contoso.sharepoint.com/sites/ProjectAlpha"},
            {"id": "site-002", "displayName": "Engineering Hub", "webUrl": "https://contoso.sharepoint.com/sites/EngineeringHub"},
            {"id": "site-003", "displayName": "HR Resources", "webUrl": "https://contoso.sharepoint.com/sites/HRResources"},
        ]

    def create_list(self, site_id: str, list_name: str, columns: list[str]) -> dict:
        return {
            "id": f"mock-list-{list_name.lower().replace(' ', '-')}",
            "displayName": list_name,
            "siteId": site_id,
            "columns": columns,
        }

    def upload_file(self, site_id: str, folder: str, filename: str) -> dict:
        return {
            "id": f"mock-file-{filename}",
            "name": filename,
            "webUrl": f"https://contoso.sharepoint.com/sites/{site_id}/{folder}/{filename}",
            "size": 1024,
        }

    # ── Meetings ─────────────────────────────────────────────────────────
    def list_meetings(self, user_id: str, days_back: int) -> list[dict]:
        return [
            {
                "id": "meet-001",
                "subject": "Sprint Planning",
                "startDateTime": "2026-02-14T10:00:00Z",
                "endDateTime": "2026-02-14T11:00:00Z",
                "attendees": ["alice@contoso.com", "bob@contoso.com", "charlie@contoso.com"],
            },
            {
                "id": "meet-002",
                "subject": "Design Review",
                "startDateTime": "2026-02-13T14:00:00Z",
                "endDateTime": "2026-02-13T15:00:00Z",
                "attendees": ["alice@contoso.com", "diana@contoso.com"],
            },
            {
                "id": "meet-003",
                "subject": "Daily Standup",
                "startDateTime": "2026-02-14T09:00:00Z",
                "endDateTime": "2026-02-14T09:15:00Z",
                "attendees": ["alice@contoso.com", "bob@contoso.com", "charlie@contoso.com", "diana@contoso.com"],
            },
        ]

    def get_transcript(self, meeting_id: str) -> str:
        transcripts = {
            "meet-001": (
                "Alice: Let's go over the sprint backlog. We have 12 stories remaining.\n"
                "Bob: I can take the authentication refactor, estimated at 5 points.\n"
                "Charlie: I'll handle the dashboard redesign. Should be about 8 points.\n"
                "Alice: Great. Bob, can you also review the API documentation by Thursday?\n"
                "Bob: Sure, I'll add that to my list.\n"
                "Alice: Charlie, please set up the staging environment by Wednesday.\n"
                "Charlie: Will do. I'll need access credentials from DevOps.\n"
                "Alice: I'll send those over today. Let's reconvene on Friday for the demo."
            ),
            "meet-002": (
                "Alice: Let's review the new design mockups for the onboarding flow.\n"
                "Diana: I've updated the wireframes based on last week's feedback.\n"
                "Alice: The color scheme looks much better. Can we add a progress indicator?\n"
                "Diana: Absolutely. I'll have the updated designs by Monday.\n"
                "Alice: Also, we need to align the iconography with the brand guidelines.\n"
                "Diana: I'll coordinate with the brand team on that."
            ),
            "meet-003": (
                "Alice: Good morning everyone. Quick updates — what did you work on yesterday?\n"
                "Bob: Finished the login endpoint and started on the password reset flow.\n"
                "Charlie: Completed the responsive layout for the dashboard.\n"
                "Diana: Finished the user research interviews, compiling the findings today.\n"
                "Alice: Any blockers?\n"
                "Bob: I need the SMTP config for the password reset emails.\n"
                "Alice: I'll get that to you by noon. Anything else? Great, let's go."
            ),
        }
        return transcripts.get(meeting_id, "No transcript available for this meeting.")

    def get_attendees(self, meeting_id: str) -> list[str]:
        attendees_map = {
            "meet-001": ["alice@contoso.com", "bob@contoso.com", "charlie@contoso.com"],
            "meet-002": ["alice@contoso.com", "diana@contoso.com"],
            "meet-003": ["alice@contoso.com", "bob@contoso.com", "charlie@contoso.com", "diana@contoso.com"],
        }
        return attendees_map.get(meeting_id, [])

    # ── Calendar ─────────────────────────────────────────────────────────
    def create_event(self, subject: str, start: str, end: str, attendees: list[str]) -> dict:
        return {
            "id": "evt-new-001",
            "subject": subject,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "attendees": attendees,
            "onlineMeeting": {"joinUrl": "https://teams.microsoft.com/l/meetup-join/mock-meeting-url"},
        }

    def list_events(self, user_id: str, days_ahead: int) -> list[dict]:
        return [
            {
                "id": "evt-001",
                "subject": "Sprint Retrospective",
                "start": {"dateTime": "2026-02-15T15:00:00Z"},
                "end": {"dateTime": "2026-02-15T16:00:00Z"},
                "attendees": ["alice@contoso.com", "bob@contoso.com"],
            },
            {
                "id": "evt-002",
                "subject": "Stakeholder Demo",
                "start": {"dateTime": "2026-02-16T10:00:00Z"},
                "end": {"dateTime": "2026-02-16T11:00:00Z"},
                "attendees": ["alice@contoso.com", "charlie@contoso.com", "cto@contoso.com"],
            },
        ]
