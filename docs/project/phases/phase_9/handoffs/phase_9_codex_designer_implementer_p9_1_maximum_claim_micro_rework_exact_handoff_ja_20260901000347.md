# Phase 9-1 Maximum Claim Micro Rework Exact Handoff

```yaml
document_id: phase_9_codex_designer_implementer_p9_1_maximum_claim_micro_rework_exact_handoff_20260901000347
document_state: frozen_ready
language: ja
created_at: 2026-09-01T00:03:47+09:00
phase: phase_9
program: phase_9_1
provider: Codex
role: designer_implementer
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
controller_thread_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
executor_thread_id: 01a03b6c-2a68-7881-99bc-c788a600f632
```

## 1. Objective

P9-CODEX-001〜004、38 Acceptance、Corrected Manual、Validation、Real Artifact／User Manual Gateをすべて保持し、P9-CODEX-005 Maximum Claim不一致だけをDocs-onlyで訂正する。

Mandatory Finding：

`docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_second_review_maximum_claim_authority_mismatch_finding_ja_20260901000347.md`

## 2. Frozen Correction

Current／Final maximum claimを次へ統一する。

```text
P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

次はHistorical Controller-originated誤ClaimとしてSupersedeする。

```text
P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

## 3. Exact Work

1. Maximum Claim Correction AddendumをAppend-only作成する。
2. 既存Post-Claude Acceptance／Recovery／ReturnはHistorical Evidenceとして改変せず、Correction AddendumからSupersedeする。
3. Phase Indexの`document_state`、`current_program`およびCurrent State表現をFrozen Claimへ合わせる。
4. P9-CODEX-005 Micro Recoveryを作成する。
5. Corrected Exact Returnを作成し、Controller Final Re-review待ちで停止する。

## 4. Preserve

```text
P9-CODEX-001〜004: COMPLETE candidate
PASS: 35
RESOURCE_GATED / NOT RUN: 2
USER MANUAL GATE / NOT RUN: 1
TOTAL: 38
Corrected Manual: unchanged
Source/Test mutation: 0
```

## 5. Prohibited

- Source／Test／Corrected Manual本文の変更。
- Test／Mypy／Ruff／Buildの再実行。
- Real Model／Artifact／Browser／Network／Root外／runtime_data。
- Phase 9-2／9-3、Closure、Git、Backup、Roadmap。
- Acceptance再分類または新Finding追加。
- Historical docsの直接改変。

## 6. Review

作成後、文字列照合だけを行う。

- Current Phase Indexに誤Claimが残らない。
- New Correction／Recovery／Returnの最大ClaimがFrozen文字列と一致する。
- Gate 3件とAcceptance合計38が変わらない。

Return後は停止する。
