"""Bootstrap composition for the Phase 3 Non-intervening Generation
Observation Hook (P3-F-WU-005, P3-CODEX-002/012 rework).

`project_root` is passed to `LocalJsonlEvidenceStore` as its Server-owned
Trusted `anchor` — never from user input (architecture §4.4) — with
`_EVIDENCE_RELATIVE_ROOT` (`runtime_data/audit_evidence`) as the
`relative_root` walked below it via the Store's own `O_NOFOLLOW` dir_fd
chain (P3-CODEX-012), independent of Conversation storage
(architecture §10). `mode_provider` is expected to read the live
Governance Mode (e.g. `governance_definitions_runtime.mode_snapshot().
current_mode.value`) so Evidence writing tracks Mode changes made after
startup, not just the boot-time flag.

The `LocalJsonlEvidenceStore` — and therefore its on-disk directory tree
— is built lazily, only on the first actual Evidence append, so a
process that never leaves `off` never touches `runtime_data/` at all.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from margpa_runtime_llm.adapters.audit_evidence.evidence_generation_observer import (
    EvidenceGenerationObserver,
)
from margpa_runtime_llm.adapters.audit_evidence.evidence_governance_observer import (
    EvidenceGovernanceObserver,
)
from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import LocalJsonlEvidenceStore
from margpa_runtime_llm.modules.audit_evidence.domain import AuditRunId
from margpa_runtime_llm.modules.audit_evidence.generation_observation import GenerationObserverPort
from margpa_runtime_llm.modules.audit_evidence.governance_observation import GovernanceObserverPort
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceStorePort

_EVIDENCE_SCOPE = "web_preview"
_SOURCE_COMPONENT = "web.generation_lifecycle"
_EVIDENCE_RELATIVE_ROOT = "runtime_data/audit_evidence"
# A distinct Scope from Generation Evidence (`_EVIDENCE_SCOPE`) so a Write
# failure on one side never degrades the other — `LocalJsonlEvidenceStore`
# tracks Degraded State per-instance and it never clears without a restart.
_GOVERNANCE_EVIDENCE_SCOPE = "runtime_governance"
_GOVERNANCE_SOURCE_COMPONENT = "web.runtime_governance"


def build_generation_observer(
    *, project_root: Path, mode_provider: Callable[[], str]
) -> GenerationObserverPort:
    def _store_factory() -> EvidenceStorePort:
        return LocalJsonlEvidenceStore(
            anchor=project_root,
            relative_root=_EVIDENCE_RELATIVE_ROOT,
            scope=_EVIDENCE_SCOPE,
        )

    return EvidenceGenerationObserver(
        store_factory=_store_factory,
        run_id=AuditRunId(value=str(uuid4())),
        source_component=_SOURCE_COMPONENT,
        mode_provider=mode_provider,
    )


def build_governance_observer(
    *, project_root: Path, mode_provider: Callable[[], str]
) -> GovernanceObserverPort:
    def _store_factory() -> EvidenceStorePort:
        return LocalJsonlEvidenceStore(
            anchor=project_root,
            relative_root=_EVIDENCE_RELATIVE_ROOT,
            scope=_GOVERNANCE_EVIDENCE_SCOPE,
        )

    return EvidenceGovernanceObserver(
        store_factory=_store_factory,
        run_id=AuditRunId(value=str(uuid4())),
        source_component=_GOVERNANCE_SOURCE_COMPONENT,
        mode_provider=mode_provider,
    )
