# Current Trading Logic

This note summarizes how the autonomous trading pipeline currently works. It references the key modules under `src/polymarket_agents/`.

## Orchestrator (`application/trade.py`)
- `Trader.one_best_trade()` coordinates a full trade cycle.
- `pre_trade_logic()` clears the temporary Chroma vector stores (`local_db_events/`, `local_db_markets/`) to avoid mixing data across runs.
- The method is wrapped in a retry loop: if any step raises, the exception is logged and the strategy restarts.

## Data Acquisition (`polymarket/polymarket.py`, `polymarket/gamma.py`)
- `Polymarket.get_all_tradeable_events()` fetches `/events` from the Gamma API, normalizes them to `SimpleEvent`, and filters for active, unrestricted, open markets.
- `GammaMarketClient.get_market()` pulls full market metadata by `market_id`; `Polymarket.map_api_to_market()` converts the response into the lighter `SimpleMarket` shape used by the agent.
- `Polymarket.get_orderbook_price()` and `get_orderbook()` expose live CLOB data via the `py-clob-client` bindings, although they are not yet wired into the strategy.
- Wallet context (RPC URL, approvals, USDC balance) is prepared in `Polymarket.__init__()`, so on-chain actions only require a private key and CLOB API credentials.

## Event Filtering (`application/executor.py`, `connectors/chroma.py`)
- `Executor.filter_events_with_rag()` provides the initial screen. It:
  1. Builds a prompt template via `Prompter.filter_events()`.
  2. Writes event JSON to disk (`local_db_events/events.json`) and persists a Chroma vector store using OpenAI embeddings.
  3. Runs semantic search against the prompt text; the resulting `(Document, score)` tuples represent the most relevant events.
- The executor expects the event metadata to include a comma-separated list of market ids to map into actual markets.

## Market Filtering (`application/executor.py`, `connectors/chroma.py`)
- `Executor.map_filtered_events_to_markets()` expands each selected event into its markets by calling `GammaMarketClient.get_market()` and mapping with `Polymarket.map_api_to_market()`.
- `Executor.filter_markets()` repeats the Chroma process, this time embedding market descriptions and metadata (outcomes, prices, token ids) to surface promising opportunities.

## Trade Selection (`application/executor.py`, `application/prompts.py`)
- The top-ranked market (first element of the filtered list) is passed to `Executor.source_best_trade()`.
- Two LLM prompts run sequentially:
  1. `Prompter.superforecaster()` asks for a qualitative forecast that mirrors superforecaster tradecraft using the market question, description, and enumerated outcomes.
  2. `Prompter.one_best_trade()` translates that forecast into actionable trade instructions in a structured text block (`price`, `size`, `side`).
- The default language model is Google Gemini 2.5 Flash accessed through the OpenAI-compatible endpoint; the executor enforces basic token-limit logic when packaging market/event context.

## Sizing and Execution (`application/executor.py`, `polymarket/polymarket.py`)
- `Executor.format_trade_prompt_for_execution()` parses the LLM output, extracts the percentage-sized sizing hint, and multiplies it by the current USDC wallet balance (`Polymarket.get_usdc_balance()`).
- The intended execution call is `Polymarket.execute_market_order()`, which:
  - Picks the market’s scalar token id (typically the “Yes” side).
  - Builds a `MarketOrderArgs` object and signs it with the wallet’s API credentials.
  - Submits the order to the CLOB with `OrderType.FOK`.
- Actual execution is **disabled by default**. The lines in `Trader.one_best_trade()` that issue the market order are commented out; simply uncommenting them will send live trades, so they remain off to respect Polymarket’s ToS unless the user opts in.

## Current Limitations
- No post-trade management is implemented; `maintain_positions()` and `incentive_farm()` are stubs.
- Market selection only considers the first filtered market; there is no diversification or risk management layer yet.
- The RAG filters rely exclusively on market/event descriptions. Incorporating orderbook depth or price action would require extending the vectorization step or adding traditional heuristics.
- Error handling restarts the strategy recursively, so repeated API failures may cause long loops until the underlying service recovers.

This document should help new contributors understand where to extend or harden the trading flow before enabling real executions.
