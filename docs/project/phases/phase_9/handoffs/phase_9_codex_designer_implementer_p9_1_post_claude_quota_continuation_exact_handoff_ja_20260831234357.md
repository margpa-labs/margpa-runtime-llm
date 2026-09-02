---
title: Phase 9-1 Post-Claude Quota Codex Designer Implementer Exact Continuation Handoff
document_state: frozen_ready
language: ja
created_at: 2026-08-31T23:43:57+09:00
phase: 9-1
provider: Codex
role: designer_implementer
task_state: continued_from_current_working_tree
controller_thread_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
executor_thread_id: 01a03b6c-2a68-7881-99bc-c788a600f632
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
---

# Phase 9-1 Post-Claude Quota Codex設計者兼実装者役 Exact Continuation Handoff

## 1. 目的

Claudeの週間利用可能量枯渇によって中断したPhase 9-1 Controller Bounded Reworkを、Current Working TreeからRollbackせずに継続する。

Phase 9-1全体を再実装・再監査しない。成立候補であるP9-CODEX-001／002を保持し、P9-CODEX-003／004だけを完了させ、差分ReviewとExact Returnを行う。

## 2. Resource境界

User観測値：

- Codex 5時間利用可能量：67%残。
- Codex週間利用可能量：63%残。
- 週間利用可能量50〜55%付近を停止帯とする。

Task自身はMeterを推測しない。User／Controllerから停止帯到達通知を受領した場合、新規Work Unitへ入らず、Current Unitを安全に収束し、Exact Recoveryを残して停止する。

## 3. Canonical State

正本は会話Memoryではなく次とする。

1. Current Working Tree。
2. `docs/project/phases/phase_9/handoffs/phase_9_claude_p9_1_one_percent_controller_bounded_rework_exact_handoff_ja_20260831231243.md`
3. `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md`
4. 本Handoff。

旧Phase 6 TaskのContext、Authority、未完了作業は継承しない。新しいBootstrapや全Mandatory Readingの再実行も行わない。

## 4. Preserved Candidate State

### P9-CODEX-001 — Production Authority Opt-in

Source／Test差分は成立候補として保持する。

- `--phase-6-dedicated-model-authority`を明示Opt-inとして追加。
- 既定値False。
- Local Exposure／Loopback Host限定。
- FlagだけではModel Loadを開始しない。
- Mode切替時に既存Preflight／Load経路を通る。

### P9-CODEX-002 — Actual Repair／Rejudge Composition

Source／Test差分は成立候補として保持する。

- Production Repair Compositionへ実接続したTestを追加。
- `:judge` → `:repair` → `:rejudge`の実Callを検証。
- 同一Main-shared Model Identity／Lease再利用を検証。
- 一時Sabotageは復元済みで、`repair_live_integration.py`に差分は残っていない。

Controller独立確認：

- Focused Test：62 passed。
- 対象Mypy：clean。
- Ruff check／format：clean。
- `git diff --check`：clean。

成立候補を理由なく再実装・Rollbackしない。P9-CODEX-003／004作業で関連Failureが出た場合だけ、最小差分で戻る。

## 5. Exact Remaining Work

### P9-CODEX-003 — State／38 Acceptance

1. `P9-ACC-001`〜`P9-ACC-038`を一件ずつ、PASS／PARTIAL／FAIL／NOT RUN／USER MANUAL GATE等へ再導出する。
2. 各IDに個別Evidence Pointerと短い根拠を付ける。
3. 合計38件を機械的に検算する。
4. Real Selene／Qwen3Guard Artifact、Real Browser、User実画面等の未成立項目をPASSへ捏造しない。
5. Phase IndexはRework中のCurrent Stateを保持し、Return成立時にだけ正確なCandidate Stateへ更新する。

### P9-CODEX-004 — Correct User Manual Order

User Manual／Recheck Sheetへ、少なくとも次の順序を明示する。

1. Judge Modeを一度OFFへ戻す。
2. Judge ProviderをMain-shared self-judgeまたは検証対象Providerへ切り替える。
3. ProviderのConfigured／Active／Stateを確認する。
4. Judge ModeをOBSERVEまたはENFORCEへ再度有効化する。
5. 新しいTurnを送信し、Semantic 109のselected／evaluated／deferred、Executed Provider、Repair／Rejudge、Evidenceを確認する。

既存TurnのBuilt-in結果をProvider切替後の新結果と誤認させない。

## 6. Review／Validation

P9-CODEX-003／004完了後、観点を変更した二段階の自己Reviewを行う。

- Cycle 1：Requirement／Acceptance／Evidence Pointer／Count／State Truthfulness。
- Cycle 2：Negative Path／未実行Gate／過大Claim／操作順／Provider相関。

Critical／Major／MVP Blockerは同一Task内でReworkする。Minor／Hardening／将来改善は未解決へ送り、Phase 9-1を製品品質まで膨張させない。

検証は差分比例とする。既にControllerが確認したFocused Testを、Docsだけの残作業を理由に無意味に反復しない。Sourceへ追加変更が生じた場合のみ、影響範囲に応じてTest／Mypy／Ruffを実行する。

## 7. Prohibited

- Phase 9-2／9-3開始。
- Phase 9 Closure、Git、Commit、Push、Backup、Roadmap変更。
- Real Model Artifact Load、Root外Model探索、Network、Real Browser。
- User `runtime_data`の変更。
- P9-CODEX-001／002の理由なき再実装・Rollback。
- 38 Acceptanceの一括PASS代替。
- Routine Progress、Large Diff、Pending Controller Review、Minor Findingを理由に独自Gateを作って停止すること。

## 8. Return

次を作成する。

1. Post-Claude Quota Continuation Recovery Index。
2. 38 Acceptanceの個別Disposition Addendum／Matrix。
3. Corrected User Manual／Recheck Sheet。
4. Exact Return Handoff。

ReturnにはP9-CODEX-001〜004の最終Disposition、変更Path、Validation、未実施Gate、最大Claim、Exact User Manual項目を明記する。

Return後はController Independent Review待ちで停止する。Phase 9-2へ進まない。

## 9. Exact Start

Current Working Treeをそのまま受け入れ、P9-CODEX-003の38 Acceptance個別再導出から開始する。
