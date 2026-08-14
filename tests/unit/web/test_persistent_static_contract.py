"""Static source-of-truth and privacy contracts for the persistent browser mode."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_ROOT = PROJECT_ROOT / "src/margpa_runtime_llm/web/static"


def test_persistent_ui_is_capability_gated_and_has_required_actions() -> None:
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    assert 'id="persistent-panel"' in html and "hidden" in html
    assert 'id="send" class="primary" type="button" disabled' in html
    for value in (
        "/api/v2/conversations/runtime",
        "loadPersistentList",
        "loadPersistentDetail",
        "createPersistentConversation",
        "stopPersistentGeneration",
        "persistentDerived",
        "selectPersistentBranch",
        "resumePersistentConversation",
        "togglePersistentArchive",
    ):
        assert value in script
    assert "persistentEnabled: false" in script
    assert 'conversationMode: "capability_pending"' in script
    assert 'runtime.source_of_truth !== "server"' in script


def test_capability_negotiation_never_silently_falls_back_to_v1() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    assert 'state.conversationMode = "persistent"' in script
    assert 'state.conversationMode = "ephemeral"' in script
    assert 'state.conversationMode = "capability_failed"' in script
    assert 'state.conversationMode === "capability_pending"' in script
    assert 'state.conversationMode !== "ephemeral"' in script
    assert 'const ready = ["persistent", "ephemeral"].includes(state.conversationMode)' in script
    assert "syncConversationCapabilityControls();" in script
    capability = script[script.index("async function loadPersistentRuntime") :]
    assert 'throw new Error("persistent_capability_load_failed")' in capability
    assert "await loadPersistentList();" in capability
    assert 'state.conversationMode = "capability_failed"' in capability


def test_persistent_eof_without_durable_terminal_fails_and_rereads_detail() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    stream = script[
        script.index("async function readPersistentEventStream") : script.index(
            "async function stopPersistentGeneration"
        )
    ]
    assert "let durableTerminalObserved = false" in stream
    assert "if (!durableTerminalObserved)" in stream
    assert "await loadPersistentDetail();" in stream
    assert "return Number.isInteger(event.data.durable_revision)" in stream


def test_persistent_citations_survive_canonical_detail_rerender_in_page_memory() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    assert "activePersistentTurnId: null" in script
    assert "persistentCitationEvidence: new Map()" in script
    assert "state.activePersistentTurnId = event.data.turn_id ?? null" in script
    assert "state.persistentCitationEvidence.set(state.activePersistentTurnId" in script
    assert "state.persistentCitationEvidence.get(turn.turn_id)" in script
    assert "renderCitations(view, citationEvidence)" in script


def test_persistent_mutations_do_not_send_client_history_or_scope() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    persistent_source = script[script.index("async function sendPersistentMessage") :]
    assert "state.messages" not in persistent_source
    assert "scope_id" not in persistent_source
    assert "runtime_data_root" not in persistent_source
    assert "history:" not in persistent_source
    assert "expected_revision" in persistent_source
    assert "operation_id" in persistent_source
    assert "loadPersistentDetail" in persistent_source


def test_browser_storage_contains_only_interface_language_not_conversation_text() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    assert script.count("localStorage.setItem") == 1
    assert "localStorage.setItem(UI_LANGUAGE_KEY" in script
    assert "sessionStorage" not in script
    assert "indexedDB" not in script
    assert "IndexedDB" not in script
    assert 'localStorage.setItem("messages' not in script


def test_persistent_ui_has_japanese_english_and_mobile_layout_contracts() -> None:
    script = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    css = (STATIC_ROOT / "app.css").read_text(encoding="utf-8")
    assert "保存済みChat" in script
    assert 'persistentTitle: "Saved chats"' in script
    assert "persistentRetry" in script and "persistentRegenerate" in script
    assert ".persistent-panel" in css
    assert "@media (max-width: 640px)" in css
