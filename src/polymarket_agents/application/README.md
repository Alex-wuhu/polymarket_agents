# Application Layer

Modules in this package coordinate trading workflows. They assemble connectors, decision policies, and utilities into runnable agents or one-off analyses.

- `finder.py` houses utilities for identifying trading opportunities, such as probability-sum arbitrage checks.
- `cron.py` contains experimental scheduling hooks for periodically running strategies.

Agents should compose helpers through explicit constructors or provider functions (see `cli/main.py`) rather than pulling dependencies from global state. This keeps workflows testable and makes it straightforward to add simulations or dry runs. When adding a new agent, wire it through this layer first, then expose a CLI entry point or API route so other contributors can exercise it quickly.
