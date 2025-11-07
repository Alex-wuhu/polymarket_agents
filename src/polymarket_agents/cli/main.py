"""Command-line interface for interacting with Polymarket trading agents."""

import typer
from polymarket_agents.application.finder import (
    describe_opportunities,
    find_probabilistic_arbitrage,
)
from polymarket_agents.polymarket.data_api import DataAPI
from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.utils.logging import (
    log_error,
    log_print,
    print_positions,
    print_trades,
    print_markets
)

app = typer.Typer()

def get_polymarket() -> Polymarket:
    """Provide a Polymarket API client configured with default settings."""
    return Polymarket()

@app.command()
def show_markets() -> None:
    """Find 3 Tradble markets."""
    gamma = GammaMarketClient()
    try:
        sample_markets = gamma.get_tradable_markets(limit=3)
        print_markets(sample_markets)
    except Exception as exc:
        log_error(f"[__main__] Failed to fetch tradable markets: {exc}")

@app.command()
def show_wallet_status() -> None:
    """Display the configured wallet address and current USDC balance."""
    polymarket = get_polymarket()
    typer.echo("Fetching wallet status...", nl=False)
    
    if not polymarket.private_key:
        log_print(
            "POLYGON_WALLET_PRIVATE_KEY is not set; unable to derive wallet address."
        )
        raise typer.Exit(code=1)

    try:
        #address = polymarket.get_address_for_private_key()
        address = "0xCb866071bd7c533b379c3e45e7Ef0D1e3bF9aa1D"
    except Exception as exc:  # pragma: no cover - defensive guard
        typer.echo("")  # ensure we break the inline status line
        log_print(f"Failed to derive wallet address: {exc}")
        raise typer.Exit(code=1)

    try:
        usdc_balance = polymarket.get_usdc_balance()
    except Exception as exc:  # pragma: no cover - defensive guard
        typer.echo("")
        log_print(f"Failed to fetch USDC balance: {exc}")
        raise typer.Exit(code=1)

    typer.echo(" done")

    log_print(f"Wallet address: {address}")
    log_print(f"USDC balance : {usdc_balance:.6f}")


@app.command()
def show_trading_history(
    limit: int = typer.Option(
        10,
        min=1,
        help="Number of most-recent trades to display.",
    )
) -> None:
    """Display recent trades associated with the configured account."""
    polymarket = get_polymarket()
    typer.echo("Fetching recent trades...", nl=False)

    try:
        trades = polymarket.client.get_trades()
    except Exception as exc:  # pragma: no cover - defensive guard
        typer.echo("")
        log_error(f"Failed to fetch trading history: {exc}")
        raise typer.Exit(code=1)

    typer.echo(" done")

    if not trades:
        log_print("No trades found for this account.")
        return

    print_trades(trades[:limit])


@app.command()
def show_positions(
    limit: int = typer.Option(
        20,
        min=1,
        help="Maximum number of positions to request.",
    ),
    size_threshold: float = typer.Option(
        1.0,
        min=0.0,
        help="Ignore positions below this token size.",
    ),
    sort_by: str = typer.Option(
        "TOKENS",
        help="Sort key accepted by the data API (e.g. TOKENS, VALUE, PNL).",
    ),
    sort_direction: str = typer.Option(
        "DESC",
        help="Sort direction (ASC or DESC).",
    ),
) -> None:
    """Display readable position data for the configured wallet."""
    polymarket = get_polymarket()
    if not polymarket.private_key:
        log_print(
            "POLYGON_WALLET_PRIVATE_KEY is not set; unable to derive wallet address."
        )
        raise typer.Exit(code=1)

    try:
        #address = polymarket.get_address_for_private_key()
        address = "0xCb866071bd7c533b379c3e45e7Ef0D1e3bF9aa1D"
    except Exception as exc:  # pragma: no cover - defensive guard
        log_error(f"Failed to derive wallet address: {exc}")
        raise typer.Exit(code=1)

    data_api = DataAPI()
    typer.echo("Fetching positions...", nl=False)
    try:
        positions = data_api.get_positions(
            user=address,
            limit=limit,
            sizeThreshold=size_threshold,
            sortBy=sort_by,
            sortDirection=sort_direction,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        typer.echo("")
        log_error(f"Failed to fetch positions: {exc}")
        raise typer.Exit(code=1)

    typer.echo(" done")

    if not positions:
        log_print("No positions found for this account.")
        return

    print_positions(positions)


@app.command()
def find_arbitrage(
    target: int = typer.Option(2, help="Number of opportunities to surface."),
    batch: int = typer.Option(200, help="Markets fetched per Gamma request."),
    offset: int = typer.Option(0, help="Starting offset for Gamma pagination."),
) -> None:
    """Surface markets where summed outcome prices deviate from parity."""
    try:
        opportunities = find_probabilistic_arbitrage(
            target_results=target,
            batch_limit=batch,
            start_offset=offset,
        )
        describe_opportunities(opportunities)
    except Exception as exc:  # pragma: no cover - defensive guard
        log_error(f"Failed to discover arbitrage opportunities: {exc}")


if __name__ == "__main__":
    app()
