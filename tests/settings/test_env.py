from __future__ import annotations

import os

from polymarket_agents.settings.env import load_env


def test_load_env_from_explicit_path(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text('EXPLICIT_KEY="explicit"\n', encoding="utf-8")
    monkeypatch.delenv("EXPLICIT_KEY", raising=False)

    load_env(env_path)

    assert os.environ["EXPLICIT_KEY"] == "explicit"


def test_load_env_defaults_to_cwd(tmp_path, monkeypatch) -> None:
    env_path = tmp_path / ".env"
    env_path.write_text("DEFAULT_KEY=42\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DEFAULT_KEY", raising=False)

    load_env()

    assert os.environ["DEFAULT_KEY"] == "42"
