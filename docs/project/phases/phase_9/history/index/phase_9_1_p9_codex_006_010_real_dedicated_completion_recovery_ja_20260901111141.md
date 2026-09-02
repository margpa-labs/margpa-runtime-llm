# Phase 9-1 P9-CODEX-006〜010 Real Dedicated Completion Recovery

```yaml
document_id: phase_9_1_p9_codex_006_010_real_dedicated_completion_recovery_20260901111141
document_state: complete_recovery
language: ja
created_at: 2026-09-01T11:11:41+09:00
phase: phase_9
program: phase_9_1
scope: p9_codex_006_to_010_only
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Completion Status

```text
P9-CODEX-006: COMPLETE
P9-CODEX-007: COMPLETE
P9-CODEX-008: COMPLETE
P9-CODEX-009: COMPLETE
P9-CODEX-010: COMPLETE
```

Phase 9-2 / 9-3、Git、Commit、Push、Backupは未実行。

## 2. Exact Changed Paths

- `config/judge_templates/selene/manifest.json`
- `config/judge_templates/selene/project_derived_multi_criterion_prompt_v1.txt`
- `src/margpa_runtime_llm/adapters/evaluation/selene.py`
- `src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py`
- `tests/unit/evaluation/test_selene_adapter.py`
- `tests/unit/evaluation/test_judge_prompt_and_decoder.py`
- `tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py`
- `docs/project/phases/phase_9/history/index/phase_9_1_p9_codex_006_010_real_dedicated_completion_recovery_ja_20260901111141.md`
- `docs/project/phases/phase_9/history/operations/phase_9_1_copilot_automation_evidence_real_dedicated_ja_20260901111141.md`
- `docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_real_dedicated_completion_exact_return_handoff_ja_20260901111141.md`

## 3. Exact Last Tests and Results

```text
./.venv/bin/pytest -q
=> 2216 passed, 7 deselected

./.venv/bin/ruff check
=> All checks passed

./.venv/bin/mypy src tests
=> Success: no issues found in 558 source files
```

## 4. Real Dedicated Evidence Summary

- Selene: authority on preflight成功、real GGUF load成功、semantic criterion executed > 0、provider=`judge.selene-1-mini-llama-3.1-8b-q5-k-m`、`provider_state=active`。
- Qwen3Guard: authority on preflight成功、real GGUF load成功、input/context/output_candidateの3経路実推論成功、provider=`guard.qwen3guard-gen-0.6b-q8-0`。
- Bounded negative path: 1ms budgetで`unknown_unresolved`即時返却、tracked worker drain後にclean shutdown=true。

## 5. Open Findings / Gates

- 重大Blocker: なし（P9-CODEX-006〜010 scope）
- User Manual / Real Browser Gate: あり（UI操作の人手確認は未実施）

## 6. Active Process / Temporary Artifact

```text
active_process: none
loaded_model_state: none
temporary_artifact_created: none
rollback_forbidden_scope: P9-CODEX-001〜005 preserved candidate
```

## 7. Exact Next Action

Codex Controller Independent Reviewへ本Returnを引き渡し、Executorは停止する。
