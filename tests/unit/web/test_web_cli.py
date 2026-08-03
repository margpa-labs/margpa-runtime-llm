"""Web command parsing and pre-load access validation tests."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from fastapi import FastAPI

from margpa_runtime_llm.bootstrap import web_application as web_application_module
from margpa_runtime_llm.bootstrap.documentation_rag import (
    LocalDocumentationRagComposition,
    build_local_documentation_rag,
)
from margpa_runtime_llm.bootstrap.phase1_application import Phase1Application
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.entrypoints.web import main as web_cli
from margpa_runtime_llm.modules.documentation_rag.ports import RagOrchestratorPort
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig
from margpa_runtime_llm.web.access_profiles import (
    DocumentationRagEffectiveState,
    DocumentationRagFeatureMode,
    OptionalControlMode,
    WebExposureMode,
)
from margpa_runtime_llm.web.auth import AUTH_MODE_ENV, AUTH_PASSWORD_ENV, AUTH_USERNAME_ENV

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASIC_PROFILE = PROJECT_ROOT / "config/web_profiles/basic_preview.toml"
PUBLIC_PROFILE = PROJECT_ROOT / "config/web_profiles/public_demo.toml"
LIGHTNING_RAG_PROFILE = (
    PROJECT_ROOT / "config/feature_profiles/lightning_public_documentation_rag.toml"
)


def test_web_help_documents_safe_defaults_and_placeholders() -> None:
    help_text = web_cli.build_parser().format_help()

    assert "margpa-web" in help_text
    assert "127.0.0.1" in help_text
    assert "8000" in help_text
    assert "HOST" in help_text
    assert "PROFILE_PATH" in help_text
    assert "basic_preview" in help_text
    assert "public_demo" in help_text
    assert "DOCUMENTATION_RAG_PROFILE_PATH" in help_text


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


def test_local_mac_documentation_rag_eligibility_is_platform_specific() -> None:
    assert web_cli._local_mac_documentation_rag_eligible(system_name="Darwin", machine="arm64")
    assert not web_cli._local_mac_documentation_rag_eligible(system_name="Linux", machine="x86_64")
    assert not web_cli._local_mac_documentation_rag_eligible(system_name="Windows", machine="AMD64")
    macos = web_cli._documentation_rag_platform(system_name="Darwin", machine="arm64")
    linux = web_cli._documentation_rag_platform(system_name="Linux", machine="x86_64")
    assert macos is not None
    assert macos.value == "macos-arm64"
    assert linux is not None
    assert linux.value == "linux-x86_64-container"
    assert web_cli._documentation_rag_platform(system_name="Windows", machine="AMD64") is None


def test_macos_arm64_local_profile_binds_documentation_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_apps: list[FastAPI] = []
    captured_compositions: list[LocalDocumentationRagComposition] = []
    captured_token_counter_binders: list[object] = []
    builder_calls = 0

    def fake_run(app: FastAPI, **kwargs: object) -> None:
        del kwargs
        captured_apps.append(app)

    def tracking_builder(
        *,
        project_root: Path,
        defaults_path: Path,
        feature_path: Path,
    ) -> LocalDocumentationRagComposition:
        nonlocal builder_calls
        builder_calls += 1
        composition = build_local_documentation_rag(
            project_root=project_root,
            defaults_path=defaults_path,
            feature_path=feature_path,
        )
        captured_compositions.append(composition)
        return composition

    def fake_create_web_app(**kwargs: object) -> FastAPI:
        runtime_factory = kwargs["runtime_factory"]
        assert isinstance(runtime_factory, partial)
        keywords = runtime_factory.keywords
        captured_token_counter_binders.append(keywords["documentation_rag_token_counter_binder"])
        return FastAPI()

    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.platform.system", lambda: "Darwin")
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.platform.machine", lambda: "arm64")
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.build_local_documentation_rag",
        tracking_builder,
    )
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.create_web_app",
        fake_create_web_app,
    )

    exit_code = web_cli.main([])

    assert exit_code == 0
    assert builder_calls == 1
    assert len(captured_apps) == 1
    assert len(captured_token_counter_binders) == 1
    assert captured_token_counter_binders[0] == captured_compositions[0].bind_token_counter
    assert captured_apps[0].state.documentation_rag_feature_profile.mode is (
        DocumentationRagFeatureMode.ENABLED
    )
    assert captured_apps[0].state.documentation_rag_state is DocumentationRagEffectiveState.ENABLED


def test_web_runtime_binds_loaded_service_counter_without_loading_another_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    count_calls: list[str] = []
    chat_count_calls: list[tuple[tuple[ChatMessage, ...], ThinkingMode]] = []
    close_calls = 0

    class FakeLoadedService:
        runtime_info = SimpleNamespace(
            model_key="main.model",
            loaded_context_size=4096,
            effective_capabilities=SimpleNamespace(features=frozenset()),
            device_kind="gpu",
            acceleration_api="metal",
        )

        def count_text_tokens(self, text: str) -> int:
            count_calls.append(text)
            return len(text.split())

        def count_chat_prompt_tokens(
            self,
            messages: tuple[ChatMessage, ...],
            thinking_mode: ThinkingMode,
        ) -> int:
            chat_count_calls.append((messages, thinking_mode))
            return 7

    service = FakeLoadedService()
    presentation = ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )
    config = SimpleNamespace(
        selected_model="main.model",
        profile_key="mac.local",
        generation=GenerationParameters(max_new_tokens=2048),
        response=SimpleNamespace(language=ResponseLanguage.JA),
        presentation=presentation,
        summarization=SummarizationConfig(),
    )

    def close() -> None:
        nonlocal close_calls
        close_calls += 1

    application = cast(
        Phase1Application,
        SimpleNamespace(
            service=service,
            config=config,
            presentation_service=object(),
            close=close,
        ),
    )
    build_calls = 0

    def fake_build(**_kwargs: object) -> Phase1Application:
        nonlocal build_calls
        build_calls += 1
        return application

    bound_counters: list[object] = []
    monkeypatch.setattr(
        web_application_module,
        "build_phase1_application",
        fake_build,
    )

    runtime = build_phase1_web_runtime(
        project_root=PROJECT_ROOT,
        profile_path=None,
        registry_path=PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml",
        documentation_rag=cast(RagOrchestratorPort, object()),
        documentation_rag_token_counter_binder=bound_counters.append,
    )

    assert build_calls == 1
    assert len(bound_counters) == 1
    counter = cast(Callable[[str], int], bound_counters[0])
    assert counter("one two") == 2
    assert count_calls == ["one two"]
    chat_counter = cast(
        Callable[[tuple[ChatMessage, ...], ThinkingMode], int],
        runtime.conversation._chat_prompt_token_counter,
    )
    messages = (ChatMessage(role=MessageRole.USER, content="日本語"),)
    assert chat_counter(messages, ThinkingMode.ENABLED) == 7
    assert chat_count_calls == [(messages, ThinkingMode.ENABLED)]
    runtime.close()
    assert close_calls == 1


def test_linux_local_profile_does_not_bind_mac_documentation_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_apps: list[FastAPI] = []

    def fake_run(app: FastAPI, **kwargs: object) -> None:
        del kwargs
        captured_apps.append(app)

    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.platform.machine", lambda: "x86_64"
    )
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.build_local_documentation_rag",
        lambda **_kwargs: pytest.fail("Linux must not bind the macOS documentation adapter"),
    )

    exit_code = web_cli.main([])

    assert exit_code == 0
    assert len(captured_apps) == 1
    assert captured_apps[0].state.documentation_rag_feature_profile.mode is (
        DocumentationRagFeatureMode.DISABLED
    )
    assert captured_apps[0].state.documentation_rag_state is (
        DocumentationRagEffectiveState.UNAVAILABLE
    )


def test_public_profile_without_server_feature_profile_reports_adapter_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_apps: list[FastAPI] = []

    def fake_run(app: FastAPI, **kwargs: object) -> None:
        del kwargs
        captured_apps.append(app)

    monkeypatch.delenv(AUTH_MODE_ENV, raising=False)
    monkeypatch.delenv(AUTH_USERNAME_ENV, raising=False)
    monkeypatch.delenv(AUTH_PASSWORD_ENV, raising=False)
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.build_local_documentation_rag",
        lambda **_kwargs: pytest.fail(
            "public composition must not construct the documentation RAG adapter"
        ),
    )

    exit_code = web_cli.main(
        [
            "--host",
            "0.0.0.0",
            "--access-profile",
            str(PUBLIC_PROFILE),
        ]
    )

    assert exit_code == 0
    assert len(captured_apps) == 1
    app = captured_apps[0]
    profile = app.state.web_access_profile
    control_policy = app.state.public_control_policy
    assert profile.access.mode is WebExposureMode.PUBLIC_DEMO
    assert control_policy.mode is OptionalControlMode.OFF
    assert app.state.documentation_rag_feature_profile.mode is DocumentationRagFeatureMode.DISABLED
    assert app.state.documentation_rag_state is DocumentationRagEffectiveState.UNAVAILABLE


@pytest.mark.parametrize("access_profile", [BASIC_PROFILE, PUBLIC_PROFILE])
def test_lightning_access_profiles_bind_the_shared_public_documentation_adapter(
    monkeypatch: pytest.MonkeyPatch,
    access_profile: Path,
) -> None:
    captured_apps: list[FastAPI] = []

    def fake_run(app: FastAPI, **kwargs: object) -> None:
        del kwargs
        captured_apps.append(app)

    if access_profile == BASIC_PROFILE:
        monkeypatch.setenv(AUTH_MODE_ENV, "basic")
        monkeypatch.setenv(AUTH_USERNAME_ENV, "preview-user")
        monkeypatch.setenv(AUTH_PASSWORD_ENV, "preview-password")
    else:
        monkeypatch.delenv(AUTH_MODE_ENV, raising=False)
        monkeypatch.delenv(AUTH_USERNAME_ENV, raising=False)
        monkeypatch.delenv(AUTH_PASSWORD_ENV, raising=False)
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.platform.machine", lambda: "x86_64"
    )
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)

    exit_code = web_cli.main(
        [
            "--host",
            "0.0.0.0",
            "--access-profile",
            str(access_profile),
            "--documentation-rag-profile",
            str(LIGHTNING_RAG_PROFILE),
        ]
    )

    assert exit_code == 0
    assert len(captured_apps) == 1
    assert captured_apps[0].state.documentation_rag_feature_profile.mode is (
        DocumentationRagFeatureMode.ENABLED
    )
    assert captured_apps[0].state.documentation_rag_state is (
        DocumentationRagEffectiveState.ENABLED
    )


def test_basic_profile_is_eligible_but_rag_adapter_remains_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_apps: list[FastAPI] = []

    def fake_run(app: FastAPI, **kwargs: object) -> None:
        del kwargs
        captured_apps.append(app)

    monkeypatch.setenv(AUTH_MODE_ENV, "basic")
    monkeypatch.setenv(AUTH_USERNAME_ENV, "preview-user")
    monkeypatch.setenv(AUTH_PASSWORD_ENV, "preview-password")
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)
    monkeypatch.setattr(
        "margpa_runtime_llm.entrypoints.web.main.build_local_documentation_rag",
        lambda **_kwargs: pytest.fail(
            "basic preview must not construct the local documentation RAG adapter"
        ),
    )

    exit_code = web_cli.main(
        [
            "--host",
            "0.0.0.0",
            "--access-profile",
            str(BASIC_PROFILE),
        ]
    )

    assert exit_code == 0
    assert len(captured_apps) == 1
    app = captured_apps[0]
    assert app.state.documentation_rag_feature_profile.mode is (
        DocumentationRagFeatureMode.DISABLED
    )
    assert app.state.documentation_rag_state is DocumentationRagEffectiveState.UNAVAILABLE


def test_basic_profile_still_fails_closed_without_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_run(*args: object, **kwargs: object) -> None:
        del args, kwargs
        nonlocal called
        called = True

    monkeypatch.setenv(AUTH_MODE_ENV, "basic")
    monkeypatch.delenv(AUTH_USERNAME_ENV, raising=False)
    monkeypatch.delenv(AUTH_PASSWORD_ENV, raising=False)
    monkeypatch.setattr("margpa_runtime_llm.entrypoints.web.main.uvicorn.run", fake_run)

    exit_code = web_cli.main(
        [
            "--host",
            "0.0.0.0",
            "--access-profile",
            str(BASIC_PROFILE),
        ]
    )

    assert exit_code == 2
    assert called is False


def test_model_and_deployment_overrides_are_orthogonal_to_access_profile() -> None:
    parsed = web_cli.build_parser().parse_args(
        [
            "--profile",
            "deployment.toml",
            "--access-profile",
            str(PUBLIC_PROFILE),
            "--registry",
            "model-definition.toml",
            "--documentation-rag-profile",
            "documentation-rag.toml",
            "--model-root",
            "models",
            "--model-key",
            "replacement.model",
            "--context-size",
            "8192",
        ]
    )

    assert parsed.profile == Path("deployment.toml")
    assert parsed.access_profile == PUBLIC_PROFILE
    assert parsed.registry == Path("model-definition.toml")
    assert parsed.documentation_rag_profile == Path("documentation-rag.toml")
    assert parsed.model_root == Path("models")
    assert parsed.model_key == "replacement.model"
    assert parsed.context_size == 8192
