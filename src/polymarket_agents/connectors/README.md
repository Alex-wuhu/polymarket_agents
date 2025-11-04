# Connectors Guide

Connectors wrap external services so trading agents can fetch market intelligence without scattering HTTP code across the codebase. Each connector returns typed objects or thin DTOs that downstream modules can consume directly.

- `polymarket.py` and `gamma.py` expose authenticated clients for the Polymarket APIs. They normalize market and event payloads, handle pagination, and supply helper methods such as `filter_markets_for_trading`.
- `chroma.py` implements local Retrieval-Augmented Generation support using ChromaDB. The `PolymarketRAG` class can build vector stores from market snapshots and run similarity queries for agent prompts.
- `news.py` uses NewsAPI to surface relevant headlines that agents can blend into their reasoning loop.

When introducing a new integration:
1. Add a connector module that encapsulates authentication and request/response handling.
2. Return typed objects (prefer Pydantic) or light dataclasses to keep orchestration code clean.
3. Cover error paths with tests in `tests/connectors/` and update `docs/` if the integration requires extra configuration (API keys, rate limits, etc.).
