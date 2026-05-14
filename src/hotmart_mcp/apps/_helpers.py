"""Shared helpers for Prefab UI apps — schema-validated."""
from __future__ import annotations

from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)


def format_brl(value: float | int | None) -> str:
    v = value or 0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def epoch_ms_to_date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")


def parse_items(raw: Any, model: type[T]) -> list[T]:
    """Validate an API response into a list of typed models.

    Hotmart's wrappers vary by endpoint — sometimes `{"items": [...]}`,
    sometimes a raw `[...]`. This normalises both into `list[model]`.

    Pydantic raises ValidationError if the response shape no longer
    matches the spec — surfaces schema drift loud instead of silently
    returning empty/zeroed data.
    """
    if isinstance(raw, dict):
        raw_items = raw.get("items", [])
    elif isinstance(raw, list):
        raw_items = raw
    else:
        raw_items = []
    return TypeAdapter(list[model]).validate_python(raw_items)


def safe_sum(items, getter, *, label: str = "value") -> float:
    """Sum a numeric attribute from typed items, asserting non-zero
    when count > 0. Returns 0 for empty input. If items exist but
    every value is None/0, returns 0 — caller can render a warning."""
    total = 0.0
    for it in items:
        v = getter(it)
        if v is not None:
            total += v
    return total
