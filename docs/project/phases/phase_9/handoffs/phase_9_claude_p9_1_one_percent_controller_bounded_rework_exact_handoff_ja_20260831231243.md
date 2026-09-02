# Phase 9-1 Claude One-percent Controller Bounded Rework Exact Handoff

```yaml
document_id: phase_9_claude_p9_1_one_percent_controller_bounded_rework_exact_handoff_20260831231243
document_type: exact_continuation_rework_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-08-31 23:12:43 JST
phase: phase_9
program: phase_9_1
provider: Claude
role: 設計者兼実装者役
task_continuity: continued_not_fresh
available_weekly_resource_at_handoff: approximately_1_percent_user_reported
implementation_authority: true_after_exact_user_start
real_artifact_authority: false
real_model_authority: false
network_authority: false
git_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

## 1. Objective

P9-1-0〜Dの成立済み差分をRollbackせず、Codex Controller Reviewで検出したP9-CODEX-001〜004だけを修正する。Phase 9-1全体を再監査・再実装しない。

Claude利用可能量はUser報告で約1%である。予測残量を理由に開始前停止せず、実際のResource Hard Stopまで順番どおり進める。Hard Stop時はCurrent WUをExact Recoveryへ直列化し、Codex設計者兼実装者役Taskが同じWorking Treeから継続できるようにする。

## 2. Continuity／Reading

Current Claude Taskを継続する。Fresh Task化、Role Bootstrap、Mandatory Readingの全再実行、長いReceiptを行わない。

読む文書は次の2件だけでよい。

1. 本Exact Handoff。
2. `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md`

必要なSource／TestはFinding記載Pathと隣接Compositionだけを読む。Phase 6〜8 HistoryまたはP9-1全Recoveryを再走査しない。

## 3. Preserved State

- Claude追加のDedicated Preflight共通化と9 Test。
- Canonical Semantic 109 Compile／Built-in NOT_APPLICABLEの正しい設計。
- Main-shared Judge Dispatch／Strict Decode／Semantic Result記録。
- 2200 Backend PASSというClaude実測と、Controller Focused 48 PASS。
- Real Artifact／Network／Git／User runtime_data Action 0。

これらを再実行目的で作り直さない。

## 4. Exact Rework Order

### P9-CODEX-001 — Production Authority Opt-in

Default Falseの明示的Startup Authority Flagまたは同等の安定したConfiguration Contractを追加する。

```text
Web CLI
-> build_phase1_web_runtime()
-> ProductionRoleAdapterFactory(dedicated_model_authority_granted=...)
```

必須条件：

- DefaultはFalseで既存挙動を保持。
- Userが明示Opt-inした時だけTrue。
- Opt-inだけでDedicated ModelをStartup Loadしない。
- Mode OFF中はArtifact Touch／Load／Inference 0。
- Mode Transition時だけ既存Preflight／Candidate Load／Atomic Commitへ進む。
- CLI HelpとReturn Manualに正確な起動Optionを書く。
- TestはFixture／Monkeypatchだけを使用し、Real Artifactへ触れない。

Flag名は既存CLI命名と整合するStable名を選べるが、曖昧なEnvironment暗黙許可にはしない。

### P9-CODEX-002 — Actual Repair／Rejudge Composition Test

Main-shared Judge HookへProductionと同じRepair実装を接続し、Fixture ServiceのCall列として次を実行するTestを追加する。

```text
Initial Main-shared Judge: needs_repair
-> Repair Candidate Generation
-> Main-shared Rejudge Model Call
-> accept／reject
-> Final Disposition／Identity／Call Count
```

Fake Repair Executorが即`accepted=True`を返すだけのTestをE2E証明に使わない。既存Testは削除せず、役割を「Parameter／Frozen Identity Wiring Test」と正確に扱ってよい。

### P9-CODEX-003 — State／38 Acceptance

- Phase 9 IndexをCurrent Rework／Candidate Stateへ更新。
- P9-ACC-001〜038を個別Disposition＋Evidence Pointer付きで再導出。
- Real Artifact関連は`RESOURCE_GATED／NOT RUN`、User実画面は`USER MANUAL GATE`とし、PASSへ捏造しない。
- 旧Returnを履歴として残し、新しいExact Return Handoffを作る。

### P9-CODEX-004 — Correct User Manual Order

少なくとも次を順序付きで記載する。

1. Current Mainと一致するMain-shared Judge Providerを選択。
2. Provider変更でOFFへ戻ったJudge ModeをOBSERVEまたはENFORCEへ再適用。
3. Repair確認時だけRepair ENFORCE、必要に応じRecording FULL。
4. Turn実行後、Selected／Evaluated／Deferred、Configured／Active／Executed、Judge／Repair／Rejudge Identityを確認。
5. Dedicated SmokeはUserがReal Artifact Authorityを別途付与した時だけ、新Startup Opt-in付きで実施。

## 5. Verification

最初にFinding直結Focused Testを実行する。Resourceが残る場合だけCanonical Backend、Mypy、Ruffを実行する。Frontend SourceまたはCLI表示だけの変更なら比例検証する。

Resource節約のため、既にPASSした無関係Package TestをPackageごとに重複実行しない。

## 6. Authority／Prohibitions

Allowed：Project Root内Source／Test／Docs／Recovery／Return、既存dependencyによるTest。

Forbidden：Project Root外Artifact Read／Stat／Digest／Load、Real Model、Network、Install、Browser、Git、Backup、User runtime_data、Phase 9-2／9-3、Roadmap、Closure。

Startup Opt-inの実装はReal Model実行Authorityではない。TestでOpt-inをTrueにしてもFixture Boundaryから外へ出ない。

## 7. Resource Hard Stop Return

実際に利用可能量が尽きる場合は、停止前に次をCompact Recoveryへ残す。

- P9-CODEX-001〜004のFixed／Partial／Not Started。
- Changed Paths。
- Test結果。
- Current Source failure／syntax状態。
- Exact Next Action。
- Real Artifact／Network／Git Action 0の確認。

Rollback、Fresh Bootstrap、成立済みWork Unit再実行はしない。

## 8. Stop Line／Return

大きなDiff、残1%、Independent Review前、不確実性、Minor Findingを理由に自主停止しない。P9-CODEX-001〜004以外のP1以下を追加Reworkしない。

4件完了後は新しいExact Return Handoffを作り、`P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION`としてCodex Controller Review待ちで停止する。Phase 9-2へ入らない。

## 9. Exact Start

```text
Current Claude Taskを継続し、P9-CODEX-001から直ちにBounded Reworkを開始する。
```
