"""Command-line interface for interacting with Polymarket trading agents."""

import typer

from polymarket_agents.application.finder import (
    describe_opportunities,
    find_probabilistic_arbitrage,
)
from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.utils.logging import (
    log_error,
    log_print,
    print_trades,
)

app = typer.Typer()


def get_polymarket() -> Polymarket:
    """Provide a Polymarket API client configured with default settings."""
    return Polymarket()


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
        address = polymarket.get_address_for_private_key()
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
def find_arbitrage(
    target: int = typer.Option(2, help="Number of opportunities to surface."),
    batch: int = typer.Option(500, help="Markets fetched per Gamma request."),
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
