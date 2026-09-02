# Phase 9-1 Copilot Real Dedicated Completion Exact Return Handoff

```yaml
document_id: phase_9_copilot_p9_1_real_dedicated_completion_exact_return_handoff_20260901111141
document_state: complete_candidate_for_controller_review
language: ja
created_at: 2026-09-01T11:11:41+09:00
phase: phase_9
program: phase_9_1
provider: copilot
role: designer_implementer
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_9_1_closure: NOT_CLAIMED
phase_9_2: NOT_STARTED
git_action: NONE
```

## 1. Final Disposition (P9-CODEX-006〜010)

```text
P9-CODEX-006: COMPLETE
  - Selene contractをofficial copyとproject-derived contractで分離
  - derived template digestとproject contract digestを独立保持
  - preflightでprompt/manifest/placeholder/decoder compatibilityを先行検証

P9-CODEX-007: COMPLETE
  - dedicated preflightの責務をstatic definition + capability probeへ厳密化
  - role-specific contract checkはSelene adapter preflightへ分離

P9-CODEX-008: COMPLETE
  - candidate load failure時cleanup/rollback/degraded収束を実装済み（既存差分維持）

P9-CODEX-009: COMPLETE
  - generation lease identity registry + exactly-once releaseを実装済み（既存差分維持）

P9-CODEX-010: COMPLETE
  - Qwen3Guard deadline/cancellation/tracked worker bounded executionを実装済み（既存差分維持）
```

## 2. Real Evidence

### 2.1 Selene

- Authority ON preflight: success
- Real GGUF load: success
- Inference + strict decode: success (`provider_state=active`, `result_count=1`)
- Executed provider: `judge.selene-1-mini-llama-3.1-8b-q5-k-m`
- Mode OFF / unload: success

### 2.2 Qwen3Guard

- Authority ON preflight: success
- Real GGUF load: success
- Input / Context Source / Output Candidateの3経路実行: success
- Executed provider: `guard.qwen3guard-gen-0.6b-q8-0`
- Artifact/manifest identity付きでevidence保持: success
- Bounded negative path (1ms budget): `unknown_unresolved`即時返却 + tracked worker drain + clean shutdown=true

## 3. Lifecycle / Lease / Deadline Negative Probe

- Duplicate/Stale/Forged lease、candidate partial-load cleanup、rollback再preflight、NONE/BUILT_IN unload failureはunit regressionで網羅済み。
- Qwen timeout/cancel pathはreal adapter + detector bounded probeでunknown typed outcomeに収束し、late publish不採用を維持。

## 4. Internal Review (Two-cycle, perspective-shifted)

Cycle 1 (Runtime/Regression/Negative Path):
- Selene実出力の`confidence`がstringで返る実挙動を検出し、decoderにnumeric-string strict decodeを追加。
- 既存strictness（range/finite/unexpected field/criterion completeness）は維持。

Cycle 2 (Production Composition/Temporal State/Evidence Truthfulness/User Flow):
- Derived Selene contractをofficial copy claimから分離し、provenanceを正直化。
- dedicated role実経路のload→inference→evidence→unloadを実機で再確認。

追加Blocker: なし（P9-1 scope）

## 5. Acceptance / Validation

```text
Full backend pytest: 2216 passed, 7 deselected
ruff check: pass
mypy src tests: pass (558 source files)
```

## 6. Artifacts

- Recovery Index:
  `docs/project/phases/phase_9/history/index/phase_9_1_p9_codex_006_010_real_dedicated_completion_recovery_ja_20260901111141.md`
- Copilot Automation Evidence:
  `docs/project/phases/phase_9/history/operations/phase_9_1_copilot_automation_evidence_real_dedicated_ja_20260901111141.md`

## 7. User Manual Gate / Stop Line

- User Manual / Real Browser確認項目は未実施（gate保持）。
- Phase 9-1 Closure、Phase 9-2/9-3、Git、Commit、Push、Backupは未実施。

## 8. Exact Next

`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW` としてCodex Controller Independent Review待ち。
