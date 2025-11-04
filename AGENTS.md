# Repository Guidelines

## Project Structure & Module Organization
Code lives under `src/polymarket_agents`, grouped by concern: `cli/` exposes Typer commands, `connectors/` handles external APIs, `application/` orchestrates agents, and `utils/` offers shared helpers. Domain models and trading logic sit in `polymarket/` and `api/`. Tests belong in `tests/`, and `docs/` contains user-facing references. Shell helpers (Docker builds, local setup) sit in `scripts/`. Generated market data during development should remain inside `local_db_events/` and kept out of version control.

## Build, Test, and Development Commands
- `uv sync` — install and lock dependencies into `.venv/`.
- `uv run polymarket-agents --help` — list available CLI entry points.
- `uv run polymarket-agents run-autonomous-trader` — launch the default autonomous agent.
- `uv run pytest` — execute the full test suite.
- `uv run ruff check .` and `uv run ruff format` — lint and format Python code.
- `pre-commit run --all-files` — mirror CI hooks before pushing.

## Coding Style & Naming Conventions
Target Python 3.10+, four-space indentation, and informative type hints for new modules. Ruff enforces a 100-character line limit and checks `E`, `F`, `I`, `UP`; let `ruff format` handle formatting where feasible. Follow Typer command naming (`snake_case`) and keep module names lowercase with underscores. Environment files follow `.env.example`; prefer descriptive variable names like `*_API_KEY`.

## Testing Guidelines
Pytest is configured in `pyproject.toml`; place tests beside the area they cover in `tests/` using `test_<feature>.py` files and `Test` classes or free functions. Aim to cover trading flows, connector error paths, and CLI argument parsing. Use `uv run pytest -k <keyword>` for focused runs and include fixtures for mocked network calls so suites stay deterministic.

## Commit & Pull Request Guidelines
Emulate existing Git history: concise, present-tense subjects (`add log system`, `refactor into UV`). Squash noisy commits before opening a PR. Each PR should include: a short summary of the agent or connector change, a note on test coverage (`uv run pytest`), any required `.env` updates, and screenshots or CLI transcripts when behavior changes. Link GitHub issues when applicable and flag breaking changes in the title.

## Configuration & Security Tips
Duplicate `.env.example` to configure secrets; never commit populated `.env` files or private keys. Use the provided Docker scripts for isolated testing, and rotate API credentials routinely when sharing environments.
