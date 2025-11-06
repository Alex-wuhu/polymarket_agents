import json
import os
import time

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores.chroma import Chroma

from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.utils.objects import Market, PolymarketEvent


class PolymarketRAG:
    def __init__(self, local_db_directory=None, embedding_function=None) -> None:
        self.gamma_client = GammaMarketClient()
        self.local_db_directory = local_db_directory
        self.embedding_function = embedding_function

    @staticmethod
    def _serialise_event(event: PolymarketEvent) -> dict:
        market_ids: list[str] = []
        if event.markets:
            for market in event.markets:
                if isinstance(market, Market):
                    market_ids.append(str(market.id))
                elif isinstance(market, dict):
                    market_id = market.get("id")
                    if market_id is not None:
                        market_ids.append(str(market_id))
                else:
                    market_ids.append(str(market))

        return {
            "id": str(event.id),
            "title": event.title or "",
            "slug": event.slug or "",
            "description": event.description or "",
            "category": getattr(event, "category", None),
            "market_ids": market_ids,
        }

    @staticmethod
    def _serialise_market(market: Market) -> dict:
        outcomes_raw = getattr(market, "outcomes", None)
        if isinstance(outcomes_raw, str):
            try:
                outcomes = json.loads(outcomes_raw)
            except json.JSONDecodeError:
                outcomes = [outcomes_raw]
        elif outcomes_raw is None:
            outcomes = []
        else:
            outcomes = [str(outcome) for outcome in outcomes_raw]

        outcome_prices_processed: list[float] = []
        for price in getattr(market, "outcomePrices", []) or []:
            try:
                outcome_prices_processed.append(float(price))
            except (TypeError, ValueError):
                continue

        clob_token_ids_raw = getattr(market, "clobTokenIds", []) or []
        if isinstance(clob_token_ids_raw, str):
            try:
                clob_token_ids = json.loads(clob_token_ids_raw)
            except json.JSONDecodeError:
                clob_token_ids = [clob_token_ids_raw]
        else:
            clob_token_ids = list(clob_token_ids_raw)
        clob_token_ids = [str(token) for token in clob_token_ids]

        return {
            "id": str(market.id),
            "question": market.question or "",
            "description": market.description or "",
            "category": market.category,
            "slug": market.slug or "",
            "outcomes": outcomes,
            "outcome_prices": outcome_prices_processed,
            "outcomePrices": outcome_prices_processed,
            "clob_token_ids": clob_token_ids,
            "clobTokenIds": clob_token_ids,
        }

    def load_json_from_local(
        self, json_file_path=None, vector_db_directory="./local_db"
    ) -> None:
        loader = JSONLoader(
            file_path=json_file_path, jq_schema=".[].description", text_content=False
        )
        loaded_docs = loader.load()

        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

    def create_local_markets_rag(self, local_directory="./local_db") -> None:
        all_markets = self.gamma_client.get_tradable_markets(limit=250)

        if not os.path.isdir(local_directory):
            os.mkdir(local_directory)

        local_file_path = f"{local_directory}/all-current-markets_{time.time()}.json"

        serialised_markets = [
            self._serialise_market(market) if isinstance(market, Market) else market
            for market in all_markets
        ]

        with open(local_file_path, "w+") as output_file:
            json.dump(serialised_markets, output_file)

        self.load_json_from_local(
            json_file_path=local_file_path, vector_db_directory=local_directory
        )

    def query_local_markets_rag(
        self, local_directory=None, query=None
    ) -> "list[tuple]":
        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        local_db = Chroma(
            persist_directory=local_directory, embedding_function=embedding_function
        )
        response_docs = local_db.similarity_search_with_score(query=query)
        return response_docs

    def events(self, events: "list[PolymarketEvent]", prompt: str) -> "list[tuple]":
        # create local json file
        local_events_directory: str = "./local_db_events"
        if not os.path.isdir(local_events_directory):
            os.mkdir(local_events_directory)
        local_file_path = f"{local_events_directory}/events.json"
        dict_events = [
            self._serialise_event(event) if isinstance(event, PolymarketEvent) else event
            for event in events
        ]
        with open(local_file_path, "w+") as output_file:
            json.dump(dict_events, output_file)

        # create vector db
        def metadata_func(record: dict, metadata: dict) -> dict:

            metadata["id"] = record.get("id")
            metadata["market_ids"] = record.get("market_ids", [])
            metadata["markets"] = metadata["market_ids"]

            return metadata

        loader = JSONLoader(
            file_path=local_file_path,
            jq_schema=".[]",
            content_key="description",
            text_content=False,
            metadata_func=metadata_func,
        )
        loaded_docs = loader.load()
        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vector_db_directory = f"{local_events_directory}/chroma"
        local_db = Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

        # query
        return local_db.similarity_search_with_score(query=prompt)

    def markets(self, markets: "list[Market]", prompt: str) -> "list[tuple]":
        # create local json file
        local_events_directory: str = "./local_db_markets"
        if not os.path.isdir(local_events_directory):
            os.mkdir(local_events_directory)
        local_file_path = f"{local_events_directory}/markets.json"
        serialisable_markets = [
            self._serialise_market(market) if isinstance(market, Market) else market
            for market in markets
        ]
        with open(local_file_path, "w+") as output_file:
            json.dump(serialisable_markets, output_file)

        # create vector db
        def metadata_func(record: dict, metadata: dict) -> dict:

            metadata["id"] = record.get("id")
            metadata["outcomes"] = record.get("outcomes")
            metadata["outcome_prices"] = record.get("outcome_prices")
            metadata["outcomePrices"] = metadata["outcome_prices"]
            metadata["question"] = record.get("question")
            metadata["clob_token_ids"] = record.get("clob_token_ids")
            metadata["clobTokenIds"] = metadata["clob_token_ids"]

            return metadata

        loader = JSONLoader(
            file_path=local_file_path,
            jq_schema=".[]",
            content_key="description",
            text_content=False,
            metadata_func=metadata_func,
        )
        loaded_docs = loader.load()
        embedding_function = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        vector_db_directory = f"{local_events_directory}/chroma"
        local_db = Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

        # query
        return local_db.similarity_search_with_score(query=prompt)
