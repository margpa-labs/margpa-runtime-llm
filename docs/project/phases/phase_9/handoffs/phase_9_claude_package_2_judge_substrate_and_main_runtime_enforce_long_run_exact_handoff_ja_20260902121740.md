# Phase 9-1 Claude Package 2 Judge Substrate／Semantic／Main Runtime ENFORCE Long-run Exact Handoff

```yaml
document_id: phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_20260902121740
document_type: exact_long_run_handoff
document_state: frozen_waiting_for_package_1_return
language: ja
created_at: 2026-09-02 12:17:40 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
provider: Claude
role: 設計者兼実装者役
claude_weekly_availability_at_planning: 100_percent_user_reported_unexpected_reset
codex_weekly_availability_at_planning: 13_percent_user_reported_preserve_for_emergency
task_continuity: continued_after_package_1_or_fresh_with_exact_return
entry_condition: package_1_exact_return_and_artifact_acquisition_complete
implementation_authority: true
real_local_model_load_authority: true
network_authority: false
project_root_external_artifact_authority: read_existing_configured_models_only
runtime_data_authority: test_fixture_only
browser_authority: false
git_authority: false
backup_authority: false
phase_9_closure_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Entry／Objective

Package 1で取得した軽量独立Judgeを入力に、次を一つのLong-runとして順序通り成立させる。

1. Built-in／Main-shared Qwen／Selene／軽量Judgeを同一条件で比較する。
2. 共通Judge基盤を先に診断・修復する。
3. 残るProvider固有問題を修復する。
4. Judge OBSERVE／ENFORCEを成立させる。
5. Judge→Repair→Rejudgeを成立させる。
6. Semantic 109の実評価を成立させる。
7. 最後にARGD／DAGDを含むMain Runtime Governance ENFORCEを成立させる。

Package 1とPackage 2は最初から一つのUser-approved Sequenceである。Package 2はPhase 9-1のCurrent Critical Pathであり、Phase 9-2へ進まない。

UserはCodex週間利用可能量を残13%と報告している。Package 2中のRoutine Controller Reviewは要求せず、ClaudeがLong-runと二段階Internal Reviewを完遂してExact Returnする。Codex ReviewがQuota回復まで遅れても、ClaudeはFinal Acceptance／Closure Authorityを取得しない。

## 2. Preserved Current State

開始時点の正直なBaselineは次である。

```text
Main-shared Qwen : malformed_output／evaluated 0
Built-in         : completedだがevaluated 0／not_applicable 32／deferred 77
Selene           : active表示後unavailable／evaluated 0／高負荷
Qwen3Guard       : Guard OBSERVE／ENFORCE／OFFの基本Baselineは成立済み
Root Cause       : Common Judge Substrate First Hypothesis／未確定
Canonical Tests  : 2214 passed／2 failed／7 deselected
Mypy             : 45 errors
Ruff             : pass
Phase 9-1        : FAIL／REWORK REQUIRED／NOT CLOSED
```

Qwen3GuardのBaselineをJudgeまたはMain Runtime Governance ENFORCE成立へ読み替えない。軽量Judgeが成功してもSelene／Main-sharedの既知Failureを自動解決扱いにしない。

## 3. Minimum Reading／Context Reuse

開始前に読むのは次に限定する。

1. 本Exact Handoff。
2. Package 1 Exact Return。
3. `docs/project/phases/phase_9/phase_index_ja.md`のCurrent State／Next Authorized Sequence。
4. `docs/project/phases/phase_9/history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md`。
5. Phase 9 Current Acceptance MatrixのP9-1該当行だけ。

Recent Verified ContextはTask Identity、AuthorityおよびCanonical Stateが変わらない限り再利用する。旧Handoffや全Historyを毎Work Unitで読み直さない。Canonicalityは毎Turn再読を意味しない。

## 4. Package Execution

### P2-WU-01 — Recovery／Four-provider Matrix Freeze

Package 1 Return、Working Tree、既知2 Test Failure、45 Mypy Errorおよび4 Providerの現状を一つのRecoveryへ固定する。

同一の短いFixture入力、同一Semantic Snapshot、同一Criterion Set、同一Mode、同一Budget記録形式で次を比較する。

- Built-in Deterministic。
- Main-shared Qwen。
- Selene。
- Package 1の軽量独立Judge。

Built-inへ未実装のQualitative能力を捏造しない。対応可能範囲、`not_applicable`、`deferred`および能力限界を正直に比較する。

### P2-WU-02 — Common Judge Substrate Diagnosis／Repair

Provider別Patchへ入る前に、次の共有経路を横断Probeする。

- Criterion Selection／Semantic Snapshot。
- Prompt Build／Token Budget。
- Inference Request／Response。
- Strict Decode／Typed Failure。
- Result Projection／Recording Correlation。
- Role Load／Lease／Unload。
- Mode Transition／Cancellation／Whole-stage Deadline。

共通Failureは共通層で一度だけ直す。Provider固有Adapterへ同じWorkaroundを複製しない。

### P2-WU-03 — Provider-specific Repair

共有層修復後に残る差分だけを個別修復する。

- Main-shared Qwen: Structured Output安定性、Model Identity維持、Selene切替後のMain Load破壊防止。
- Selene: 実Load／Inference／Strict Decode／Unload、重さと不具合の分離、Bounded Budget。
- 軽量Judge: Registry／Prompt／Decode／Lifecycle統合。
- Built-in: 対応可能Criterionの決定論的処理と、非対応Criterionの正直なDisposition。

### P2-WU-04 — OBSERVE／ENFORCE

各ProviderのCapability範囲に応じて、OBSERVEではCandidateを提示しつつTyped Evidenceを記録し、ENFORCEでは確定不能時のSafe Fallbackと確定時のActionを正しく分離する。

Configured／Active／Executed Provider、Request ID、Criterion Count、Verdict、Failure Code、Presentation、BudgetをLosslessに相関させる。

### P2-WU-05 — Judge→Repair→Rejudge

同一Request ChainでJudge、Repair Candidate、Rejudge、Adopt／Reject／Safe Fallbackを成立させる。Frozen Provider Identity、Maximum Repair Count、Whole-stage DeadlineおよびCancellationを維持し、別RunのEvidenceを混入させない。

### P2-WU-06 — Semantic 109 Live Evaluation

LLM Judge経路でSemantic 109の実評価をBudget内に成立させる。`evaluated = passed + deviated`とOutcome総和109を満たし、常時`Deferred 109／evaluated 0`へ戻らない。

一つのRunで全109を無理に投入してContext／Deadlineを破壊しない。Batching、Token Accounting、Deferred ReasonおよびFinal Aggregationを正直に設計する。

### P2-WU-07 — Main Runtime Governance ENFORCE

Judge基盤成立後にだけ進む。ARGD／DAGDを最低必須として、Main Runtime Governance ENFORCEが実際に許可されたActionを適用し、Authorityを拡張せず、Unsupported／Conflict／Failure時にFail ClosedするGolden Pathを成立させる。

単なる`mode=enforce`表示、Observation記録またはQwen3Guard Actionを、MARGPA Main Runtime Governance ENFORCE成立と主張しない。

### P2-WU-08 — Verification／Two-stage Internal Review／Return

Focused Testから開始し、Canonical Backend Test、Mypy、Ruffを実行する。Frontendを変更した場合だけFrontend Test／Typecheck／Lint／Buildも実行する。

内部Reviewは全く異なる観点で二段階行う。

1. Runtime／Concurrency／Lifecycle／Cancellation／Authority観点。
2. Requirement／Semantic／Evidence／Manual Truthfulness／Claim観点。

Critical／Major／MVP Blockerは同一Task内で修正し、該当Reviewを再実施する。Minor／Hardeningは未解決へ分類して続行する。

## 5. Manual／Observability Truthfulness

User Manual Sheetには、現UIで実際に見える項目だけを書く。Model Call 0、Worker Drain、Strict Decoder内部、Artifact Digest、Late Publish 0などUIに存在しない内部項目を「画面で確認」と指示しない。

内部保証はBackend Test、Structured Logまたは専用Evidenceで証明し、将来Observability UI候補と区別する。

## 6. Continuation／Stop Contract

次は停止理由ではない。

- Core PipelineのLarge DiffまたはBlast Radius。
- Independent Review前であること。
- Minor Finding、Routine Progress、Test Failure、Reworkまたは実装難度。
- Seleneが重い、または一つのProviderが失敗したこと。

RiskはFocused Test、Recovery、Rollback可能な小差分および二段階Reviewで管理し、True StopがなければP2-WU-08まで連結実行する。

True Stopは次に限定する。

- Authorized Root外Write、Credential、Paymentまたは新しい外部Authorityが不可欠。
- Canonical Working Stateが復旧不能に競合。
- Artifact破損、License不明または安全に解決できないModel Root問題。
- Irrecoverable destructive risk。
- Provider Resource Hard Stop。
- 最終User実画面Gate。

Resource Hard Stop時はCurrent WUを安全に収束し、Completed／Partial／Invalid、変更Path、Test、Active Process、Exact Next ActionをRecoveryへ直列化する。Worker FailureをJob Failureへ拡張しない。

## 7. Authority／Prohibitions

許可する。

- Current Source／Test／Frontend／DocsのPackage 2必須変更。
- 既存構成済みLocal Model ArtifactのRead／Load／Inference／Unload。
- Test Fixture用一時領域。
- Focused／Canonical Verification。

禁止する。

- 新しいNetwork Download、Dependency Install、Credentialまたは課金。
- User `runtime_data`、実Conversation／Local CorpusのMutation。
- Artifact削除／上書き。
- Git Stage／Commit／Push、Backup、Phase 9 Closure、Phase 9-2／9-3開始。
- Provider Memoryを正本にすること。
- Final AcceptanceまたはUser Manual PASSの自己認定。

## 8. Return Contract

Returnには最低限次を含める。

- WU別Disposition。
- 4 Provider Matrix Before／After。
- 共通Root CauseとProvider固有Root Causeの分離。
- Judge OBSERVE／ENFORCE Evidence。
- Judge→Repair→Rejudge Evidence。
- Semantic 109 Outcome Accounting。
- ARGD／DAGDを含むMain Runtime Governance ENFORCE Evidence。
- Verification、二段階Review、Open Finding、User Manual項目。
- Source／Test／Docs変更、Active Process／Artifact Inventory。
- Recovery IndexとExact Return Handoff。

最大Claimは`P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`である。Phase 9-1 Closure、User Final AcceptanceまたはPhase 9-2 Readyを主張しない。

## 9. User Scope Correction — Default JudgeのGemma化

Package 2実行中の2026-09-02に、Userが次を追加で確定した。

- `Gemma 4 E2B`は比較候補へ追加するだけでなく、Fresh Runtimeの規定Judge Providerとする。
- 現行Sourceは`ProviderSelectionController`のJudge既定値が`SELENE_JUDGE`のままであり、Gemmaは選択可能な追加Candidateにとどまっている。これはPackage 2完了条件を満たさない。
- Fresh Runtimeの`configured_provider`を`GEMMA_E2B_JUDGE`へ変更する。ただしMode OFF時は`active_provider=None`のままとし、起動時の暗黙Loadは行わない。
- Seleneは廃止せず、明示選択可能な比較・後方互換Providerとして残す。
- 既存Runtime中のUser選択を強制上書きせず、Fresh Controllerの規定値として変更する。
- Default Contract Test、Provider Selection表示、Mode ONでのLoad、OFFでのUnload、Judge→Repair→Rejudge IdentityをGemma規定で再検証する。

本追記はP2-WU-08 Exact Return前に実装・Test・二段階Internal Reviewの対象とする。
