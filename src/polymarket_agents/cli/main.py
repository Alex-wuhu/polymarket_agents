"""Command-line interface for interacting with Polymarket trading agents."""

import typer
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.connectors.chroma import PolymarketRAG
from polymarket_agents.connectors.news import News
from polymarket_agents.application.trade import Trader
from polymarket_agents.application.executor import Executor
from polymarket_agents.utils.logging import log_print

app = typer.Typer()


def get_polymarket() -> Polymarket:
    """Provide a Polymarket API client configured with default settings."""
    return Polymarket()


def get_news_client() -> News:
    """Return the NewsAPI client used for gathering context."""
    return News()


def get_polymarket_rag() -> PolymarketRAG:
    """Instantiate the Chroma-backed RAG helper for local market data."""
    return PolymarketRAG()



@app.command()
def ask_superforecaster(event_title: str, market_question: str, outcome: str) -> None:
    """Request a superforecaster-style assessment for a given event and outcome."""
    log_print(
        f"event: str = {event_title}, question: str = {market_question}, outcome (usually yes or no): str = {outcome}"
    )
    executor = Executor()
    response = executor.get_superforecast(
        event_title=event_title, market_question=market_question, outcome=outcome
    )
    log_print(f"Response:{response}")





@app.command()
def run_autonomous_trader() -> None:
    """Launch the end-to-end trading agent using default policies and connectors."""
    trader = Trader()
    trader.one_best_trade()


if __name__ == "__main__":
    app()
