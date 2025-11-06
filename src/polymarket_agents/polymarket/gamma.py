from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional
import httpx
from polymarket_agents.utils.objects import ClobReward, Market, PolymarketEvent, Tag
from polymarket_agents.utils.logging import log_debug, log_error,log_print,print_markets

TRADABLE_MARKET_BASE_FILTER: Dict[str, Any] = {
    "active": True,
    "closed": False,
    "archived": False,
    "enableOrderBook": True,
}


class GammaMarketClient:
    """Thin wrapper around the public Gamma REST API used by the agents."""

    def __init__(self):
        """Initialise base URLs for the Gamma API."""
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.gamma_markets_endpoint = self.gamma_url + "/markets"
        self.gamma_events_endpoint = self.gamma_url + "/events"

    def parse_pydantic_market(self, market_object: dict) -> Optional[Market]:
        """Convert a raw market payload into the richer `Market` pydantic model."""
        try:
            if "clobRewards" in market_object:
                clob_rewards: list[ClobReward] = []
                for clob_rewards_obj in market_object["clobRewards"]:
                    clob_rewards.append(ClobReward(**clob_rewards_obj))
                market_object["clobRewards"] = clob_rewards

            if "events" in market_object:
                events: list[PolymarketEvent] = []
                for market_event_obj in market_object["events"]:
                    events.append(self.parse_nested_event(market_event_obj))
                market_object["events"] = events

            # These fields are returned as stringified lists from the API
            if "outcomes" in market_object:
                outcomes_field = market_object["outcomes"]
                if isinstance(outcomes_field, str):
                    try:
                        outcomes_field = json.loads(outcomes_field)
                    except json.JSONDecodeError:
                        log_error("[parse_market] Failed to decode outcomes JSON string")
                        outcomes_field = []
                if isinstance(outcomes_field, list):
                    market_object["outcomes"] = [str(outcome) for outcome in outcomes_field]
                else:
                    market_object["outcomes"] = []
            if "outcomePrices" in market_object:
                prices = market_object["outcomePrices"]
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except json.JSONDecodeError:
                        prices = []
                if isinstance(prices, list):
                    normalised_prices: list[float] = []
                    for price in prices:
                        try:
                            normalised_prices.append(float(price))
                        except (TypeError, ValueError):
                            continue
                    market_object["outcomePrices"] = normalised_prices
                else:
                    market_object["outcomePrices"] = []
            if "clobTokenIds" in market_object:
                clob_ids = market_object["clobTokenIds"]
                if isinstance(clob_ids, str):
                    try:
                        clob_ids = json.loads(clob_ids)
                    except json.JSONDecodeError:
                        clob_ids = [clob_ids]
                if isinstance(clob_ids, list):
                    market_object["clobTokenIds"] = [str(token) for token in clob_ids]
                else:
                    market_object["clobTokenIds"] = []

            return Market(**market_object)
        except Exception as err:
            log_error(f"[parse_market] Caught exception: {err}")
            log_debug("exception while handling object:", market_object)

    # Event parser for events nested under a markets api response
    def parse_nested_event(self, event_object: dict) -> PolymarketEvent:
        """Convert embedded event objects under the markets response."""
        try:
            if "tags" in event_object:
                tags: list[Tag] = []
                for tag in event_object["tags"]:
                    tags.append(Tag(**tag))
                event_object["tags"] = tags
            return PolymarketEvent(**event_object)
        except Exception as err:
            log_error(f"[parse_event] Caught exception: {err}")

    def parse_pydantic_event(self, event_object: dict) -> PolymarketEvent:
        """Convert a raw event payload into the richer `PolymarketEvent` model."""
        try:
            if "tags" in event_object:
                tags: list[Tag] = []
                for tag in event_object["tags"]:
                    tags.append(Tag(**tag))
                event_object["tags"] = tags
            if "markets" in event_object:
                parsed_markets: list[Market] = []
                for nested_market in event_object["markets"]:
                    parsed = self.parse_pydantic_market(nested_market)
                    if parsed is not None:
                        parsed_markets.append(parsed)
                event_object["markets"] = parsed_markets
            return PolymarketEvent(**event_object)
        except Exception as err:
            log_error(f"[parse_event] Caught exception: {err}")

    def filter_events_for_trading(
        self, events: Iterable[PolymarketEvent]
    ) -> list[PolymarketEvent]:
        """Filter out any events that are closed, archived, or restricted."""
        tradeable_events = [
            event
            for event in events
            if event.active
            and not event.restricted
            and not event.archived
            and not event.closed
        ]
        if tradeable_events:
            return tradeable_events

        return [
            event
            for event in events
            if event.active and not event.archived and not event.closed
        ]

    def get_tradeable_events(self, limit: int = 100) -> list[PolymarketEvent]:
        """Fetch default tradeable events and return them as `PolymarketEvent` objects."""
        payload = self._fetch(
            self.gamma_events_endpoint,
            {
                "active": True,
                "closed": False,
                "archived": False,
                "restricted": False,
                "limit": limit,
            },
        )

        parsed_events: list[PolymarketEvent] = []
        for event_obj in payload:
            parsed = self.parse_pydantic_event(event_obj)
            if parsed is not None:
                parsed_events.append(parsed)
        return self.filter_events_for_trading(parsed_events)

    def get_tradable_markets(
        self,
        limit: int = 100,
        offset: int = 0,
        parse_pydantic: bool = True,
    ) -> list[Market] | list[dict]:
        """Fetch markets that are open, live on the order book, and not yet expired."""
        params = dict(TRADABLE_MARKET_BASE_FILTER)
        params["limit"] = limit
        params["offset"] = offset
        params["end_date_min"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        )

        payload = self._fetch(self.gamma_markets_endpoint, params)

        if not parse_pydantic:
            return payload

        parsed_markets: list[Market] = []
        for market_obj in payload:
            parsed = self.parse_pydantic_market(market_obj)
            if parsed is not None:
                parsed_markets.append(parsed)
        return parsed_markets

    def _fetch(self, endpoint: str, params: Dict[str, Any]) -> list[dict]:
        """Perform a GET request against Gamma and return the JSON payload."""
        response = httpx.get(endpoint, params=params, timeout=httpx.Timeout(30.0, read=30.0))
        if response.status_code != 200:
            log_error(
                f"Error response returned from api: HTTP {response.status_code} for {endpoint}"
            )
            raise Exception(f"Unable to fetch data from {endpoint}")
        return response.json()

if __name__ == "__main__":
    gamma = GammaMarketClient()
    try:
        sample_markets = gamma.get_tradable_markets(limit=3)
        print_markets(sample_markets)
    except Exception as exc:
        log_error(f"[__main__] Failed to fetch tradable markets: {exc}")
