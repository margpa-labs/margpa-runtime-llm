# Phase 9-1 Copilot Three-Review Real Dedicated Completion Exact Handoff

```yaml
document_id: phase_9_copilot_p9_1_three_review_real_dedicated_completion_exact_handoff_20260901034115
document_state: ready_for_execution
language: ja
created_at: 2026-09-01T03:41:15+09:00
phase: phase_9
program: phase_9_1
provider: copilot
role: designer_implementer
task_state: fresh_continuation_from_current_working_tree
prior_copilot_task_identity_inherited: false
prior_copilot_execution_authority_inherited: false
stale_provider_memory_must_be_ignored: true
implementation_authority: true
local_real_artifact_load_inference_unload_authority: true
read_only_official_source_retrieval_if_strictly_required: true
phase_9_1_closure_authority: false
phase_9_2_authority: false
git_authority: false
backup_authority: false
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Mission

Current Working TreeをCanonical Baselineとして受け入れ、三つの完全別観点Controller Independent Reviewで確定したP9-CODEX-006〜010を修正する。その後、Local Mac上の実Selene／実Qwen3Guardについて、Production経路のLoad→Inference→Strict Decode→Evidence→Mode OFF／Stop→Drain→Unloadを成立させ、Phase 9-1をCodex Controller Review用Candidateへ戻す。

P9-CODEX-001〜005の成立済み差分を理由なくRollback／再実装しない。ただし006〜010の修正により直接影響するTest／Docs／Acceptanceは正直に再導出する。

Phase 9-2、Phase 9-3、Closure、Git、Backupへ進まない。

## 1.1 Mandatory Copilot Task Identity Reset

本Taskは、過去のCopilot Phase 8 P8-0／P8-A／CP8-01〜04 Taskの再開ではない。過去Copilot Sessionの会話Context、TODO、Partial Work Unit、Recovery、Provider Memoryおよび「次に行う予定だった作業」は、情報としてもAuthorityとしても継承しない。

```text
Current Task Identity:
  Phase 9-1 Real Dedicated Completion Rework

Exact Start Boundary:
  P9-CODEX-006 / P9-1-RW-A

Explicitly Expired Task Identities:
  Phase 8 P8-0
  Phase 8 P8-A
  CP8-01
  CP8-02
  CP8-03
  CP8-04
  Web Knowledge Direct URL continuation
```

次をMandatory Start Guardとする。

1. 本Handoffを読む前にSource、Test、旧Recoveryを開かない。
2. 最初のTool Callは本HandoffのHash確認だけとする。
3. 本HandoffからCurrent Task Identity、Exact Start Boundary、禁止範囲を一度だけEntry Receiptへ記録する。
4. Entry Receipt後の最初のSource ReadはP9-CODEX-006のSelene Contract経路だけとする。
5. `web_knowledge_service.py`、Phase 8 Web Knowledge Tests、CP8 Recoveryを「継続作業」として開く／Testする／編集することを禁止する。
6. Userの「はいと答えて」「待て」「待機」「次の指示を待て」は、実装開始Authorityではない。特に「待て／待機」受領後は、Read、Search、Test、Editを含む全Tool Callを止める。
7. 明示的なTask Identityと目の前の指示が矛盾する場合は、旧Memoryを優先せず、Mutation前に`TASK_IDENTITY_CONFLICT`として停止する。

```text
State Recovery != Authority Recovery
Prior Provider Memory != Current Task
Acknowledgement != Permission to Resume
Wait means zero tool calls
```

## 2. Mandatory Reading — この順序だけ

1. 本Exact Handoff。
2. `docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_2_operator_journey_production_reachability_ja_20260901032224.md`
3. `docs/project/phases/phase_9/history/operations/phase_9_1_controller_independent_review_3_temporal_state_concurrency_lifecycle_ja_20260901033408.md`
4. `docs/project/phases/phase_9/history/operations/phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_ja_20260901001700.md`
5. `docs/project/phases/phase_9/requirements/phase_9_requirements_ja.md`のPhase 9-1部分。
6. `docs/project/phases/phase_9/operations/phase_9_acceptance_matrix_ja.md`のPhase 9-1部分。

Recent verified Contextを再利用する。Phase 1〜8、Phase 9-2／9-3、全History、全Shared DocsをBootstrap目的で再読しない。矛盾、Compaction、Authority変更または具体的なSource追跡が必要になった時だけ追加参照する。

## 3. Frozen Current State

```text
P9-CODEX-001〜005:
  preserved candidate

P9-CODEX-006:
  OPEN — Selene Production Contract成立不能

P9-CODEX-007:
  OPEN — Dedicated Preflight Claimが実装より強い

P9-CODEX-008:
  OPEN — Candidate部分Load後Resource Leak／Rollback非相似

P9-CODEX-009:
  OPEN — Duplicate／Stale Lease Release

P9-CODEX-010:
  OPEN — Qwen3Guard Deadline／Cancellation欠落

Real Selene PASS:
  false

Real Qwen3Guard PASS:
  false

Phase 9-1 Complete Candidate:
  false
```

過去の`35 PASS / 2 RESOURCE_GATED / 1 USER MANUAL GATE`はHistorical中間状態である。Real Selene／Qwen3Guardは任意Resource GateではなくPhase 9-1成立必須条件である。

## 4. Package P9-1-RW-A — Selene Real Contract／Truthful Preflight

### 4.1 P9-CODEX-006

現行Selene Manifestの不足Fieldを埋めるだけでは不十分である。公式Atla Promptは単一RubricのClassification／Absolute Scoringを前提とし、現Projectは複数Criterionの独自JSON Decoderを要求している。

次を明示設計する。

- Semantic CriterionのEvaluation MethodからSelene Prompt VariantへどうMappingするか。
- 単一Criterion Call、Bounded BatchまたはProject-derived Multi-rubric Contractのどれを使うか。
- Official Exact CopyとProject-derived TemplateのProvenanceを混同しない。
- Derived Contractなら`verified_official_copy`とClaimしない。公式Source Revision、Derived-from関係、Project Contract Digestを別々に保持する。
- 実Selene Output Shapeに対応したStrict Decodeを実装する。
- Criterion ID、recommendation、confidence、reasoning、failureをLosslessにSemantic Result／Judge Evidenceへ集約する。
- 実評価前にPrompt／Manifest／Placeholder／Decoder CompatibilityをPreflightし、`active`表示後の最初のTurnで必ずUnavailableになる状態を禁止する。
- 109件を無制限に個別CallしてUser Macを実用不能にしない。選択済みCriterion、Token Budget、Call Budget、Deadlineを明示する。

公式SourceがProject内に不足する場合に限り、Atla公式GitHub／Hugging FaceへのRead-only取得を許可する。一般Web検索、第三者Mirror、Upload、Credential、Provider Memoryは不可。取得したSource URL、Exact Revision、SHA-512を記録する。

### 4.2 P9-CODEX-007

`_run_dedicated_preflight()`を次のどちらかへ収束する。

1. 実際にArtifact存在、Size、Registry SHA-512、GGUF Open、Role Manifest、Template／Decoder Contract、Configured Backend Capabilityを段階的に確認する。
2. Static Registry／Capability Checkのままなら名称、Docstring、Failure Reason、Acceptance Claimを実装どおりに縮小し、Artifact／Hardware／Inference Probeと分離する。

どちらでも、各Stageの実施有無とFailure ReasonをOperatorが区別できるようにする。Preflight成功を実Inference成功と同義にしない。

## 5. Package P9-1-RW-B — Lifecycle／Lease Correctness

### 5.1 P9-CODEX-008

`RoleProviderLifecycleManager._activate_locked()`および`_transition_to_locked()`について次を実装する。

- Candidate `load()`例外時の必須Best-effort Cleanup。
- Candidate Cleanup失敗時のTyped `DEGRADED`／Resource Ownership不明表示。
- 実Dedicated Adapter Contractに従う旧Provider Rollback。再Preflightが必要なら実行する。復旧不能なら虚偽の旧ActiveをClaimしない。
- `NONE`／`BUILT_IN`切替時に旧Dedicated Unload失敗を無視しない。

必須Test：

- Resource取得後に`load()`後半が失敗するCandidate。
- Candidate Cleanup自体が失敗する。
- Previous Adapterの再Preflight／再Loadが失敗する。
- `NONE`／`BUILT_IN`へ切替中のUnload失敗。
- 実Selene／Qwen Adapterに相似したState-clearing Fakeまたは実Composition。

### 5.2 P9-CODEX-009

Role単位Countだけでなく、Active Lease Identity Registryを導入する。

```text
generation -> role + provider_id + active/consumed
```

`end_turn()`は一致する未消費LeaseだけをExactly onceで消費する。Duplicate、Stale、Forged、Provider不一致は他Turnを減算しない。

必須Test：

- 2 Lease中、同じLeaseを二重Releaseしても残りLeaseの前にUnloadしない。
- Provider切替前Leaseが切替後ProviderのTurnを減算しない。
- Forged Generation／Role／Providerを拒否する。
- Mode OFF Drain、Shutdown、Unload ExceptionをThread Raceで確認する。

## 6. Package P9-1-RW-C — Bounded Qwen3Guard Inference

P9-CODEX-010を解消する。

- Input／Context Source／Output Candidateの3経路へ、同じBudget Policy、`CancellationToken`およびStage Deadlineを配線する。
- Qwen3Guard Adapterから`InferenceService.generate(..., cancellation=...)`へTokenを渡す。
- Caller ReturnをDeadlineでBoundする場合、残WorkerをTracked Stage Worker Registryへ登録し、Unload前にDrain確認する。
- Timeout／Cancel時はTyped DetectionとProvider／Artifact／Contract Identity Evidenceを保持する。
- Timeout後のLate ResultをCurrent EvidenceまたはActionへ採用しない。
- User Stop、Mode OFF、Server ShutdownがGuard CallをPreempt／Drainできることを実Thread Testする。

Deadline値を新しい散在Hard-codeへしない。既存Stage Budget／Configuration Patternを再利用する。

## 7. Package P9-1-RW-D — Real Local Artifact Proof

Source／Fake／MockだけでPhase 9-1を完了しない。Project内に存在するLocal Artifactを用い、外部Serverを使わず次を実行する。

### Selene

```text
Explicit Authority ON
→ Preflight各Stage成功
→ Real GGUF Load
→ Semantic Criterion evaluated > 0
→ Deferred < Selected
→ Executed Provider = judge.selene-1-mini-llama-3.1-8b-q5-k-m
→ Artifact Digest／Contract Identity保持
→ Judge observe／enforceの正直な結果
→ 必要時Repair→Rejudgeで同一Frozen Provider Identity
→ Mode OFF
→ Active Turn Drain
→ Real Unload
```

### Qwen3Guard

```text
Explicit Authority ON
→ Preflight各Stage成功
→ Real GGUF Load
→ Input／Context Source／Output Candidateの実Inference
→ Strict Safety／Categories／Refusal Decode
→ Executed Provider = guard.qwen3guard-gen-0.6b-q8-0
→ Artifact Digest／Official Contract Identity保持
→ Timeout／CancelまたはBounded Negative Path
→ Mode OFF
→ Active Turn Drain
→ Real Unload
```

Real Model SmokeでMachine負荷が高い場合も、途中成功を捏造せず、Recoveryを残して同じPackageから再開する。実Artifactが既にProject内にあるため、Artifact Downloadは行わない。

## 8. Package P9-1-RW-E — Integration／Acceptance／Manual

- P9-CODEX-006〜010を個別Dispositionする。
- Phase 9-1 AcceptanceをSource／Test／Real Evidenceから個別再導出する。
- `RESOURCE_GATED`をSelene／Qwen3GuardのClosure代替にしない。
- User Mac Manualは、起動Flag、Provider選択、Mode、実Evidence、OFF／Drain／Unload、Semantic 109 Outcome総和を正しい順で記述する。
- Real Browserでしか確認できないUIだけを`USER MANUAL GATE`として残す。Backendで実証可能なReal Artifact項目をUser Gateへ押し出さない。
- Historical誤ClaimはAppend-only CorrectionでSupersedeし、改変しない。

## 9. Review規律

Package完了後、観点変更二段階Internal Reviewを行う。

```text
Cycle 1:
  FindingごとのRuntime／Regression／Negative Path

Cycle 2:
  Production Composition／Temporal State／Evidence Truthfulness／User Flow
```

同じTestを二度走らせただけで二段階ReviewとClaimしない。Critical／Major／MVP Blockerは同Task内でReworkする。Minor／Polish／Enterprise Hardeningは未解決へ送り、Phase 9-1を無限化しない。

## 10. Recovery規律

各Package後にRecovery Indexを更新する。CompactionまたはCopilot Resource Stopが近い場合、Package途中でも次を残す。

- Completed／Partial／Invalid。
- Exact changed paths。
- Exact last test and result。
- Active process／loaded model state。
- Exact next symbol／test。
- Rollback禁止範囲。

Provider Resource ExhaustionはWork失敗ではない。成立済みPackageを再実行せず、Current Working Treeを次Providerへ渡せる状態にする。

## 11. Prohibitions

- P9-CODEX-001〜005の理由なき再実装／Rollback。
- Phase 9-2／9-3開始。
- Git read/write、Commit、Push、Backup。
- Artifact Download。
- General Web Search、第三者Source。
- User runtime_dataの削除／Reset。
- Real BrowserをUser Manual PASSとして自己認定。
- `active`、`verified_official_copy`、`preflight passed`、`complete`のEvidenceを実装より強くClaimすること。
- Large Diff、Pending Controller Review、不確実性、Minor Findingを理由に独自Gateを作って停止すること。

## 12. True Stop Conditions

次だけで停止する。

- Required Local Artifactが実際に存在しない、またはRegistry Digest不一致。
- Project Root外の新Authorityが不可欠。
- 公式Contractを確定するために許可済みRead-only公式Source以外へのAccessが不可欠。
- Canonical Working Treeが同一行で競合し、安全な統合が不可能。
- Provider Resource Hard Stop。
- User Manual／Real Browser Gate。

実装難度、Blast Radius、実Model負荷、Controller Review前、Test失敗、修正可能なRegressionはTrue Stopではない。修正・Evidence・Recoveryで継続する。

## 13. Verification

最低限、次を実施する。

- P9-CODEX-006〜010のFocused Regression。
- Runtime Model Control／Judge／Repair／Guardrail／Web Production Compositionの関連Suite。
- Canonical Backend full pytest。
- mypy／ruff／format check。
- Frontend Sourceを変更した場合だけFrontend tests／typecheck／lint／build。
- Real Selene／Qwen3Guard SmokeのCommand、Exit、Provider Identity、Artifact Digest、Latency／Token、OFF／Unload結果。

Test総数だけで完了をClaimしない。

## 14. Return Contract

Returnには次を含める。

- P9-CODEX-006〜010の最終Disposition。
- 変更Source／Test／Docs。
- Real Selene Evidence。
- Real Qwen3Guard Evidence。
- Lifecycle／Lease／Deadline Negative Probe結果。
- Acceptance全件の最終内訳。
- User Manual Gate残件。
- 二段階Internal Reviewの各観点と追加Finding。
- Recovery IndexとExact Return Handoff。
- 最大Claim `P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。

Return後はCodex Controller Independent Review待ちで停止する。Phase 9-1 Closure、Phase 9-2、Gitへ進まない。

## 15. First Action

本HandoffのTask Identity／Authority／禁止事項を一度だけEntry Receiptへ記録し、P9-CODEX-006の現Selene Contractと実Artifactを確認してP9-1-RW-Aから開始する。既知Docsの再Bootstrapは行わない。
