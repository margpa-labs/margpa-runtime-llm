# Phase 9-1 Governance Semantic Debt Preflight

```yaml
document_id: phase_9_1_governance_semantic_debt_preflight_20260831221231
document_type: bounded_implementation_preflight
document_state: final
language: ja
created_at: 2026-08-31 22:12:31 JST
phase: phase_9
program: phase_9_1
decision: GO
implementation_started: false
real_model_action: not_run
network_action: not_run
```

## 1. 結論

Phase 9-1は`GO／NOT STARTED`とする。

ただし入口はゼロ実装ではない。Phase 6 ReworkでSemantic 109 Compiler／Runtime、Selene／Qwen3Guard Adapter、Role Lifecycle、Provider Selection、Judge Dispatch、Budget／Cancel／Recording等が既に成立している。Phase 9-1はこれらを再実装せず、実Artifact、Production Turn、User実画面で未成立だった差分だけを再導出する。

## 2. Entry State

```text
User Backup                    : USER CONFIRMED COMPLETE
Baseline Commit                : f894d3b3f8ab9e903db12ec7c682623fa1c17272
Branch                         : main
Local／origin                  : 同期済み
Phase 8                        : COMPLETE／ACCEPTED／CLOSED
Phase 9                        : READY
Phase 9-1                      : PREFLIGHT GO／NOT STARTED
Source Mutation after Backup   : 0（本Preflight Docsを除く）
Real Model Load／Inference     : 0
Network                        : 0
User runtime_data Action       : 0
Git Mutation                   : 0
```

Backupの内容または保存先はInspectionせず、Userの完了報告を正本とする。

## 3. Environment／Focused Baseline

```text
Python                         : 3.13.14
Node                           : v25.8.1
npm                            : 11.11.0
Focused Governance Baseline    : 258 passed
Phase 8 Closure Backend        : 2191 passed, 7 deselected
Phase 8 Closure Frontend       : 318 passed
.claude                        : absent／gitignore対象
```

Focused 258件はRuntime Governance、Semantic Adapter／Runtime、Selene Adapter、Qwen3Guard Adapter／Manifest、Dedicated Role Adapter、Judge Live Dispatch、Provider Selection AtomicityおよびRuntime Governance Webを含む。

## 4. Reusable As-built — 再実装禁止

- `modules/runtime_governance/`のSemantic Criterion、Frozen Turn、Provider State、Result、Action Resolution、Evidence。
- Canonical 109 DescriptorのCompiler／Adapterと109件を欠落なく扱うTest。
- `adapters/evaluation/selene.py`のPrompt Manifest／Strict Result Adapter入口。
- `adapters/guardrail_governance/qwen3guard_*`のTarget別Contract、Official Manifest、Decode、Detector Adapter。
- `adapters/runtime_model_control/dedicated_role_adapters.py`のDedicated Load／Unload／Authority Gate。
- Provider Selection、Role Lifecycle、Lease、Tracked Worker、Atomic Mode／Provider Transition。
- `bootstrap/judge_live_integration.py`のBuilt-in／Selene／Main-shared Dispatch、Semantic Snapshot、Judge／Repair／Recording入口。
- Phase 6で成立したBudget、Deadline、Cancel、Late Result、Failure Presentation、Configured／Active／Executed Identity。

Phase 9-1は「存在確認のための再実装」や「Testがある機構の全面置換」を行わない。まずUser Mac失敗とCurrent Production Wiringの差をProbeし、最小差分を確定する。

## 5. Exact Unresolved Gates

### 5.1 Selene Official Prompt Provenance

```text
template_type          : official_selene_prompt_template_unresolved
verified_official_copy : false
upstream_revision      : null
template_file／digest  : null
```

SeleneのModel DefinitionとArtifact IdentityはFreeze済みだが、公式Prompt Copyは未検証である。P9-1 Executorが公式取得を必要とする場合、Exact Official SourceへのRead-only Network Authorityを別途必要とする。推測PromptをOfficial扱いしない。

### 5.2 Qwen3Guard Official Contract

Qwen3GuardはOfficial Hugging Face／GitHubのExact Revision、Source Digest、Target別Category SetおよびLine ProtocolがManifestへ固定済みである。公式Contractの再取得を入口条件にしない。実Artifact Load／Inferenceだけを別Gateで扱う。

### 5.3 Real Artifact

Selene／Qwen3GuardのModel ConfigにはRelative Path、Size、SHA-512、Quantization、Backendがある。ただし本PreflightではProject Root外のArtifactをRead／Stat／Digest／Loadしていない。存在、Digest一致、Mac Memory／Latencyおよび実Inferenceは未判定である。

### 5.4 Semantic 109／Judge／Repair

109 Compiler／Runtime Unitは存在しFocused TestもPASSする。残件は、User Macで全件Deferred／evaluated 0になったProduction Pathとの接続、適用可能Criterionの実Outcome、Dedicated Judge、Repair／Rejudge／AdoptまたはFallbackの実Turn証明である。

## 6. First Execution Order

```text
P9-1-0-WU-001  User Mac FailureとCurrent SourceのAs-built Delta固定
P9-1-0-WU-002  Artifact／Manifest／Composition RootのAuthority内Audit
P9-1-0-WU-003  Real Artifact／Network／Model Smoke Gate固定
P9-1-A〜D      Execution Planどおり
```

ExecutorはP9-1-0終了時点でScopeを再発明せず、既存23 WUをCurrent As-builtに合わせて縮約／再利用する。

## 7. Authority Boundary

### Allowed in the later Exact Handoff

- Project Root内のPhase 9-1 Source／Test／Config／Docs／Recovery。
- Existing `.venv`／Frontend dependencyを用いるFocused／Canonical Verification。
- Fixture／Fake／Deterministic経路。
- Userが別途明示した場合だけ、Exact Artifactに対するLocal Model SmokeまたはOfficial Selene SourceのRead-only Network。

### Not authorized by this Preflight

- Source実装開始、Real Model Load、Project Root外Artifact Read、Network、Install、Git、Backup、Browser、User runtime_data Mutation。
- Phase 9-2／9-3、Phase 10／11、General Search、Formal Agent、Full Constitution、UI全面改修。
- Dedicated ProviderのFixture PASSをReal Artifact PASSへ格上げすること。

## 8. Stop／Return

```text
Phase 9-1 Entry : GO
Current State   : PREFLIGHT COMPLETE／IMPLEMENTATION NOT STARTED
Next Required   : Exact Executor Handoff＋Instruction
```

True StopはPhase 9 Execution Plan §7だけを使用する。実装難度、Diff量、Independent Review前またはMinor Findingを理由に新しいGateを作らない。
