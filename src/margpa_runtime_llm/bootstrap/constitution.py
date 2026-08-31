"""Phase 8 (P8-C): composition root for the Provisional Runtime Constitution.

`project_root` is always the caller's own already-resolved value — never
re-derived or hard-coded here (P8-REQ-019).
"""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.constitution import JsonFileConstitutionProvider
from margpa_runtime_llm.modules.constitution import ConstitutionProviderPort


def build_constitution_provider(*, project_root: Path) -> ConstitutionProviderPort:
    return JsonFileConstitutionProvider(project_root=project_root)
