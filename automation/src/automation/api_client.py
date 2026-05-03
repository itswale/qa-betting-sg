"""Minimal HTTP client for reset + catalog + balance (used by tests)."""

from __future__ import annotations

from typing import Any, Literal

import requests

Selection = Literal["HOME", "DRAW", "AWAY"]


class BettingAPI:
    def __init__(self, base_url: str, user_id: str) -> None:
        self._base = base_url.rstrip("/")
        self._headers = {"x-user-id": user_id, "Content-Type": "application/json"}

    def matches(self) -> list[dict[str, Any]]:
        r = requests.get(f"{self._base}/api/matches", headers=self._headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def balance(self) -> dict[str, Any]:
        r = requests.get(f"{self._base}/api/balance", headers=self._headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def reset_balance(self) -> None:
        r = requests.post(f"{self._base}/api/reset-balance", headers=self._headers, timeout=30)
        r.raise_for_status()
