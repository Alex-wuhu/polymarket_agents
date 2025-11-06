"""Tools for discovering potentially profitable markets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.utils.logging import log_print
from polymarket_agents.utils.objects import Market


@dataclass(slots=True)
class MarketOpportunity:
    """Represents a potential trading opportunity."""

    market: Market
    total_probability: float


def _normalize_prices(prices: Sequence[float]) -> list[float]:
    """Convert any numeric-like sequence into a clean list of floats."""
    normalized: list[float] = []
    for value in prices:
        try:
            normalized.append(float(value))
        except (TypeError, ValueError):
            continue
    return normalized


def find_probabilistic_arbitrage(
    target_results: int = 2,
    batch_limit: int = 200,
    start_offset: int = 0,
) -> list[MarketOpportunity]:
    """Identify markets where outcome prices sum away from parity."""
    gamma = GammaMarketClient()
    opportunities: list[MarketOpportunity] = []
    offset = max(start_offset, 0)

    while len(opportunities) < target_results:
        log_print(
            f"Fetching tradable markets (limit={batch_limit}, offset={offset})..."
        )
        markets = gamma.get_tradable_markets(limit=batch_limit, offset=offset)
        if not markets:
            log_print("No more markets returned by Gamma; stopping search.")
            break

        log_print(f"Processing {len(markets)} markets for probability sums...")
        for market in markets:
            prices = market.outcomePrices or []
            normalized_prices = _normalize_prices(prices)
            if not normalized_prices:
                continue

            total_probability = sum(normalized_prices)
            if total_probability > 1.01 or total_probability < 0.99:
                log_print(
                    f"  Potential arbitrage in market {market.id} "
                    f"(sum={total_probability:.4f})"
                )
                opportunities.append(
                    MarketOpportunity(
                        market=market,
                        total_probability=total_probability,
                    )
                )
                if len(opportunities) >= target_results:
                    break

        offset += batch_limit

        if len(markets) < batch_limit:
            log_print(
                "Reached the end of available markets before hitting the target count."
            )
            break

    log_print(
        f"Finished scanning: discovered {len(opportunities)} "
        f"opportunit{'y' if len(opportunities)==1 else 'ies'}."
    )
    return opportunities


def describe_opportunities(opportunities: Iterable[MarketOpportunity]) -> None:
    """Pretty-print a collection of market opportunities."""
    opportunities = list(opportunities)
    if not opportunities:
        log_print("No probabilistic arbitrage markets detected.")
        return

    log_print("Detailing probabilistic arbitrage candidates:")
    for opportunity in opportunities:
        market = opportunity.market
        prices = ", ".join(f"{price:.4f}" for price in market.outcomePrices or [])
        log_print("=" * 72)
        log_print(f"Market ID     : {market.id}")
        log_print(f"Question      : {market.question or '-'}")
        log_print(f"Slug          : {market.slug or '-'}")
        log_print(f"Total Prob    : {opportunity.total_probability:.4f}")
        log_print(f"Outcome Prices: {prices or '-'}")
        log_print(f"Volume        : {market.volume if market.volume is not None else '-'}")


if __name__ == "__main__":
    market_opportunities = find_probabilistic_arbitrage(limit=1000)
    describe_opportunities(market_opportunities)
