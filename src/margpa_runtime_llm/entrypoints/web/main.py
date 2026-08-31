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

from margpa_runtime_llm.adapters.data_controls import JsonFileDataControlConsentStore
from margpa_runtime_llm.adapters.dev_agent import JsonFileDevAgentRunStore
from margpa_runtime_llm.adapters.documentation_rag import JsonFileLocalCorpusRegistry
from margpa_runtime_llm.bootstrap.audit_evidence import build_generation_observer
from margpa_runtime_llm.bootstrap.constitution import build_constitution_provider
from margpa_runtime_llm.bootstrap.dev_agent import build_dev_agent_run_service
from margpa_runtime_llm.bootstrap.documentation_rag import (
    build_documentation_rag,
    build_local_documentation_rag,
)
from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_governance_definitions_runtime,
)
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.bootstrap.web_knowledge import build_web_knowledge_service
from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationScopeId
from margpa_runtime_llm.modules.data_controls.ports import DataControlConsentStorePort
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagPlatform,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.web_knowledge.contracts import WebEvidenceGovernanceMode
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
    parser.add_argument(
        "--phase-3-governance-definitions",
        action="store_true",
        help=(
            "Enable loopback-only Phase 3 Governance Definitions Runtime "
            "(Default Mode off; no Model I/O change)"
        ),
    )
    parser.add_argument(
        "--phase-3-governance-definitions-root",
        type=Path,
        metavar="DEFINITIONS_ROOT",
        help=(
            "Filesystem Definition Provider root (must contain manifest.json). "
            "Omitted: Empty Provider (definitions=0 Baseline)."
        ),
    )
    parser.add_argument(
        "--phase-4-runtime-governance",
        action="store_true",
        help=(
            "Enable loopback-only Phase 4 Main Runtime Governance "
            "(Default Mode off; no Model I/O change)"
        ),
    )
    parser.add_argument(
        "--phase-4-runtime-governance-definitions-root",
        type=Path,
        metavar="DEFINITIONS_ROOT",
        help=(
            "Filesystem Definition Provider root for the ARGD/DAGD Reference "
            "Bundle (must contain manifest.json). Omitted: Empty Descriptor Set "
            "(Definitions-0 Baseline, P4-GD-005)."
        ),
    )
    parser.add_argument(
        "--phase-5-guardrail-governance",
        action="store_true",
        help=(
            "Enable loopback-only Phase 5 Guardrail/Security/Policy/Authority "
            "Governance (Default Mode off; no Model I/O change)"
        ),
    )
    parser.add_argument(
        "--phase-6-runtime-model-control",
        action="store_true",
        help=(
            "Enable loopback-only Phase 6 Runtime Model Control "
            "(Model identity/status, Context Size, Max New Tokens)"
        ),
    )
    parser.add_argument(
        "--phase-6-feature-modes",
        action="store_true",
        help=(
            "Enable loopback-only Phase 6 Judge/Repair/Recording Mode toggles "
            "(Default Mode off for all three; OBSERVE/ENFORCE Judge and Repair "
            "do call the live Generation path — P6-RR-P-WU-005)"
        ),
    )
    parser.add_argument(
        "--phase-7-local-corpus",
        action="store_true",
        help=(
            "Enable loopback-only Phase 7 Local Corpus document register/update/"
            "delete (P7-B), composed into Documentation RAG retrieval alongside "
            "the fixed project documentation corpus"
        ),
    )
    parser.add_argument(
        "--local-corpus-runtime-data-root",
        type=Path,
        metavar="RUNTIME_DATA_ROOT",
        help=(
            "Absolute server-owned runtime-data root for the Local Corpus "
            "registry (default: same as --conversation-runtime-data-root, "
            "else <project root>/runtime_data)"
        ),
    )
    parser.add_argument(
        "--local-corpus-scope-id",
        metavar="SCOPE_ID",
        help=(
            "Local Corpus storage scope identity (default: --conversation-scope-id, else 'default')"
        ),
    )
    parser.add_argument(
        "--phase-7-web-search",
        action="store_true",
        help=(
            "Enable loopback-only Phase 7 Governed Web Search/Fetch (P7-E/F). "
            "Manual activation only (initial value OFF; client requests explicit "
            "activation per call). Uses a Fixture Search/Fetch Provider pair — "
            "no real Search API is configured in this Task."
        ),
    )
    parser.add_argument(
        "--phase-7-web-search-governance-mode",
        choices=["off", "observe", "enforce"],
        default="off",
        metavar="MODE",
        help="Web Evidence Governance mode for Document Prompt Injection Detection (default: off)",
    )
    parser.add_argument(
        "--phase-7-data-controls",
        action="store_true",
        help=(
            "Enable loopback-only Phase 7 Data Controls (P7-G): per-Purpose "
            "Consent (Feedback/Synthetic/Training Export, default OFF) and "
            "read-only Retention facts"
        ),
    )
    parser.add_argument(
        "--data-controls-runtime-data-root",
        type=Path,
        metavar="RUNTIME_DATA_ROOT",
        help=(
            "Absolute server-owned runtime-data root for the Data Controls "
            "consent store (default: --conversation-runtime-data-root, else "
            "<project root>/runtime_data)"
        ),
    )
    parser.add_argument(
        "--data-controls-scope-id",
        metavar="SCOPE_ID",
        help=(
            "Data Controls storage scope identity "
            "(default: --conversation-scope-id, else 'default')"
        ),
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
        governance_definitions_enabled = _governance_definitions_enabled(
            enabled=args.phase_3_governance_definitions,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        runtime_governance_enabled = _runtime_governance_enabled(
            enabled=args.phase_4_runtime_governance,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        guardrail_governance_enabled = _guardrail_governance_enabled(
            enabled=args.phase_5_guardrail_governance,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        runtime_model_control_enabled = _runtime_model_control_enabled(
            enabled=args.phase_6_runtime_model_control,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        feature_modes_enabled = _feature_modes_enabled(
            enabled=args.phase_6_feature_modes,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        local_corpus_enabled = _local_corpus_enabled(
            enabled=args.phase_7_local_corpus,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        web_search_enabled = _web_search_enabled(
            enabled=args.phase_7_web_search,
            host=args.host,
            access_mode=web_access_profile.access.mode,
            authentication_required=access_policy.authentication_required,
        )
        data_controls_enabled = _data_controls_enabled(
            enabled=args.phase_7_data_controls,
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
        local_corpus_registry: LocalCorpusRegistryPort | None = None
        if local_corpus_enabled:
            local_corpus_runtime_data_root, local_corpus_scope_id = _local_corpus_registry_settings(
                runtime_data_root=args.local_corpus_runtime_data_root,
                scope_id=args.local_corpus_scope_id,
                conversation_runtime_data_root=args.conversation_runtime_data_root,
                conversation_scope_id=args.conversation_scope_id,
                project_root=PROJECT_ROOT,
            )
            local_corpus_registry = JsonFileLocalCorpusRegistry(
                runtime_data_root=local_corpus_runtime_data_root,
                scope_key=local_corpus_scope_id,
            )
        web_knowledge_service = build_web_knowledge_service() if web_search_enabled else None
        web_search_governance_mode = WebEvidenceGovernanceMode(
            args.phase_7_web_search_governance_mode
        )
        data_controls_store: DataControlConsentStorePort | None = None
        if data_controls_enabled:
            data_controls_runtime_data_root, data_controls_scope_id = _data_controls_settings(
                runtime_data_root=args.data_controls_runtime_data_root,
                scope_id=args.data_controls_scope_id,
                conversation_runtime_data_root=args.conversation_runtime_data_root,
                conversation_scope_id=args.conversation_scope_id,
                project_root=PROJECT_ROOT,
            )
            data_controls_store = JsonFileDataControlConsentStore(
                runtime_data_root=data_controls_runtime_data_root,
                scope_key=data_controls_scope_id,
            )
        # P8-C: unconditionally composed (a purely local, Read-only File
        # load — the `constitution/` directory simply won't exist for a
        # deployment that never opted in, and `load_manifest()` already
        # fails closed to `ConstitutionManifestUnavailable` in that case).
        # `constitution_mode` stays `OFF` — no CLI flag exists yet to raise
        # it, matching this Task's "Provisional" scope (P8-REQ-016: OFF is
        # never `allow all`, so leaving it OFF has zero behavioral effect
        # beyond making the Manifest observable).
        constitution_provider = build_constitution_provider(project_root=PROJECT_ROOT)
        # P8-D/P8-E: unconditionally composed, same rationale as the
        # Constitution Provider above — zero external dependency at
        # Composition time beyond a private local directory, so there is no
        # "unavailable" state to gate behind a CLI Flag yet. Reuses the same
        # runtime_data_root/scope_id fallback resolution `_data_controls_settings`
        # already applies (no dedicated Dev Agent CLI Flag exists yet) so a
        # Restart of this same process/host recovers every prior Run.
        dev_agent_runtime_data_root = args.conversation_runtime_data_root or (
            PROJECT_ROOT / "runtime_data"
        )
        dev_agent_scope_id = args.conversation_scope_id or "default"
        dev_agent_run_store = JsonFileDevAgentRunStore(
            runtime_data_root=dev_agent_runtime_data_root,
            scope_key=dev_agent_scope_id,
        )
        # P8-MR5 (P8-MANUAL-005): Production Composition wires the
        # traceable real-File Fixture Workspace Adapter, confined to this
        # same `runtime_data_root`/`scope_id` (never Project Source).
        dev_agent_run_service = build_dev_agent_run_service(
            run_store=dev_agent_run_store,
            runtime_data_root=dev_agent_runtime_data_root,
            scope_key=dev_agent_scope_id,
        )
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
                    local_corpus_registry=local_corpus_registry,
                )
            elif (
                web_access_profile.access.mode is WebExposureMode.LOCAL
                and _local_mac_documentation_rag_eligible()
            ):
                documentation_composition = build_local_documentation_rag(
                    project_root=PROJECT_ROOT,
                    defaults_path=DEFAULT_DOCUMENTATION_RAG_DEFAULTS,
                    feature_path=DEFAULT_LOCAL_DOCUMENTATION_RAG_PROFILE,
                    local_corpus_registry=local_corpus_registry,
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
        # Built before runtime_factory (not after create_web_app, as a
        # standalone Phase 3 feature would be) so Configuration Control's
        # Preview/Apply — which now owns Governance Mode Mutation
        # (P3-CODEX-001) — can be wired to the same live Runtime instance.
        governance_definitions_runtime = (
            build_governance_definitions_runtime(
                definitions_root=args.phase_3_governance_definitions_root,
            )
            if governance_definitions_enabled
            else None
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
            governance_definitions_runtime=governance_definitions_runtime,
            runtime_governance_enabled=runtime_governance_enabled,
            runtime_governance_definitions_root=args.phase_4_runtime_governance_definitions_root,
            guardrail_governance_enabled=guardrail_governance_enabled,
            runtime_model_control_enabled=runtime_model_control_enabled,
            feature_modes_enabled=feature_modes_enabled,
            local_corpus_registry=local_corpus_registry,
            web_knowledge_service=web_knowledge_service,
            web_search_governance_mode=web_search_governance_mode,
            data_controls_store=data_controls_store,
            constitution_provider=constitution_provider,
            dev_agent_run_service=dev_agent_run_service,
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
        app.state.governance_definitions_runtime = governance_definitions_runtime
        app.state.generation_observer = (
            build_generation_observer(
                project_root=PROJECT_ROOT,
                mode_provider=partial(
                    _current_governance_mode_value, governance_definitions_runtime
                ),
            )
            if governance_definitions_enabled
            else None
        )
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


def _governance_definitions_enabled(
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
                "Phase 3 Governance Definitions requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _runtime_governance_enabled(
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
                "Phase 4 Runtime Governance requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _guardrail_governance_enabled(
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
                "Phase 5 Guardrail Governance requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _runtime_model_control_enabled(
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
                "Phase 6 Runtime Model Control requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _local_corpus_enabled(
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
                "Phase 7 Local Corpus requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _local_corpus_registry_settings(
    *,
    runtime_data_root: Path | None,
    scope_id: str | None,
    conversation_runtime_data_root: Path | None,
    conversation_scope_id: str | None,
    project_root: Path,
) -> tuple[Path, str]:
    resolved_root = (
        runtime_data_root or conversation_runtime_data_root or (project_root / "runtime_data")
    )
    resolved_scope = scope_id or conversation_scope_id or "default"
    return resolved_root, resolved_scope


def _data_controls_enabled(
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
                "Phase 7 Data Controls requires local loopback access and explicit opt-in."
            ),
        )
    return True


def _data_controls_settings(
    *,
    runtime_data_root: Path | None,
    scope_id: str | None,
    conversation_runtime_data_root: Path | None,
    conversation_scope_id: str | None,
    project_root: Path,
) -> tuple[Path, str]:
    resolved_root = (
        runtime_data_root or conversation_runtime_data_root or (project_root / "runtime_data")
    )
    resolved_scope = scope_id or conversation_scope_id or "default"
    return resolved_root, resolved_scope


def _web_search_enabled(
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
            safe_message=("Phase 7 Web Search requires local loopback access and explicit opt-in."),
        )
    return True


def _feature_modes_enabled(
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
                "Phase 6 Judge/Repair/Recording Mode requires local loopback access and "
                "explicit opt-in."
            ),
        )
    return True


def _current_governance_mode_value(
    runtime: GovernanceDefinitionsRuntime | None,
) -> str:
    if runtime is None:
        return "off"
    return runtime.mode_snapshot().current_mode.value


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
