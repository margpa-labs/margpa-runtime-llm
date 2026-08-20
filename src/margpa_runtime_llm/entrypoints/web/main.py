"""Run the single-worker Phase 1-G preview web surface."""

from __future__ import annotations

import argparse
import ipaddress
import platform
import sys
from collections.abc import Sequence
from functools import partial
from pathlib import Path

import uvicorn

from margpa_runtime_llm.bootstrap.documentation_rag import (
    build_documentation_rag,
    build_local_documentation_rag,
)
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationScopeId
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagPlatform,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.web.access_profiles import (
    DocumentationRagCapability,
    DocumentationRagFeatureMode,
    DocumentationRagFeatureProfile,
    WebExposureMode,
    build_disabled_control_policy,
    load_web_access_profile,
    local_web_access_profile,
    resolve_documentation_rag_state,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import load_web_access_policy, validate_bind_access_policy

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
DEFAULT_DOCUMENTATION_RAG_DEFAULTS = (
    PROJECT_ROOT / "config/feature_profiles/documentation_rag_defaults.toml"
)
DEFAULT_LOCAL_DOCUMENTATION_RAG_PROFILE = (
    PROJECT_ROOT / "config/feature_profiles/local_documentation_rag.toml"
)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
PLACEHOLDER_HELP = (
    "Usage内の大文字(HOST、PORT、PROFILE_PATH等)は、実際の値へ置き換える仮引数名です。\n"
    "Non-loopback Bindには明示的なbasic_previewまたはpublic_demo Access Profileが必須です。"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="margpa-web",
        description=__doc__,
        epilog=PLACEHOLDER_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        metavar="HOST",
        help=f"Bind host (default: {DEFAULT_HOST})",
    )
    parser.add_argument(
        "--port",
        type=_port,
        default=DEFAULT_PORT,
        metavar="PORT",
        help=f"Bind port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        metavar="PROFILE_PATH",
        help="Deployment Profile path (environment/platform resolution when omitted)",
    )
    parser.add_argument(
        "--access-profile",
        type=Path,
        metavar="WEB_ACCESS_PROFILE_PATH",
        help="Web Access Profile path (default: built-in loopback-only local profile)",
    )
    parser.add_argument(
        "--documentation-rag-profile",
        type=Path,
        metavar="DOCUMENTATION_RAG_PROFILE_PATH",
        help="Server-owned Documentation RAG Feature Profile path",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        metavar="MODEL_DEFINITION_PATH",
        help="Model Definition path (default: tracked Qwen3-4B definition)",
    )
    parser.add_argument(
        "--model-root",
        type=Path,
        metavar="MODEL_ROOT",
        help="Model storage root (default source: environment/application config)",
    )
    parser.add_argument(
        "--model-key",
        metavar="MODEL_KEY",
        help="Registered model key (default source: environment/application config)",
    )
    parser.add_argument(
        "--context-size",
        type=int,
        metavar="TOKENS",
        help="Loaded context size (default source: profile/application config)",
    )
    parser.add_argument(
        "--conversation-persistence",
        action="store_true",
        help="Enable explicit loopback-only local conversation persistence",
    )
    parser.add_argument(
        "--conversation-runtime-data-root",
        type=Path,
        metavar="RUNTIME_DATA_ROOT",
        help="Absolute server-owned runtime-data root for conversation persistence",
    )
    parser.add_argument(
        "--conversation-scope-id",
        metavar="SCOPE_ID",
        help="Server-owned local conversation scope identity",
    )
    parser.add_argument(
        "--conversation-persistence-migrate",
        action="store_true",
        help=(
            "Explicit opt-in: on startup, upgrade an existing older-schema "
            "conversation store in place (checkpoint/digest/rollback via the "
            "existing migration contract). Without this flag, an older-schema "
            "store fails closed instead of starting."
        ),
    )
    parser.add_argument(
        "--configuration-control",
        action="store_true",
        help="Enable loopback-only process-local configuration control",
    )
    parser.add_argument(
        "--runtime-composition-inspection",
        action="store_true",
        help="Enable loopback-only read-only runtime component inspection",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        web_access_profile = (
            load_web_access_profile(args.access_profile)
            if args.access_profile is not None
            else local_web_access_profile()
        )
        access_policy = load_web_access_policy(profile=web_access_profile)
        validate_bind_access_policy(args.host, access_policy)
        configuration_control_enabled = _configuration_control_enabled(
            enabled=args.configuration_control,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        runtime_composition_inspection_enabled = _runtime_composition_inspection_enabled(
            enabled=args.runtime_composition_inspection,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        conversation_persistence_settings = _conversation_persistence_settings(
            enabled=args.conversation_persistence,
            runtime_data_root=args.conversation_runtime_data_root,
            scope_id=args.conversation_scope_id,
            allow_migration=args.conversation_persistence_migrate,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        control_policy = build_disabled_control_policy(web_access_profile)
        documentation_rag = None
        documentation_rag_default_mode = DocumentationRagMode.DISABLED
        documentation_rag_provider_display_name = None
        documentation_rag_token_counter_binder = None
        documentation_rag_feature_profile = DocumentationRagFeatureProfile()
        documentation_composition = None
        if web_access_profile.features.documentation_rag is DocumentationRagCapability.ELIGIBLE:
            if args.documentation_rag_profile is not None:
                observed_platform = _documentation_rag_platform()
                documentation_composition = build_documentation_rag(
                    project_root=PROJECT_ROOT,
                    defaults_path=DEFAULT_DOCUMENTATION_RAG_DEFAULTS,
                    feature_path=args.documentation_rag_profile,
                    access_mode=web_access_profile.access.mode.value,
                    platform_observation=(
                        observed_platform.value if observed_platform is not None else "unsupported"
                    ),
                )
            elif (
                web_access_profile.access.mode is WebExposureMode.LOCAL
                and _local_mac_documentation_rag_eligible()
            ):
                documentation_composition = build_local_documentation_rag(
                    project_root=PROJECT_ROOT,
                    defaults_path=DEFAULT_DOCUMENTATION_RAG_DEFAULTS,
                    feature_path=DEFAULT_LOCAL_DOCUMENTATION_RAG_PROFILE,
                )
        if documentation_composition is not None:
            documentation_rag = documentation_composition.orchestrator
            documentation_rag_default_mode = documentation_composition.defaults.default_mode
            documentation_rag_provider_display_name = (
                documentation_composition.feature.provider_display_name
            )
            documentation_rag_token_counter_binder = documentation_composition.bind_token_counter
            documentation_rag_feature_profile = DocumentationRagFeatureProfile(
                mode=DocumentationRagFeatureMode.ENABLED
            )
        documentation_rag_availability = (
            DocumentationRagAvailability.DENIED
            if web_access_profile.features.documentation_rag is DocumentationRagCapability.DENIED
            else (
                DocumentationRagAvailability.AVAILABLE
                if documentation_rag is not None
                else DocumentationRagAvailability.UNAVAILABLE
            )
        )
        documentation_rag_state = resolve_documentation_rag_state(
            access_profile=web_access_profile,
            feature_profile=documentation_rag_feature_profile,
            adapter_available=documentation_rag is not None,
        )
        load_overrides = (
            {"context_size": args.context_size} if args.context_size is not None else None
        )
        runtime_factory = partial(
            build_phase1_web_runtime,
            project_root=PROJECT_ROOT,
            profile_path=args.profile,
            registry_path=args.registry,
            cli_model_root=args.model_root,
            cli_model_key=args.model_key,
            load_overrides=load_overrides,
            documentation_rag=documentation_rag,
            documentation_rag_availability=documentation_rag_availability,
            documentation_rag_effective_state=documentation_rag_state,
            documentation_rag_default_mode=documentation_rag_default_mode,
            documentation_rag_provider_display_name=documentation_rag_provider_display_name,
            documentation_rag_token_counter_binder=documentation_rag_token_counter_binder,
            conversation_persistence_settings=conversation_persistence_settings,
            configuration_control_enabled=configuration_control_enabled,
            runtime_composition_inspection_enabled=runtime_composition_inspection_enabled,
        )
        app = create_web_app(
            runtime_factory=runtime_factory,
            access_policy=access_policy,
            control_policy=control_policy,
        )
        app.state.web_access_profile = web_access_profile
        app.state.public_control_policy = control_policy
        app.state.documentation_rag_feature_profile = documentation_rag_feature_profile
        app.state.documentation_rag_state = documentation_rag_state
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=1,
            reload=False,
            access_log=False,
        )
        return 0
    except InferenceError as exc:
        print(f"error [{exc.code.value}]: {exc.safe_message}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("PORT must be an integer") from exc
    if not 1 <= port <= 65_535:
        raise argparse.ArgumentTypeError("PORT must be between 1 and 65535")
    return port


def _local_mac_documentation_rag_eligible(
    *,
    system_name: str | None = None,
    machine: str | None = None,
) -> bool:
    resolved_system = platform.system() if system_name is None else system_name
    resolved_machine = platform.machine() if machine is None else machine
    return resolved_system == "Darwin" and resolved_machine.casefold() == "arm64"


def _documentation_rag_platform(
    *,
    system_name: str | None = None,
    machine: str | None = None,
) -> DocumentationRagPlatform | None:
    resolved_system = platform.system() if system_name is None else system_name
    resolved_machine = platform.machine() if machine is None else machine
    normalized_machine = resolved_machine.casefold()
    if resolved_system == "Darwin" and normalized_machine == "arm64":
        return DocumentationRagPlatform.MACOS_ARM64
    if resolved_system == "Linux" and normalized_machine in {"x86_64", "amd64"}:
        return DocumentationRagPlatform.LINUX_X86_64_CONTAINER
    return None


def _conversation_persistence_settings(
    *,
    enabled: bool,
    runtime_data_root: Path | None,
    scope_id: str | None,
    allow_migration: bool,
    host: str,
    access_mode: WebExposureMode,
    authentication_required: bool,
) -> LocalConversationPersistenceSettings | None:
    supplied = runtime_data_root is not None or scope_id is not None
    if not enabled:
        if supplied:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_CONFIGURATION,
                safe_message="Conversation persistence inputs require explicit opt-in.",
            )
        if allow_migration:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_CONFIGURATION,
                safe_message="Conversation persistence migration requires explicit opt-in.",
            )
        return None
    if (
        runtime_data_root is None
        or scope_id is None
        or access_mode is not WebExposureMode.LOCAL
        or authentication_required
        or not _is_loopback_host(host)
    ):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message=(
                "Conversation persistence requires local loopback access and explicit inputs."
            ),
        )
    try:
        return LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=runtime_data_root,
            scope_id=ConversationScopeId(value=scope_id),
            allow_migration=allow_migration,
        )
    except ValueError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="Conversation persistence inputs are invalid.",
        ) from exc


def _configuration_control_enabled(
    *,
    enabled: bool,
    host: str,
    access_mode: WebExposureMode,
    authentication_required: bool,
) -> bool:
    if not enabled:
        return False
    if (
        access_mode is not WebExposureMode.LOCAL
        or authentication_required
        or not _is_loopback_host(host)
    ):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message=(
                "Configuration control requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _runtime_composition_inspection_enabled(
    *,
    enabled: bool,
    host: str,
    access_mode: WebExposureMode,
    authentication_required: bool,
) -> bool:
    if not enabled:
        return False
    if (
        access_mode is not WebExposureMode.LOCAL
        or authentication_required
        or not _is_loopback_host(host)
    ):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message=(
                "Runtime composition inspection requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower().strip("[]")
    if normalized == "localhost":
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
