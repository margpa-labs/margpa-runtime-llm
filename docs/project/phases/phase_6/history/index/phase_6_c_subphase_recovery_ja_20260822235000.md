# Phase 6-C Subphase Recovery（Evaluation Domain／Deterministic Judge）

```yaml
document_id: phase_6_c_subphase_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_c
work_unit: p6_c_wu001_wu002_wu003_wu005_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-22 23:50:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/evaluation/**
    （domain/identifiers.py, dataset.py, run.py, result.py／ports.py／
      application/evaluation_orchestrator.py）
  src/margpa_runtime_llm/adapters/evaluation/deterministic/evaluators.py
    （ExactReferenceMatch／RequiredFieldPresence／ContradictionMarker／
      UnsupportedClaimCandidate／FormatCompliance の5交換可能Evaluator）
  tests/unit/evaluation/**
    （domain 6、orchestrator 3、deterministic evaluators 10、baseline verification 6）
  tests/unit/evaluation/fixtures/qwen_known_failure_modes_manifest.json
    （Synthetic Dataset、6 Case：overconfidence／definition_confusion／
      insufficient_grounding／contradiction／format_deviation／uncertainty_expression）
  tests/unit/evaluation/fixtures_loader.py（Test-scoped Manifest Loader、SHA-512記録）
Modified: なし
```

## Work Unit対応

```text
P6-C-WU-001（Domain／Ports）        : 完了。EvaluationDataset／Case／Run／Result／
                                       EvaluatorBinding／Budget、DeterministicEvaluatorPort。
P6-C-WU-002（Dataset／Manifest）     : 完了（Test-scoped）。Qwenの知ったかぶり、定義混同、
                                       根拠不足、矛盾、形式逸脱、不確実性表現の6種を
                                       Synthetic Caseとして用意。Production Dataset Loader
                                       はPhase 6-H Experiment Freezeで正式化する。
P6-C-WU-003（Deterministic Registry）: 完了。5 Evaluator全てModel Call 0を保証（Gate依存
                                       ではなく実装自体がModel Port非参照）。
P6-C-WU-004（Result／Metric／Evidence）: EvaluationResult Contract自体でカバー済み
                                       （dimension_results／confidence／token・latency・
                                       call／evidence_refs）。独立実装は追加不要と判断。
P6-C-WU-005（Baseline Verification） : 完了。Model 0、Judge OFF Call 0、Deterministic-only、
                                       Unknown Reference、Malformed Case Fail-closedを検証。
```

## Validation

```text
New Unit Test  : 25 passed（Evaluation Domain全体）
Full Backend   : 1291 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff           : All checks passed
Mypy           : Success（357 source files）
```

## Next Exact Route

Phase 6-D（LLM-as-a-Judge、P6-D-WU-001 Typed Judge Adapter）へ進む。
