# Phase 6 Claude Current Task R17〜R20 Exact Rework Handoff

```yaml
document_id: phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_20260829032604
document_type: differential_exact_rework_handoff
document_state: ready_for_single_step_start
language: ja
created_at: 2026-08-29 03:26:04 JST
authority_owner: Codex_プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
target_task: current_existing_claude_task
preserved_baseline: current_working_tree_after_r0_to_r16
first_exact_work_unit: P6-RR-R17-WU-001
remaining_packages: P6-RR-R17_to_R20
maximum_claim: complete_candidate_with_real_provider_and_user_manual_gates
phase_6_closure: prohibited
phase_7: prohibited
git_action: prohibited
network: prohibited
```

## 1. Authority／Continuation

現在のClaudeタスクをそのまま継続する。Fresh Taskではない。Role／Authority Bootstrap、旧Context初期化、全Docs再読、Receipt専用段階は不要である。

R0〜R16の成立済み差分を保持し、Rollbackまたは一括再実装しない。Current Source／Testを正本として、P6-CODEX-080〜085だけを差分修正する。

## 2. Required Reading

開始時に次の3文書だけを読む。

1. 本書。
2. `docs/project/phases/phase_6/history/operations/phase_6_gov022_claude_r13_to_r16_controller_independent_review_ja_20260829032604.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r13_to_r16_exact_return_handoff_ja_20260828233354.md`

必要なSource／Testは各Package到達時に限定して読む。Workspace全走査や過去文書の全再読は不要である。

## 3. Exact Packages

### P6-RR-R17 — Composite Transition／Status Snapshot

1. Judge／Guardそれぞれについて、Mode、Configured、Active、Runtime State、Failure、Lifecycleを同一Transition Lock内で読むComposite Snapshot APIを作る。
2. Provider Selection GET、Feature Modes GET、Mode Apply Response、Provider Apply Responseが同じComposite Boundaryを使用する。
3. ON方向のProvider ACTIVE→Mode Commit間、OFF方向のMode Commit→Provider Deactivate間でConcurrent Readerを実際に走らせ、ReaderがTransaction完了まで待つか、完全な旧Tupleだけを返すことをTestする。
4. Mutation POST ResponseもLock解放後の個別再読で混合Tupleを作らない。
5. Judge／Guard双方、Mode OBSERVE／ENFORCE双方、Mode OFF、Mode Commit Failure、Unload Failure、Active Turn Drainを含める。
6. P6-CODEX-080を閉じる。

### P6-RR-R18 — Full Stage Deadline／AUTO Language

1. Prompt BuildとDecodeをTracked Stage Workerまたは同等のTerminal-owner境界へ移し、自身のDeadline超過時にCallerをBoundする。
2. Timeout後のPrompt／Decoded Result、Judge Result、Evidence、Presented Final、Last ResultへのLate Publishを拒否する。
3. Cancellation無視Workerも実完了まで追跡し、Shutdown／JoinのFalse-cleanを作らない。
4. 既存Judge Inference／Repair Generation／Rejudge Deadlineを保持し、Stage間の余剰Budget流用を許さない。
5. `ResponseLanguage.AUTO`を英語へ固定変換しない。Turn開始時に最新User Input等から実効`ja`／`en`を決定論的に解決し、Judge／Repair／Rejudge／全Failure Presentationへ同一値を継承する。
6. 明示JA、明示EN、AUTO＋日本語、AUTO＋英語、Main Governance OFFをTestする。
7. P6-CODEX-081／083を閉じる。

### P6-RR-R19 — Shared Request Correlation Registry

1. Judge CompositionやRecording Last Outcomeではなく、Conversation Turn開始時にbase `request_id`を登録する共有Correlation Registryを作る。
2. Current／Pending／Completed／Cancelled／Failedを同じRequest IDで管理する。
3. Turn Metadata、Judge Result、Final Disposition、Failure、Configured／Active／Executed Provider、Budget、Frozen Modes、開始／完了時刻、Turn Recording、Judge Evidence RecordingをServer-side単一SummaryへJoinする。
4. Judge OFF＋Recording FULL／METADATA、Judge OBSERVE Background Pending、Judge ENFORCE、Recording OFF、途中Mode変更、別RequestのOut-of-order CompletionをTestする。
5. UIはServer Summaryを正本として表示し、設定初回Openで一つ前の結果をCurrent扱いしない。2秒Poll、再Open、Unmount Cleanupを維持する。
6. P6-CODEX-082を閉じる。

### P6-RR-R20 — Contract-complete QA／Claim Audit／Return

1. S4をGuard OBSERVEの字義どおり追加Testする。
2. S9をFake Selene AdapterでInitial Judge→Repair→Frozen Selene Rejudgeまで単一Turn E2E Testする。
3. S12／S13をLive Hook上のMalformed／Timeout／UnavailableについてJA／EN双方Testする。AUTO日本語／英語も含める。
4. S1〜S17をExact Test Path／Test Name／Result付きで再導出し、未成立は`PARTIAL`または`NOT RUN`とする。
5. Remaining Rework `P6-RR-ACC-001〜040`とDelta `P6-DELTA-001〜026`の全66 IDを一件ずつ再導出し、DispositionとEvidence Pointerを記載する。一括`Regression 0`で代替しない。別SetのPhase-wide `P6-ACC-001〜084`を代用しない。
6. `ruff format --check src tests`をCanonical PASSにする。必要なら現時点の17対象をFormatting-onlyで整形し、Semantic変更と混同せずInventoryへ記録する。
7. Focused Backend／Frontend、Canonical Mypy／Ruff Check／Ruff Format Check／Backend Full／Frontend Typecheck・Lint・Test・Buildを実行する。
8. Changed File Full Path／SHA-512、Finding Ledger、Internal Review Cycle 1→必要Rework→Cycle 2、Final Recovery、Exact Return Handoffを作る。
9. P6-CODEX-084／085を閉じる。

## 4. Required Regression Scenarios

```text
R17-A: ON Transaction中のProvider GET
R17-B: ON Transaction中のFeature Modes GET
R17-C: OFF Transaction中の両GET
R17-D: Mode／Unload Failure時のHonest Tuple
R18-A: Prompt Build Deadline＋Late Publish 0
R18-B: Decode Deadline＋Late Publish 0
R18-C: AUTO日本語／AUTO英語 Failure Presentation
R19-A: Judge OFF＋Recording FULLのCurrent Turn
R19-B: OBSERVE Pending中のCurrent Request
R19-C: Completed TurnのJudge／Recording Single Join
R19-D: Out-of-order旧RequestのHistorical分離
R20-A: S4 OBSERVE exact
R20-B: S9 Frozen Selene Rejudge E2E
R20-C: S12／S13 Live timeout／unavailable JA／EN
```

## 5. Execution／Recovery

- Package R17、R18、R19、R20の各BoundaryでRecovery Indexを1件作る。
- Work Unitごとの文書作成は不要である。
- 軽微な非破壊Incidentや自己修正可能なTest／Command Errorだけで停止しない。Recoveryへ記録して継続する。
- Gitは使用しない。誤ったRead-only Git実行だけで全体停止せず、記録して継続する。Git Mutation、Project外Persistent Mutation、Secret／Privacy接触、不可逆破壊は停止対象である。
- Network、Real Model、User `runtime_data`は使用しない。Real Selene／Qwen3Guard／Browser項目は正確に`NOT RUN／USER GATE`としてよく、それだけで全体停止しない。
- 不要な進捗確認待ちを挟まず、True Stop ConditionがなければR17からR20まで連結実行する。

## 6. Return Contract

最大Claimは`Complete Candidate with Real Provider and User Manual Gates`である。

Returnには最低限、次を含める。

- P6-CODEX-080〜085の個別Disposition。
- R17〜R20 Recovery Index。
- Required Regression ScenariosのTest Path／Name／Result。
- S1〜S17 Matrix。
- 66 Acceptance IDの個別Disposition。
- Focused／Canonical Command、Exit Code、Exact Count。
- Format Check PASS。
- Changed File Full Path／SHA-512。
- Open Critical／Major／Minor／User Gate。
- Action Inventory。

Phase 6 Closure、Git、Backup、Roadmap、Phase 7へ進まない。Return後はCodex Independent Review待ちで停止する。
