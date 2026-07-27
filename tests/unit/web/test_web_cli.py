"""Web command parsing and pre-load access validation tests."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.entrypoints.web import main as web_cli
from margpa_runtime_llm.web.auth import AUTH_MODE_ENV, AUTH_PASSWORD_ENV, AUTH_USERNAME_ENV


def test_web_help_documents_safe_defaults_and_placeholders() -> None:
    help_text = web_cli.build_parser().format_help()

    assert "margpa-web" in help_text
    assert "127.0.0.1" in help_text
    assert "8000" in help_text
    assert "HOST" in help_text
    assert "PROFILE_PATH" in help_text
    assert "MARGPA_WEB_AUTH_MODE=basic" in help_text


def test_non_loopback_without_auth_fails_before_uvicorn(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    called = False

    def fake_run(*args: object, **kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.delenv(AUTH_MODE_ENV, raising=False)
    monkeypatch.delenv(AUTH_USERNAME_ENV, raising=False)
    monkeypatch.delenv(AUTH_PASSWORD_ENV, raising=False)
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)

    exit_code = web_cli.main(["--host", "0.0.0.0"])

    assert exit_code == 2
    assert called is False
    captured = capsys.readouterr()
    assert "non-loopback" in captured.err


def test_port_range_is_validated() -> None:
    with pytest.raises(SystemExit):
        web_cli.build_parser().parse_args(["--port", "0"])
    assert web_cli.build_parser().parse_args(["--port", "9000"]).port == 9000
