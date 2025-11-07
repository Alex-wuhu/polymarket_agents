"""Client for interacting with the public Polymarket Data API."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from polymarket_agents.utils.logging import log_error


class DataAPI:
    """Minimal wrapper around the Polymarket data-api service."""

    def __init__(self) -> None:
        self.base_url = "https://data-api.polymarket.com"
        self.positions_endpoint = f"{self.base_url}/positions"

    def get_positions(self, user: str, **params: Any) -> List[dict]:
        """Return positions associated with the provided on-chain address."""
        if not user:
            raise ValueError("User address must be provided to fetch positions.")

        query: Dict[str, Any] = {"user": user}
        query.update(params)

        response = httpx.get(
            self.positions_endpoint,
            params=query,
            timeout=httpx.Timeout(30.0, read=30.0),
        )
        if response.status_code != 200:
            log_error(
                f"Data API returned HTTP {response.status_code} for "
                f"{self.positions_endpoint}"
            )
            raise RuntimeError("Unable to fetch positions from Data API.")
        payload = response.json()
        if not isinstance(payload, list):
            raise RuntimeError("Unexpected payload when fetching positions.")
        return payload
