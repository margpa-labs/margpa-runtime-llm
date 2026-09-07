# Phase 9-1 Claude Package 3 Context 16K／Output 4K・8K Expansion Exact Handoff

```yaml
document_id: phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_handoff_20260902150815
document_type: exact_bounded_implementation_handoff
document_state: frozen_waiting_for_package_2_planner_proof_and_user_manual_recheck
language: ja
created_at: 2026-09-02 15:08:15 JST
phase: phase_9
program: phase_9_1
package: P9-1-CONTEXT-PACKAGE-3
provider: Claude
role: 設計者兼実装者役
entry_condition: package_2_exact_return_planner_proof_pass_and_user_manual_recheck_complete
implementation_authority: true_after_entry_condition
real_main_model_load_authority: true
real_gemma_judge_load_authority: true
real_selene_load_authority: false
real_guard_load_authority: false
network_authority: false
artifact_mutation_authority: false
runtime_data_authority: test_fixture_only
browser_authority: false
git_authority: false
backup_authority: false
phase_9_closure_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_CONTEXT_16K_OUTPUT_4K_8K_HARDWARE_VERIFIED_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Objective

Package 2でJudge内部Token Plannerの修復とRegression Evidenceを成立させた後、Local Mac Deploymentの通常ContextとOutput Budgetを次へ拡張する。

```text
Current Context Size        : 16384
Effective Context Maximum   : 16384
Current max_new_tokens      : 4096
Maximum max_new_tokens      : 8192
```

本Packageは内部Judge Plannerの代替修正ではない。Planner未成立のままContextだけを増やさない。

## 2. Mandatory Entry Audit

開始時、Package 2 Exact Returnおよびその後のUser Manual結果から次を確認する。

1. Planner無効時のTruncation／`malformed_output`再現Testがある。
2. Planner有効時に`prompt + reserved output <= effective context`をAssertしている。
3. Criterion欠落／重複0、Identity Drift 0をAssertしている。
4. Sabotage時Failure／復元後PASSが記録されている。
5. Focused Commandを再実行してPASSする。
6. UserがPackage 2後の実画面でJudge OBSERVE／ENFORCE、Judge→Repair→Rejudge、Semantic 109およびARGD／DAGDを含むMain Runtime Governance ENFORCEを再確認している。
7. UserがPackage 3開始を明示している。
8. Active Model／Worker／Temporary Artifactが残っていない。

一つでも欠ける場合はContext実装へ進まない。Planner Evidence不足はPackage 2の同一Task Reworkへ戻し、User Manual未完了時はその結果を待つ。これはRoutine User Confirmation Gateではなく、Userが明示したPackage間Gateである。

## 3. Minimum Reading

読むのは次に限定する。

1. 本Exact Handoff。
2. Package 2 Exact ReturnとPlanner専用Evidence節。
3. `docs/project/phases/phase_9/history/operations/phase_9_1_judge_token_budget_planner_proof_context_16k_decision_and_deferred_role_split_ja_20260902150815.md`。
4. Context／Output Limitに直接関係するCurrent Config／Domain／Controller／UI Test。

旧Phase History、全Handoffまたは全Docsを再読しない。Recent Verified Contextを再利用する。

## 4. Frozen Scope

### P3-WU-01 — Config Contract

- Local macOS Deployment Contextを16384へ変更する。
- Default／Current `max_new_tokens`を4096へ変更する。
- Profile由来のMaximum `max_new_tokens` 8192を導入する。
- `-1` SentinelまたはUnlimited生成を導入しない。
- Config未指定時の既存Portable DefaultとMigration／Backward Compatibilityを明示する。

Maximum 8192はSource内Literalの散在ではなく、Config→Resolver→Capability／SnapshotへLosslessに流す。

### P3-WU-02 — Runtime Model Control

Runtime Snapshot／Capability／Controllerが次を正確に保持する。

```text
loaded_context_size              = 16384
deployment_verified_context_limit= 16384
effective_context_limit          = 16384
current_max_new_tokens           = 4096
max_output_token_limit           = 8192
```

- 8192は受理する。
- 8193はTyped Validation Failureで拒否する。
- Context変更／Model Switch／Rollback／Restart後もOutput Ceilingを失わない。
- Stale CAS、Failed LoadまたはRollbackで半端なSnapshotをCommitしない。

### P3-WU-03 — Conversation／UI Truthfulness

- 通常TurnがDefault 4096を使用する。
- Prompt TokenとRequested Outputの合計が16Kを超える場合は既存のTyped Context Failureへ収束する。
- UIへCurrent Context 16384／Effective Maximum 16384／Current Output 4096／Maximum Output 8192を正確に表示する。
- 入力ControlのMax値とBackend上限を一致させる。
- Judge内部PlannerのProvider別Output値をGlobal 4096へ勝手に置換しない。

### P3-WU-04 — Automated Verification

最低限次をTestする。

- Config Parse／Effective Profile。
- Runtime Snapshot／Digest／Switch／Rollback。
- 4096 Default、8192 Boundary、8193 Rejection。
- Context 16384 Load Contract。
- Conversation Token Accounting。
- UI Display／Input Boundary。
- 既存8K Fixtureの互換性。

Focused Test後、Full Backend、Mypy、Ruffを実行する。Frontend変更時はFrontend Test／Typecheck／Lint／Buildも実行する。

### P3-WU-05 — Main 16K Real Smoke

Clean Restart起点でMain Qwenを16K Loadし、短い通常TurnとContext Budget境界Testを実行する。

記録する。

- Load成功／Context値／Output値。
- Model Identity。
- Memory Pressure Before／After。
- Latency／Failure Code。
- Unload／Restart Recovery。
- OOM、Unhandled Exception、`model_not_loaded`再発の有無。

### P3-WU-06 — Main＋Gemma Real Smoke

Main 16KとGemma Judge 16Kの実経路をLoad／Inference／Decode／Unloadまで実行する。Semantic長時間Runではなく、16GB環境での共存可能性を確認するBounded Smokeとする。

Qwen3GuardおよびSeleneを同時Loadしない。Selene 16Kを試さない。

Main＋GemmaがMemory Pressure、Swap Thrash、Deadline常態化またはLifecycle破壊へ至る場合、16K Hardware Verifiedを主張せず、差分を安全に8Kへ戻して`HARDWARE_NOT_VERIFIED`として返す。原因をRole別Context分離の即時実装へ勝手にScope拡張しない。

### P3-WU-07 — Manual Backoff／Recovery／Review

Selene使用時の正本手順を残す。

```text
local_macos_arm64 context_sizeを8192へ戻す
Server Restart
Runtime表示が8192／8192へ戻ったことを確認
SeleneをLoad
```

Role別Context分離はFuture Reservationのまま維持する。

Internal Reviewは二段階行う。

1. Config／Capability／Atomicity／Rollback／Resource観点。
2. UI Truthfulness／Manual／Portability／Claim観点。

Critical／Major／MVP Blockerは同一Task内で修正し、再Reviewする。

## 5. Authority／Prohibitions

許可する。

- Config、Source、Test、Frontend、Docsの本Package必須変更。
- 既存Main Qwen／Gemma ArtifactのRead、Load、Inference、Unload。
- Local Test FixtureとRead-only System Memory観測。

禁止する。

- 新規Model Download、Network、Dependency Install。
- Artifact変更／削除、Selene／Guardの16K実Load。
- Role別Context Configの実装。
- User `runtime_data`、実Conversation Store、Local CorpusのMutation。
- Git、Backup、Phase Closure、Phase 9-2／9-3開始。
- Planner Testを削除・弱化して16Kを通すこと。

## 6. Continuation／True Stop

Routine Progress、Test Failure、Minor Finding、Large Diff、Pending ReviewまたはMemory調整の必要性では停止しない。Recovery、Focused TestおよびRollbackで管理する。

True Stopは次に限定する。

- Planner ProofがPackage 2 Reworkでも成立しない。
- Authorized Root外Write、Credential、Paymentまたは新Authorityが不可欠。
- Canonical Stateが復旧不能に競合。
- OOM／Process Killが反復し、安全な8K Rollbackも確認できない。
- Provider Resource Hard Stop。

## 7. Return Contract

Returnには次を含める。

- Planner Entry Audit結果とFocused Command。
- Config／Snapshot Before／After。
- 16384／16384、4096／8192のTest Evidence。
- Main単体およびMain＋Gemma Smoke。
- Memory／Latency／Lifecycle Evidence。
- Selene 8K Backoff手順。
- Full Verification、二段階Review、Open Finding。
- Active Process／Artifact／Temporary File Inventory。
- Recovery IndexとExact Return Handoff。

最大Claimは`P9_1_CONTEXT_16K_OUTPUT_4K_8K_HARDWARE_VERIFIED_CANDIDATE_FOR_CONTROLLER_REVIEW`である。Main＋Gemma Smoke失敗時はこのClaimを使わず、正直なPartial／Hardware Not Verifiedとして返す。Phase 9-1 ClosureまたはUser Final Acceptanceを主張しない。
