# Phase 9-1 Maximum Claim Correction Addendum

```yaml
document_id: phase_9_1_maximum_claim_correction_addendum_20260901000630
document_state: final_append_only_correction
language: ja
created_at: 2026-09-01T00:06:30+09:00
phase: phase_9
program: phase_9_1
finding: P9-CODEX-005
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Frozen Correction

Phase 9-1のCurrent／Final Maximum Claimを次へ統一する。

```text
P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

次の文字列はHistorical Controller-originated誤Claimであり、Current Claimとしては本AddendumがSupersedeする。

```text
P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

この不一致はExecutorだけのFailureではない。先行Controller Finding LedgerとClaude／Codex Exact Authorityが誤ClaimをAfter-Rework Maximumとして指定し、ExecutorはそのAuthorityに従った。Frozen Requirements／Execution Plan／Acceptance Matrixを優先する本Correctionにより解消する。

## 2. Historical Documents Superseded for Maximum Claim Only

次の文書はHistorical Evidenceとして改変しない。実装、Validation、Acceptance、Manual、Gateは有効なまま保持し、`maximum_claim`および同義のCurrent State表現だけを本AddendumがSupersedeする。

- `docs/project/phases/phase_9/history/operations/phase_9_1_post_claude_quota_acceptance_disposition_addendum_ja_20260831234930.md`
- `docs/project/phases/phase_9/history/index/phase_9_1_post_claude_quota_continuation_recovery_ja_20260831234930.md`
- `docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_exact_return_handoff_ja_20260831234930.md`
- `docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_continuation_exact_handoff_ja_20260831234357.md`
- `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md`

## 3. Preserved State

```text
P9-CODEX-001〜004: COMPLETE candidate
P9-CODEX-005: COMPLETE by this Docs-only Correction
PASS: 35
RESOURCE_GATED / NOT RUN: 2
USER MANUAL GATE / NOT RUN: 1
TOTAL: 38
Corrected Manual: unchanged
Existing Validation: unchanged
Source／Test mutation: 0
```

P9-ACC-038は、Phase IndexとCorrected Exact ReturnがFrozen Maximum Claimへ一致したことをEvidenceとしてPASSを維持する。

## 4. Claims Not Made

User Manual PASS、Real Artifact PASS、Phase 9-1 Closure、Phase 9-2／9-3開始、Git状態を主張しない。
