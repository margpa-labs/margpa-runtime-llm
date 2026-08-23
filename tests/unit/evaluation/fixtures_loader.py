"""Loads the synthetic Qwen-known-failure-modes fixture manifest for tests.

Test-scoped only: no production Dataset loader exists yet (that is
Phase 6-H's Experiment Freeze concern). This keeps the Tracked Evaluation
Fixture separate from any User Runtime Result, per Architecture 6.1.
"""

import hashlib
import json
from pathlib import Path

from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase, EvaluationDataset

_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "qwen_known_failure_modes_manifest.json"


def load_qwen_known_failure_modes() -> tuple[EvaluationDataset, tuple[EvaluationCase, ...]]:
    raw_bytes = _FIXTURE_PATH.read_bytes()
    digest = hashlib.sha512(raw_bytes).hexdigest()
    payload = json.loads(raw_bytes)
    dataset = EvaluationDataset(
        dataset_id=payload["dataset_id"],
        revision=payload["revision"],
        digest_sha512=digest,
        source_class=payload["source_class"],
    )
    cases = tuple(
        EvaluationCase(
            case_id=raw_case["case_id"],
            input=raw_case["input"],
            reference=raw_case["reference"],
            criteria=tuple(raw_case["criteria"]),
            language=raw_case["language"],
            tags=tuple(raw_case["tags"]),
        )
        for raw_case in payload["cases"]
    )
    return dataset, cases
