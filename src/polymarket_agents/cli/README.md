# CLI Overview

The Typer application in this package exposes the command line entry points distributed with `polymarket-agents`. Each command creates lightweight wrappers around higher-level orchestrators so contributors can inspect agent behavior quickly.

- `main.py` registers commands such as `get-all-markets`, `get-all-events`, `ask-superforecaster`, and `run-autonomous-trader`. Each command uses factory helpers (`get_polymarket`, `get_news_client`, etc.) to build the dependencies the agent needs.
- Commands log through `polymarket_agents.utils.logging` to ensure consistent verbosity. Toggling the `POLYMARKET_LOGGING` environment variable controls whether results are printed or silent.
- When adding new commands, define them in `main.py`, make sure they delegate to orchestrators under `application/`, and add a short docstring so the command surfaces clear help text.

Run `uv run polymarket-agents --help` to see a full list of available commands during development.
