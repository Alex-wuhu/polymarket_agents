from __future__ import annotations

from typer.testing import CliRunner

from polymarket_agents.cli.main import app


def test_help_lists_core_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in [
        "get-all-markets",
        "get-all-events",
        "get-relevant-news",
        "run-autonomous-trader",
    ]:
        assert command in result.output
