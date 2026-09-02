# Phase 9-1 Claude Four-percent Resource-bounded Long-run Exact Handoff

```yaml
document_id: phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_handoff_20260831221823
document_type: exact_continuation_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-08-31 22:18:23 JST
phase: phase_9
program: phase_9_1
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_continuity: continued_not_fresh
available_weekly_resource_at_handoff: approximately_4_percent_user_reported
start_boundary: P9-1-0 recovery freeze then P9-1-A
implementation_authority: true_after_exact_user_start
project_root_external_artifact_authority: false
real_model_load_authority: false
network_authority: false
git_authority: false
backup_authority: false
phase_9_closure_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Objective

Phase 6で成立済みのSemantic 109、Selene／Qwen3Guard Adapter、Role Lifecycle、Provider Selection、Judge Dispatch、Budget／Cancel／Recordingを再実装せず、Phase 9-1で未成立のProduction接続だけを差分修正する。

目標は次である。

1. Dedicated Selene／Qwen3Guard RuntimeのProduction配線をAuthority内で完成させる。
2. Semantic 109をProduction Turnで実評価可能にし、`Deferred 109／evaluated 0`固定から脱却させる。
3. Judge／Repair／Rejudge／Adopt・Reject・Safe Fallbackを同一Request Chainへ接続する。
4. 二段階Internal Reviewと検証を行い、Codex Controller Review用Candidateを返す。

Claudeの週間利用可能量はUser報告で約4%である。低残量それ自体を自主停止理由にしない。実際のResource Hard Stopまで進め、Hard Stop時だけ成立済みWork UnitとCurrent PartialをLosslessに直列化して返す。

## 2. Continuity — Fresh Task化しない

このTaskはFresh Taskではない。Current Claude設計者兼実装者役Taskを継続する。

- Role Bootstrap、Mandatory Role Reading、Digest ReceiptまたはAuthority初期化をやり直さない。
- 過去ContextよりCurrent Working Tree、Current Phase 9 Docsおよび本Exact Handoffを優先する。
- 本Handoff作成前のPreflight／Phase Index変更を外部競合と誤認せず、そのままCanonical Working Stateとして受け入れる。
- 新しい三段階貼り付け手順やPrompt文書を作らない。

既存のClaude Long-running／Internal Review／比例的Autonomy Ruleは有効だが、開始前に全文再読して利用可能量を消費しない。

## 3. Minimum Reading／Digest

開始前に読むのは次の3文書だけとする。

1. 本Exact Handoff。
2. `docs/project/phases/phase_9/history/operations/phase_9_1_governance_semantic_debt_preflight_ja_20260831221231.md`
3. `docs/project/phases/phase_9/operations/phase_9_execution_plan_ja.md`の§1、§3、§4、§7、§8。

Requirements／Architecture／Acceptance MatrixはCurrent Canonical Referenceであり、該当Work Unitで必要な節をTargeted Readingする。Phase 3〜8 Historyや旧Handoffを開始前に全走査しない。

```text
Preflight SHA-512:
f6af1d33f13fd541426a1ff9b3f0f9787fb4f90e3e6a7a23b595745318356fbc2a5556a408a90ba6f531172f1abd70425c7f6d48730d8b181b8622abb6097cdb

Execution Plan SHA-512:
54ca3dd7e5c9eb40d208fd765465f5fd14d1f3b661358e154189235ea00167344a3250be3eb4d6a43fdb25b1a52343fa2c35254b5aac7e2a91bb3d42dc5f8ea2
```

## 4. Preserved Entry State

```text
Phase 8                       : COMPLETE／ACCEPTED／CLOSED
Phase 9                       : READY
User Backup                   : USER CONFIRMED COMPLETE
Phase 9-1 Preflight           : GO／COMPLETE
Source Implementation         : NOT STARTED
Focused Governance Baseline   : 258 passed
Real Model Load／Inference     : 0
Network                       : 0
Project-root-external Artifact: NOT READ
User runtime_data Mutation    : 0
Git Mutation after Backup     : 0
```

P9-1-0-WU-001〜003相当のAs-built／Authority AuditはController Preflightに実質的に含まれている。Claudeは同じ監査を最初から繰り返さず、最初の短いRecovery IndexへPreflight Dispositionを写して`P9-1-0 COMPLETE BY PRESERVED CONTROLLER PREFLIGHT`と固定し、直ちにP9-1-Aへ進む。

## 5. Reuse Boundary — 再実装禁止

次をPreserved As-builtとして扱う。

- Runtime GovernanceのSemantic Criterion、Frozen Turn、Provider State、Result、Action Resolution、Evidence。
- Canonical 109 Descriptor Compiler／Adapterと109件網羅Test。
- Selene Prompt Manifest／Strict Result Adapter入口。
- Qwen3Guard Target別Contract、Official Manifest、Line Protocol、Decode、Detector Adapter。
- Dedicated Role Load／Unload／Authority Gate。
- Provider Selection、Lifecycle、Lease、Tracked Worker、Atomic Mode／Provider Transition。
- Built-in／Selene／Main-shared Judge Dispatch、Semantic Snapshot、Judge／Repair／Recording入口。
- Phase 6で成立したBudget、Deadline、Cancel、Late Result、Failure Presentation、Configured／Active／Executed Identity。

存在確認を目的とした全面置換や、P6の再実装をしない。User Mac FailureとProduction Composition Rootの差だけをProbeし、最小差分で接続する。

## 6. First Exact Actions

1. 本HandoffとPreflightを読み、Current DiffをRollbackせず確認する。
2. `P9-1-0`用のCompact Recovery Indexを1件だけ作り、PreflightのPreserved State、258件Baseline、Authority境界、Exact Next Actionを記録する。
3. P9-1-A-WU-001から開始し、Artifact／Manifest／Digest／Quantization／Backend／Hardware Preflight ContractとProduction Composition Rootの差を確定する。
4. Authority内で実装・Focused Test・Recoveryを進め、P9-1-A〜Dを連結実行する。

利用可能量が少ないため、長いEntry報告を作らない。Receiptは次の一行で十分である。

```text
Phase 9-1 Current Task継続／Preflight継承／P9-1-0 Recovery固定後P9-1-A開始。
```

## 7. Long-run Scope

Execution Planの23 WUをCurrent As-builtに合わせて縮約・再利用し、次を連結する。

```text
P9-1-0  Preserved PreflightをRecoveryへ固定
P9-1-A  Dedicated Selene／Qwen3Guard Runtime
P9-1-B  Semantic 109／Built-in Evaluation
P9-1-C  Judge／Repair／Rejudge／Semantic ENFORCE
P9-1-D  Integration／二段階Review／Return Candidate
```

P9-1-DのInternal Reviewは観点を変えて2回行う。

- Cycle 1：Requirement／Negative Path／Concurrency／Resource。
- Cycle 2：Evidence Truthfulness／Acceptance／User Journey／PoC停止線。

Cycle 1のFindingを必要に応じてReworkしてからCycle 2へ進む。同じ観点を言い換えただけの重複Reviewにしない。

P9-1が成立してもPhase 9-2へ入らず、Codex Controller Review用Returnで止める。

## 8. Authority-independent Progress／External Gates

### Selene Official Prompt

Official Prompt Copyは未検証で、Network Authorityはない。推測PromptをOfficial扱いしない。Official Source取得が必要になった場合はExact Gateとして記録するが、Task全体を止めず、Authority-independentなComposition、Parser、Failure、Fixture、Semantic、Judge／Repair作業を続行する。

### Real Artifact

Selene／Qwen3Guard ArtifactはProject Root外のため、本HandoffではRead／Stat／Digest／Load／Inferenceしない。Fixture PASSをReal Artifact PASSへ格上げしない。Real Smokeが必要なWork Unitだけ`AUTHORITY REQUIRED／NOT RUN`として分離し、他のWork Unitを続行する。

### Qwen3Guard Contract

Official Contract ManifestはPhase 6でVerified済みである。再取得や再調査を入口条件にしない。

## 9. Allowed／Forbidden

### Allowed

- Project Root内のPhase 9-1 Source、Test、Config、Frontend、Static Artifact、Docs、Recovery、Finding Ledger、Return Handoff。
- 既存`.venv`および既存Frontend dependencyを用いたFocused／Canonical Verification。
- Fixture、Fake、Deterministic Provider、Mock Transport。
- 必要なSource／Testの追加・修正と、比例したBuild／Static再生成。

### Forbidden

- Project Root外ArtifactのRead／Stat／Digest／Load、Real Model Inference。
- Network、Install／Download、Browser、User `runtime_data/` Mutation。
- Git Read／Write、Clean、Commit、Push、Backup、Roadmap更新、Phase Closure。
- Phase 9-2／9-3、Phase 10／11、General Search、Docs全統合、Full Constitution、UI全面改修。
- Preserved Phase 6実装のRollback、全面再実装、成立済みWork Unitの再実行。

新しいAuthorityが必要なら対象ActionだけをGateへ残す。Authority不足を理由に、無関係なAuthority-independent作業まで止めない。

## 10. Recovery／Resource Exhaustion

- Package BoundaryごとにRecovery Indexを作る。
- 残4%のため、各Work Unitまたは意味のあるPartial差分の直後にCurrent Recoveryを短く更新してよい。ただしSource作業よりDocs量が大きくならないようにする。
- Compactionが近い場合も、Current WU、成立済み差分、Changed Paths、実行済みTest、失敗形、Exact Next Actionを残して続行する。
- 実際のResource Hard Stopが発生した場合、Completed／Partial／Invalidを分離し、Current Working TreeをRollbackせずExact Returnする。
- Provider Resource ExhaustionはJob Failureではない。次のCodex設計者兼実装者役Taskが同じWorking Treeから継続できる形にする。
- Resource残量が低いという予測だけで自主停止しない。

## 11. Stop／Review Line

Program全体の停止候補はExecution Plan §7だけである。

- Canonical Stateの重大衝突で安全な正本を選べない。
- 必須Artifactが存在せず、新しいNetwork／License／Cost Authorityが必要。
- 既存Data／Schemaを不可逆に破壊するMigrationが必要。
- Resource Hard StopでCurrent Work Unitを安全収束できない。
- Real ModelがMacを不安定化し、安全なUnload／Process停止ができない。
- User Manual GateまたはController Review Return Point。

実装難度、大きなDiff、Blast Radius、Independent Review前、不確実性、Minor Finding、非Blocking Incident、Candidateを自分で最終承認できないことは停止理由ではない。

```text
Risk Detection ≠ Stop Authority
Complete Candidate ≠ Final Acceptance ≠ Closure
```

Critical／Major／MVP BlockerはCurrent Package内でReworkする。Minor／Hardening／低頻度Edgeは未解決へ送り、PoC／MVPの進行を止めない。

## 12. Return Contract

通常完了時またはResource Hard Stop時のExact Returnに、次を含める。

- Package／WU別のCOMPLETE／PARTIAL／NOT RUN。
- Preserved Phase 6 As-builtと新規Changed Paths。
- Focused／Canonical Test結果とRegression。
- Selene Prompt、Real Artifact、Network、Model、User Data、GitのAction Inventory。
- Semantic 109のApplicable／Evaluated／Passed／Deviation／Unknown／Unsupported／Deferred集計。
- Dedicated Configured／Active／Executed IdentityとFailure Stage。
- Judge／Repair／Rejudge／Adopt・Reject・FallbackのRequest Chain Evidence。
- 二段階Internal ReviewとRework Disposition。
- Acceptance個別Disposition、Open Finding、User Mac Manual Gate。
- Active Process／Temporary Artifact／Exact Next Action。

通常完了の最大Claimは`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Resource Hard Stop時は成立範囲に応じた`RESOURCE_EXHAUSTED_PARTIAL_WITH_EXACT_RECOVERY`とし、完成を捏造しない。

## 13. Exact Start

```text
Phase 9-1をCurrent Claude Task継続で開始する。Preserved PreflightをP9-1-0 Recoveryへ固定し、P9-1-AからAuthority-independent作業を自走する。
```
