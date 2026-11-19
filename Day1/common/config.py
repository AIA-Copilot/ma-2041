"""
MA-2041 — the single .env loader for every Python lab.

Configuration is optional for these local exercises; do not create .env.

Usage:
    from common.config import settings
    settings.get("GRAPH_TENANT_ID")          # -> None if unset
    settings.require("GRAPH_TENANT_ID")      # -> raises ConfigMissing if unset

Never put a real secret in .env.example. Never print a secret value.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - requirements.txt pins python-dotenv
    load_dotenv = None

# Day1/.env — resolved relative to this file, so it loads no matter
# which directory pytest or VS Code was launched from.
CODE_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = CODE_ROOT / ".env"

_loaded = False


class ConfigMissing(RuntimeError):
    """Raised when a lab needs a setting that is not configured."""


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    if load_dotenv is not None and ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)
    _loaded = True


class Settings:
    """Thin, explicit wrapper over os.environ + Day1/.env."""

    @property
    def env_file(self) -> Path:
        return ENV_FILE

    @property
    def env_file_loaded(self) -> bool:
        _ensure_loaded()
        return ENV_FILE.exists()

    def get(self, key: str, default: str | None = None) -> str | None:
        _ensure_loaded()
        value = os.environ.get(key, default)
        return value if value not in ("", None) else default

    def require(self, key: str) -> str:
        value = self.get(key)
        if not value:
            raise ConfigMissing(
                f"{key} is not set. Copy .env.example to .env in Day1 and fill it in, "
                f"or set {key} in your shell. Expected file: {ENV_FILE}"
            )
        return value

    def has_all(self, *keys: str) -> bool:
        return all(self.get(k) for k in keys)

    def model_endpoint_configured(self) -> bool:
        """True only when a real model endpoint is fully configured (Labs 7/8)."""
        return self.has_all(
            "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"
        )

    def graph_configured(self) -> bool:
        """True only when Lab 5 live ingestion is fully configured."""
        return self.has_all("GRAPH_TENANT_ID", "GRAPH_CLIENT_ID", "GRAPH_CLIENT_SECRET")


settings = Settings()
