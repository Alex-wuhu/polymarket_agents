# Application Layer

Modules in this package coordinate trading workflows. They assemble connectors, decision policies, and executors into runnable agents.

- `creator.py` proposes candidate markets based on current events and available liquidity.
- `executor.py` mediates conversations with LLM-driven advisors such as the superforecaster workflow, translating responses into actionable signals.
- `trade.py` encapsulates an end-to-end trading loop via the `Trader` class, drawing on connectors for market data and the `polymarket` package to submit orders.

Agents should compose helpers through explicit constructors or provider functions (see `cli/main.py`) rather than pulling dependencies from global state. This keeps workflows testable and makes it straightforward to add simulations or dry runs. When adding a new agent, wire it through this layer first, then expose a CLI entry point or API route so other contributors can exercise it quickly.
