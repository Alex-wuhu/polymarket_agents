import typer
from devtools import pprint

from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.connectors.chroma import PolymarketRAG
from polymarket_agents.connectors.news import News
from polymarket_agents.application.trade import Trader
from polymarket_agents.application.executor import Executor
from polymarket_agents.application.creator import Creator
from polymarket_agents.utils.logging import is_enabled, print_log

app = typer.Typer()


def get_polymarket() -> Polymarket:
    return Polymarket()


def get_news_client() -> News:
    return News()


def get_polymarket_rag() -> PolymarketRAG:
    return PolymarketRAG()


@app.command()
def get_all_markets(limit: int = 5, sort_by: str = "spread") -> None:
    """
    Query Polymarket's markets
    """
    print_log(f"limit: int = {limit}, sort_by: str = {sort_by}")
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
    """
    Use NewsAPI to query the internet
    """
    articles = get_news_client().get_articles_for_cli_keywords(keywords)
    if is_enabled():
        pprint(articles)


@app.command()
def get_all_events(limit: int = 5, sort_by: str = "number_of_markets") -> None:
    """
    Query Polymarket's events
    """
    print_log(f"limit: int = {limit}, sort_by: str = {sort_by}")
    client = get_polymarket()
    events = client.get_all_events()
    events = client.filter_events_for_trading(events)
    if sort_by == "number_of_markets":
        events = sorted(events, key=lambda x: len(x.markets), reverse=True)
    events = events[:limit]
    if is_enabled():
        pprint(events)


@app.command()
def create_local_markets_rag(local_directory: str) -> None:
    """
    Create a local markets database for RAG
    """
    get_polymarket_rag().create_local_markets_rag(local_directory=local_directory)


@app.command()
def query_local_markets_rag(vector_db_directory: str, query: str) -> None:
    """
    RAG over a local database of Polymarket's events
    """
    response = get_polymarket_rag().query_local_markets_rag(
        local_directory=vector_db_directory, query=query
    )
    if is_enabled():
        pprint(response)


@app.command()
def ask_superforecaster(event_title: str, market_question: str, outcome: str) -> None:
    """
    Ask a superforecaster about a trade
    """
    print_log(
        f"event: str = {event_title}, question: str = {market_question}, outcome (usually yes or no): str = {outcome}"
    )
    executor = Executor()
    response = executor.get_superforecast(
        event_title=event_title, market_question=market_question, outcome=outcome
    )
    print_log(f"Response:{response}")


@app.command()
def create_market() -> None:
    """
    Format a request to create a market on Polymarket
    """
    c = Creator()
    market_description = c.one_best_market()
    print_log(f"market_description: str = {market_description}")


@app.command()
def ask_polymarket_llm(user_input: str) -> None:
    """
    What types of markets do you want trade?
    """
    executor = Executor()
    response = executor.get_polymarket_llm(user_input=user_input)
    print_log(f"LLM + current markets&events response: {response}")


@app.command()
def run_autonomous_trader() -> None:
    """
    Let an autonomous system trade for you.
    """
    trader = Trader()
    trader.one_best_trade()


if __name__ == "__main__":
    app()
