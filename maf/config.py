"""Application configuration loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the PM Assistant application.

    Values are loaded from environment variables and can be overridden by
    a `.env` file located in the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── OpenAI ───────────────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_chat_model_id: str = "gpt-4o"

    # ── Microsoft Graph ──────────────────────────────────────────────────
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # ── MS Teams Bot Framework ───────────────────────────────────────────
    ms_teams_app_id: str = ""
    ms_teams_app_password: str = ""

    # ── Application ──────────────────────────────────────────────────────
    graph_mode: str = "mock"  # "mock" or "live"
    port: int = 3978

    @property
    def is_mock_mode(self) -> bool:
        """Return True when Graph calls should be mocked."""
        return self.graph_mode.lower() == "mock"


# Singleton – import `settings` everywhere
settings = Settings()
