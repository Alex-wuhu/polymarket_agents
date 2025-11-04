"""Command-line interface for interacting with Polymarket trading agents."""

import typer
from devtools import pprint

from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.connectors.chroma import PolymarketRAG
from polymarket_agents.connectors.news import News
from polymarket_agents.application.trade import Trader
from polymarket_agents.application.executor import Executor
from polymarket_agents.application.creator import Creator
from polymarket_agents.utils.logging import is_enabled, log_print

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
def get_all_markets(limit: int = 5, sort_by: str = "spread") -> None:
    """Show the most attractive active markets for trading."""
    log_print(f"limit: int = {limit}, sort_by: str = {sort_by}")
    client = get_polymarket()
    markets = client.get_all_markets()
    markets = client.filter_markets_for_trading(markets)
    if sort_by == "spread":
        markets = sorted(markets, key=lambda x: x.spread, reverse=True)
    markets = markets[:limit]
    if is_enabled():
        pprint(markets)


@app.command()
def get_relevant_news(keywords: str) -> None:
    """Fetch recent headlines from NewsAPI for the provided keywords."""
    articles = get_news_client().get_articles_for_cli_keywords(keywords)
    if is_enabled():
        pprint(articles)


@app.command()
def get_all_events(limit: int = 5, sort_by: str = "number_of_markets") -> None:
    """Return candidate Polymarket events filtered for trading readiness."""
    log_print(f"limit: int = {limit}, sort_by: str = {sort_by}")
    client = get_polymarket()
    events = client.get_all_events()
    filtered_events = client.filter_events_for_trading(events)
    if not filtered_events:
        log_print(
            "No active unrestricted events returned; showing raw results instead."
        )
        filtered_events = events
    events = filtered_events
    if sort_by == "number_of_markets":
        events = sorted(events, key=lambda x: len(x.markets), reverse=True)
    events = events[:limit]
    if is_enabled():
        pprint(events)


@app.command()
def create_local_markets_rag(local_directory: str) -> None:
    """Build a Chroma vector store from an exported Polymarket dataset."""
    get_polymarket_rag().create_local_markets_rag(local_directory=local_directory)


@app.command()
def query_local_markets_rag(vector_db_directory: str, query: str) -> None:
    """Query a local Chroma database for markets matching the provided prompt."""
    response = get_polymarket_rag().query_local_markets_rag(
        local_directory=vector_db_directory, query=query
    )
    if is_enabled():
        pprint(response)


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
def create_market() -> None:
    """Draft a Polymarket market creation payload based on current insights."""
    c = Creator()
    market_description = c.one_best_market()
    log_print(f"market_description: str = {market_description}")


@app.command()
def ask_polymarket_llm(user_input: str) -> None:
    """Send a free-form query to the Polymarket agent LLM for trade suggestions."""
    executor = Executor()
    response = executor.get_polymarket_llm(user_input=user_input)
    log_print(f"LLM + current markets&events response: {response}")


@app.command()
def run_autonomous_trader() -> None:
    """Launch the end-to-end trading agent using default policies and connectors."""
    trader = Trader()
    trader.one_best_trade()


if __name__ == "__main__":
    app()
