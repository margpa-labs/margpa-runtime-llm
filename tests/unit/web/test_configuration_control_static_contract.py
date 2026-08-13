"""Static local configuration-control privacy and capability contract."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = PROJECT_ROOT / "src/margpa_runtime_llm/web/static"


def test_static_bootstrap_defaults_disabled_and_is_boolean_only() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert html.count('id="configuration-bootstrap"') == 1
    assert '{"enabled":false}' in html
    assert "digest_sha512" not in html
    assert "configuration_control" not in html
    assert 'id="configuration-panel"' in html
    assert "hidden" in html.split('id="configuration-panel"', maxsplit=1)[1].split(">", 1)[0]


def test_browser_fetches_configuration_only_after_fixed_capability_gate() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    bootstrap_index = script.index("const configurationBootstrapEnabled")
    guard_index = script.index("if (!configurationBootstrapEnabled)", bootstrap_index)
    fetch_index = script.index('fetch("/api/v2/configuration/runtime"', guard_index)

    assert bootstrap_index < guard_index < fetch_index
    assert "configurationState" in script
    assert "configurationPreviewPatch" in script
    assert "developerDetailsVisible" in script
    assert 'fetch("/api/v2/configuration/preview"' in script
    assert 'fetch("/api/v2/configuration/apply"' in script


def test_configuration_state_is_not_written_to_browser_storage_or_dynamic_html() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    configuration_section = script[
        script.index("async function loadConfigurationControl") : script.index(
            "function parseEventBlock"
        )
    ]

    assert "localStorage.setItem" not in configuration_section
    assert "sessionStorage" not in configuration_section
    assert "innerHTML" not in configuration_section
    assert "insertAdjacentHTML" not in configuration_section
    assert "configurationTitle" in script
    assert "Runtime configuration control" in script


def test_control_panel_has_mobile_layout_and_existing_chat_controls_remain() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    css = (STATIC_ROOT / "app.css").read_text(encoding="utf-8")

    assert 'id="send"' in html
    assert 'id="persistent-panel"' in html
    assert ".configuration-controls" in css
    assert "@media (max-width: 640px)" in css
