# Phase 9-1 三連続完全別観点Controller Independent Review — 実測Evidence

```yaml
document_id: phase_9_1_three_fully_distinct_controller_independent_review_empirical_evidence_20260901033839
document_type: append_only_automation_empirical_evidence
document_state: recorded
language: ja
created_at: 2026-09-01T03:38:39+09:00
scope: phase_9_1_exceptional_three_review_experiment
review_owner: Codex_project_controller
default_review_count: 2
default_review_policy_changed: false
generalization_grade: strong_single_program_evidence_not_universal_proof
```

## 1. 目的

Phase 9-1へ、互いに前提・Source Order・Failure仮説が異なるIndependent Reviewを3回適用した結果を記録する。評価対象は「3回読んだこと」ではなく、2回目／3回目が先行Reviewで見逃したCritical／Majorを実際に追加検出したかである。

既定運用は観点変更二段階Reviewのままとし、本件を理由に全Taskを三段階へ変更しない。Phase 9-1はReal Model、Semantic Governance、Judge／Repair／Guard、Provider Lifecycle、User Manualが交差し、過去Phase 6由来の再発Riskも高いため、User Authorityにより例外的に3回目を追加した。

## 2. 三つのReviewは何が違ったか

### Review 1 — Requirement／Acceptance／Source／Test／Claim Conformance

```text
起点:
  Exact Handoff
  Requirements
  Acceptance Matrix
  Executor Return

主質問:
  申告ClaimはSource／Test／Authorityと一致するか
```

検出・訂正：

- P9-CODEX-001: Dedicated Production Authority入口。
- P9-CODEX-002: Repair→Rejudge実Composition Evidence。
- P9-CODEX-003: 38 AcceptanceとCurrent Stateの整合。
- P9-CODEX-004: User ManualのLifecycle順序。
- P9-CODEX-005: Maximum Claim Authority不一致。
- User Correction: Real Selene／Qwen3GuardをResource GateのままPhase 9-1完了条件から外せる、というRequirement／Controller停止線そのものがUser Intentより緩かった。

### Review 2 — Operator Journey／Production Reachability

```text
起点:
  CLI Startup
  Production Composition
  実Artifact
  Provider Selection

主質問:
  UserがONにした時、実ModelのLoad→Prompt→Inference→Decode→Evidenceへ本当に到達するか
```

Review 1のAcceptance件数やPASS Claimを前提にせず、Production経路を前から後ろへ追った結果、次を追加検出した。

- P9-CODEX-006 Critical: Selene公式Promptと現Project独自JSON Contractが両立せず、現在のProduction Seleneは実Semantic評価不能。
- P9-CODEX-007 Major: Dedicated PreflightがArtifact／Digest／Manifest／Hardwareを確認するというClaimが実装より強い。

### Review 3 — Temporal State／Concurrency／Lifecycle

```text
起点:
  State Machine
  Resource Ownership
  Lease Identity
  Deadline／Cancel

主質問:
  途中失敗、並行Turn、二重Release、OFF、Timeout、ShutdownでもStateとResource所有権を守れるか
```

Requirement行や正常系User Flowを起点にせず、時間軸上の反転Probeを行った結果、次を追加検出した。

- P9-CODEX-008 Critical: Candidate部分Load失敗後のModel ResourceがLoad済みのまま追跡不能になる。
- P9-CODEX-009 Critical: Duplicate／Stale Lease Releaseが他の実行中Turnを減算し、早期Unloadできる。
- P9-CODEX-010 Major: Qwen3Guard実InferenceにDeadline／Cancellationがなく、Stop／OFF／Shutdownが実CallをPreemptできない。

## 3. 定量結果

```text
Review 1後の追加検出:
  Review 2: Critical 1 / Major 1
  Review 3: Critical 2 / Major 1

追加合計:
  Critical 3
  Major 2
  Material Finding 5
```

したがって本件では、3連続完全別観点Reviewに明確な追加検出価値があった。Review 2／3のどちらも、Review 1のFindingを言い換えただけではなく、別のSource境界、別のFailure機序および別の修正対象を検出した。

## 4. 先行Reviewが見逃した理由

| Finding群 | 先行Reviewが見逃した主因 | 観点変更で見えたもの |
|---|---|---|
| 001〜005 | Executor Claimと正本の適合を中心に見た | Authority／Claim／Acceptance不整合 |
| Real Artifact必須条件 | Canonical Requirement自体を正しい前提として扱った | `Canonical ≠ Correct`、User IntentとのSemantic Closure |
| 006〜007 | Type／Fixture／Test成立をProduction成立へ寄せて読んだ | 実Prompt Contract不一致、Preflight Claimの過大さ |
| 008 | `load()`を実質Atomicと仮定し、FakeがResource取得前に失敗した | Load後半例外と所有権喪失 |
| 009 | Leaseの固有Generation発行だけを確認した | Generationが消費・照合されず再利用可能 |
| 010 | `except TimeoutError`の存在をTimeout保証と暗黙に扱った | Timer／Budget／CancellationのProduction配線欠落 |

## 5. 修正箇所とRework対応

| Finding | 主修正対象 | 必須Regression Evidence |
|---|---|---|
| P9-CODEX-006 | Selene Prompt Assembly／呼出し粒度／Strict Decode／Evidence集約／Role Preflight | 公式Source Identityを保持した実Contract、Real Artifact実Inference |
| P9-CODEX-007 | `_run_dedicated_preflight()`とFailure Reason／Docs Claim | Preflight各Stageの実行有無と失敗理由を個別証明 |
| P9-CODEX-008 | `RoleProviderLifecycleManager._activate_locked()`／`_transition_to_locked()`／Dedicated Adapter cleanup | 部分Load後例外、cleanup例外、rollback例外、NONE／BUILT_IN unload失敗 |
| P9-CODEX-009 | Active Lease Registry／`begin_role_turn()`／`end_turn()` | Duplicate、Stale、Forged、Provider不一致、Drain Thread Race |
| P9-CODEX-010 | Qwen3Guard Call Budget／Cancellation／Tracked Worker／Late Result抑止 | Input／Context／Output timeout、User Stop、Mode OFF、Shutdown Race |

実Selene／Qwen3Guardは、双方について次を一つのProduction Evidence Chainとして成立させる。

```text
Explicit Authority
→ Preflight
→ Real Artifact Load
→ Real Inference
→ Strict Decode
→ Executed Provider／Artifact／Contract Identity Evidence
→ Mode OFF／Stop
→ Active Turn Drain
→ Unload
```

## 6. 運用上の結論

有効だったのはReview回数そのものではなく、各回が別の問いを持ったことである。

```text
Review 1: 書かれた契約へ適合しているか
Review 2: 実利用者がProduction経路へ到達できるか
Review 3: 時間と並行性で契約が壊れないか
```

同じSource Order、同じAcceptance表、同じTest再実行を3回繰り返しても、本Evidenceの三段階Reviewには数えない。

既定値は次のまま変更しない。

```text
通常のMaterial Change:
  観点変更二段階Review

例外的な第三Review候補:
  Real Model／外部Resource／Lifecycle／Concurrencyが同時に交差する
  先行ReviewでCriticalが継続して検出される
  Canonical Requirement自体の誤りが発見された
  複数Phaseにまたがる再発Findingがある
  UserがResource価値を認めて明示的に許可する
```

第三Reviewは、自動的な品質競争または未解決0件化へ使わない。PoC／MVP BlockerだけをReworkし、Minor／Polish／Enterprise Hardeningは未解決へ送る。

## 7. Resource／Human Cost

三段階ReviewはToken、Tool Call、経過時間だけでなく、Userの確認、画面張り付き、睡眠、判断疲労を消費する。したがって、追加Reviewの評価関数にはHuman Attention Costも含める。

今回のようにCritical 3／Major 2を追加検出した場合は費用対効果が成立する。一方、第三Reviewが既存Findingの再記述だけなら、既定二段階へ戻し、追加Resourceを実画面Testまたは次Phaseへ配分する。

## 8. Evidence参照

- `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md`
- `docs/project/phases/phase_9/history/operations/phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_ja_20260901001700.md`
- `docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_2_operator_journey_production_reachability_ja_20260901032224.md`
- `docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_3_temporal_state_concurrency_lifecycle_ja_20260901033408.md`
- `docs/project/shared/history/automation/phase_8_changed_perspective_two_cycle_controller_review_empirical_evidence_ja_20260831070840.md`
