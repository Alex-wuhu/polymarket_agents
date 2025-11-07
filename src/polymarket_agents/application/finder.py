"""Tools for discovering potentially profitable markets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.utils.logging import log_debug, log_print
from polymarket_agents.utils.objects import Market


@dataclass(slots=True)
class MarketOpportunity:
    """Represents a potential trading opportunity."""

    market: Market
    total_probability: float
    quotes: list["OutcomeQuote"]
    execution_side: str  # "ask" for buy-set, "bid" for sell-set
    profit_per_share: float
    max_position_size: float
    estimated_profit: float


@dataclass(slots=True)
class OutcomeQuote:
    token_id: str
    outcome_label: str
    ask_price: float | None = None
    ask_size: float | None = None
    bid_price: float | None = None
    bid_size: float | None = None


def _normalize_prices(prices: Sequence[float]) -> list[float]:
    """Convert any numeric-like sequence into a clean list of floats."""
    normalized: list[float] = []
    for value in prices:
        try:
            normalized.append(float(value))
        except (TypeError, ValueError):
            continue
    return normalized


def _iter_token_ids(market: Market) -> list[str]:
    """Return normalized CLOB token IDs for a market."""
    token_ids = market.clobTokenIds or []
    if isinstance(token_ids, str):
        token_ids = [token_ids]
    return [str(token_id) for token_id in token_ids if token_id]


def _best_order(
    orders, prefer_high: bool
) -> tuple[float | None, float | None]:
    """Return the best price/size tuple from an iterable of orders."""
    best_price: float | None = None
    best_size: float | None = None
    for order in orders or []:
        raw_price = getattr(order, "price", None)
        raw_size = getattr(order, "size", None)
        if raw_price is None and isinstance(order, dict):
            raw_price = order.get("price")
            raw_size = order.get("size")
        try:
            price = float(raw_price)
            size = float(raw_size)
        except (TypeError, ValueError, AttributeError):
            continue
        if price < 0 or size <= 0:
            continue
        if best_price is None or (
            prefer_high and price > best_price
        ) or (not prefer_high and price < best_price):
            best_price = price
            best_size = size
    return best_price, best_size


def _collect_orderbook_quotes(
    market: Market, polymarket: Polymarket, token_ids: list[str]
) -> list[OutcomeQuote]:
    """Fetch best ask/bid quotes for each outcome token."""
    quotes: list[OutcomeQuote] = []
    outcomes = market.outcomes or []

    for index, token_id in enumerate(token_ids):
        try:
            orderbook = polymarket.get_orderbook(token_id)
        except Exception as exc:  # pragma: no cover - network/HTTP guard
            log_debug(f"Failed to fetch order book for {token_id}: {exc}")
            return []

        ask_price, ask_size = _best_order(
            getattr(orderbook, "asks", None), prefer_high=False
        )
        bid_price, bid_size = _best_order(
            getattr(orderbook, "bids", None), prefer_high=True
        )

        if ask_price is None and bid_price is None:
            return []

        outcome_label = (
            outcomes[index] if index < len(outcomes) else f"Outcome {index + 1}"
        )
        quotes.append(
            OutcomeQuote(
                token_id=token_id,
                outcome_label=str(outcome_label),
                ask_price=ask_price,
                ask_size=ask_size,
                bid_price=bid_price,
                bid_size=bid_size,
            )
        )
    return quotes


def _build_opportunity(
    market: Market, quotes: Sequence[OutcomeQuote], threshold: float = 0.01
) -> MarketOpportunity | None:
    """Determine whether quotes form a viable arbitrage opportunity."""
    ask_prices = []
    ask_sizes = []
    for quote in quotes:
        if quote.ask_price is None or quote.ask_size is None:
            ask_prices = []
            break
        ask_prices.append(float(quote.ask_price))
        ask_sizes.append(float(quote.ask_size))

    if ask_prices:
        total = sum(ask_prices)
        if total < (1 - threshold):
            max_size = min(ask_sizes)
            profit_per = 1 - total
            estimated_profit = profit_per * max_size
            return MarketOpportunity(
                market=market,
                total_probability=total,
                quotes=list(quotes),
                execution_side="ask",
                profit_per_share=profit_per,
                max_position_size=max_size,
                estimated_profit=estimated_profit,
            )

    bid_prices = []
    bid_sizes = []
    for quote in quotes:
        if quote.bid_price is None or quote.bid_size is None:
            bid_prices = []
            break
        bid_prices.append(float(quote.bid_price))
        bid_sizes.append(float(quote.bid_size))

    if bid_prices:
        total = sum(bid_prices)
        if total > (1 + threshold):
            max_size = min(bid_sizes)
            profit_per = total - 1
            estimated_profit = profit_per * max_size
            return MarketOpportunity(
                market=market,
                total_probability=total,
                quotes=list(quotes),
                execution_side="bid",
                profit_per_share=profit_per,
                max_position_size=max_size,
                estimated_profit=estimated_profit,
            )

    return None


def find_probabilistic_arbitrage(
    target_results: int = 2,
    batch_limit: int = 200,
    start_offset: int = 0,
) -> list[MarketOpportunity]:
    """Identify markets where outcome prices sum away from parity."""
    gamma = GammaMarketClient()
    polymarket = Polymarket()
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
            token_ids = _iter_token_ids(market)
            if not token_ids:
                continue

            quotes = _collect_orderbook_quotes(market, polymarket, token_ids)
            if len(quotes) != len(token_ids):
                continue

            opportunity = _build_opportunity(market, quotes)
            if opportunity is None:
                continue

            log_print(
                f"  Potential arbitrage in market {market.id} "
                f"(sum={opportunity.total_probability:.4f})"
            )
            opportunities.append(opportunity)
            if len(opportunities) >= target_results:
                break

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
        quotes = opportunity.quotes
        direction = (
            "BUY complete set (hit asks)" if opportunity.execution_side == "ask"
            else "SELL complete set (lift bids)"
        )
        prices = ", ".join(
            f"{quote.outcome_label}: "
            f"{(quote.ask_price if opportunity.execution_side == 'ask' else quote.bid_price):.4f}"
            for quote in quotes
        )
        log_print("=" * 72)
        log_print(f"Market ID     : {market.id}")
        log_print(f"Question      : {market.question or '-'}")
        log_print(f"Slug          : {market.slug or '-'}")
        log_print(f"Total Prob    : {opportunity.total_probability:.4f}")
        log_print(f"Strategy      : {direction}")
        log_print(f"Outcome Prices: {prices or '-'}")
        log_print(
            f"Max Size      : {opportunity.max_position_size:.4f} "
            f"shares (per outcome)"
        )
        log_print(f"Profit/share  : {opportunity.profit_per_share:.4f}")
        log_print(f"Est. Profit   : {opportunity.estimated_profit:.4f}")
        log_print("Order book legs:")
        for quote in quotes:
            if opportunity.execution_side == "ask":
                log_print(
                    f"  BUY {quote.outcome_label:<15} @ "
                    f"{quote.ask_price:.4f} (size {quote.ask_size:.4f})"
                )
            else:
                log_print(
                    f"  SELL {quote.outcome_label:<14} @ "
                    f"{quote.bid_price:.4f} (size {quote.bid_size:.4f})"
                )
        log_print(f"Volume        : {market.volume if market.volume is not None else '-'}")


if __name__ == "__main__":
    market_opportunities = find_probabilistic_arbitrage(limit=1000)
    describe_opportunities(market_opportunities)
