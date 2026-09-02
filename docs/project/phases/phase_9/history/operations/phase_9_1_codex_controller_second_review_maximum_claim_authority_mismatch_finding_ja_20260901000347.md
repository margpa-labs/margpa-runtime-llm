# Phase 9-1 Codex Controller Second Review — Maximum Claim Authority Mismatch Finding

```yaml
document_id: phase_9_1_codex_controller_second_review_maximum_claim_authority_mismatch_finding_20260901000347
document_state: rework_required
language: ja
created_at: 2026-09-01T00:03:47+09:00
phase: phase_9
program: phase_9_1
finding_count: 1
source_role: codex_controller
```

## 1. Review Conclusion

P9-CODEX-001〜004の実装、Focused Validation、38 Acceptance個別行、Real Artifact／User Manual GateおよびCorrected Manual順序は受理可能である。

ただしFrozen Acceptance／Requirements／Execution Planが最大Claimを次へ固定している。

```text
P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Post-Claude Rework Return群は次を最大Claimとして使用している。

```text
P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

前者より先の状態を表す独自Claimであり、P9-ACC-038の正確な文字列／停止線と一致しない。そのためP9-ACC-038を現状のままPASSとして受理しない。

## 2. Finding

### P9-CODEX-005 — Frozen Maximum Claim不一致

```yaml
severity: moderate
priority: P0_STATE_TRUTHFULNESS
scope: docs_and_current_phase_index_only
implementation_blocker: false
closure_blocker: true
source_mutation_required: false
```

Frozen正本：

- `docs/project/phases/phase_9/requirements/phase_9_requirements_ja.md` §4.4。
- `docs/project/phases/phase_9/operations/phase_9_execution_plan_ja.md` P9-1-D Exit。
- `docs/project/phases/phase_9/operations/phase_9_acceptance_matrix_ja.md` P9-ACC-038。
- `docs/project/phases/phase_9/history/operations/phase_9_pre_phase_8_closure_three_program_design_and_execution_freeze_ja_20260831210244.md`。

不一致対象：

- Post-Claude Quota Acceptance Addendum。
- Post-Claude Quota Recovery。
- Post-Claude Quota Exact Return。
- Phase Indexの`current_program`。

Real Artifact 2件とUser Manual 1件が未実施であること自体は正しく保持されており、Gate分類を変える必要はない。必要なのは最大ClaimとCurrent State名だけをFrozen正本へ戻すDocs-only訂正である。

## 3. Controller-originated Error Disclosure

この不一致はExecutorの独自過大Claimだけではない。先行Controller Finding Ledger §5およびClaude／Codex用Rework Handoffで、Controller自身が誤って次をAfter-Rework Claimとして指示した。

```text
P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

ExecutorはそのAuthorityに従った。したがってP9-CODEX-005をExecutorだけのFailureへ転嫁しない。Frozen Requirements／Execution Plan／Acceptance Matrixより、Controllerが後から作った独自Claimを優先したController Authority／State Truthfulness Failureとして保持する。

## 4. Required Micro Rework

Append-onlyで次を作る。

1. Maximum Claim Correction Addendum。
2. P9-CODEX-005 Micro Recovery。
3. Corrected Exact Return Handoff。
4. Phase IndexのCurrent State／`current_program`を`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`へ整合。

Historical Handoff／Recovery／Finding Ledgerは改変しない。Correction Addendumから明示的にSupersedeする。

Acceptance内訳は次を維持する。

```text
PASS 35
RESOURCE_GATED / NOT RUN 2
USER MANUAL GATE / NOT RUN 1
TOTAL 38
```

P9-ACC-038は訂正後の正確なClaimをEvidenceとしてPASSを維持する。

## 5. Stop Line

- Source／Test／Manual本文の変更なし。
- Test／Mypy／Ruff／Build再実行なし。
- Real Model／Artifact／Browser／Networkなし。
- Phase 9-2／Closure／Git／Roadmapなし。
- 新しいReview Loopなし。

訂正後は`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`としてController Final Re-review待ちで停止する。
