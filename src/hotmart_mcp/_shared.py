"""Shared lazy singleton for the Hotmart API client."""

from __future__ import annotations

from hotmart_mcp.client import HotmartClient

_client: HotmartClient | None = None


def get_client() -> HotmartClient:
    global _client
    if _client is None:
        _client = HotmartClient()
    return _client
