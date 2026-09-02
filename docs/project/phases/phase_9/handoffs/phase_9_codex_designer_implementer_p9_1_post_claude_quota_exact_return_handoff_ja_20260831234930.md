# Phase 9-1 Post-Claude Quota Codex Designer Implementer Exact Return Handoff

```yaml
document_id: phase_9_codex_designer_implementer_p9_1_post_claude_quota_exact_return_handoff_20260831234930
document_state: complete_candidate_for_controller_independent_review
language: ja
created_at: 2026-08-31T23:49:30+09:00
phase: phase_9
program: phase_9_1
from_role: designer_implementer
to_controller_thread_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
phase_9_1_closure: NOT_CLAIMED
phase_9_2: NOT_STARTED
git_action: NONE
```

## 1. Direct Return

P9-CODEX-001〜004をCurrent Working Treeから完了候補として確定した。001 Production Authority Opt-inと002 Actual Repair／Rejudge Production Compositionは成立済み差分を保持し、003の38 Acceptance再導出、004のCorrected User Manual、二段階自己Reviewを完了した。

```text
P9-CODEX-001: COMPLETE
P9-CODEX-002: COMPLETE
P9-CODEX-003: COMPLETE
P9-CODEX-004: COMPLETE
```

## 2. Acceptance

個別Disposition正本：
`docs/project/phases/phase_9/history/operations/phase_9_1_post_claude_quota_acceptance_disposition_addendum_ja_20260831234930.md`

```text
PASS: 35
RESOURCE_GATED / NOT RUN: 2
USER MANUAL GATE / NOT RUN: 1
TOTAL: 38
rows 38 / unique 38 / missing 0 / duplicate 0
```

P9-ACC-008 Selene Real Artifact、P9-ACC-011 Qwen3Guard Real ArtifactはAuthorityがないためNOT RUN。P9-ACC-037 User Mac実画面はManual準備済み／NOT RUN。Fixture EvidenceをReal PASSへ昇格していない。

## 3. Validation／Changed Paths

Controller確認済みFocused `62 passed`、対象Mypy／Ruff／diff-check cleanを保持した。Phase 9-1成立済みCanonical Backendは`2200 passed, 7 deselected`、Mypy src/tests clean、Ruff clean。本ContinuationはDocs／Indexだけのため、成立済みTestを再実行していない。

Source／Test／DocsのExact Changed PathsはRecoveryを正本とする：
`docs/project/phases/phase_9/history/index/phase_9_1_post_claude_quota_continuation_recovery_ja_20260831234930.md`

## 4. Correct User Manual Order

正本：
`docs/project/phases/phase_9/history/operations/phase_9_1_corrected_user_manual_recheck_sheet_ja_20260831234930.md`

```text
1. Judge Mode OFF、Repair OFF、Current／Historical分離確認
2. Current Mainと一致するMain-shared Judge、またはAuthority対象Providerを選択
3. OFF状態のConfigured／Active／State／drain pendingを確認
4. Judge OBSERVE／ENFORCE、必要時Repair ENFORCE／Recording FULLを再適用
5. ON状態のConfigured／Active／State／Independenceを確認
6. 必ず新しいTurnを送信しRequest IDを記録
7. 109 Outcome総和、selected、evaluated、Executed Providerを確認
8. 必要時:judge→:repair→:rejudgeとFinalを確認
9. OFF／Unload／Call 0／Late Current追加0／Stopを確認
```

Dedicated Smokeの`--phase-6-dedicated-model-authority`は別途Real Artifact Authorityが付与された時だけ使う。Flag単独ではLoadしない。

## 5. Review／Open Gate

Cycle 1でPhase Index stale stateを修正。Cycle 2でManualの109 Count二重加算表現とActive Turn drain待機不足を修正した。Critical／Major／MVP Blocker残存0。

```text
Real Selene: RESOURCE_GATED / NOT RUN
Real Qwen3Guard: RESOURCE_GATED / NOT RUN
Real Browser / User Screen: USER MANUAL GATE / NOT RUN
Network / Root outside / runtime_data / Git: Action 0
```

## 6. Exact Next Action／Stop

Controller Independent Reviewを開始する。受理後にUser Mac Manual／Real Artifact Dispositionを行う。本Return後、Executorは停止し、追加Rework、Phase 9-2／9-3、Closure、Gitへ進まない。

`P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION`
