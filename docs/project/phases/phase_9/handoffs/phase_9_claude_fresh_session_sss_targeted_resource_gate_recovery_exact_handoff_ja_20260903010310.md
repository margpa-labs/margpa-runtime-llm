# Phase 9-1 Claude Fresh Session — SSS Resource Gate局所復旧 Exact Handoff

```yaml
document_id: phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_handoff_20260903010310
document_type: exact_implementation_handoff
document_state: ready
phase: phase_9
program: phase_9_1
work_package: P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY
from: Codex Controller
to: Claude Code Fresh Session
created_at: 2026-09-03 01:03:10 JST
language: ja_with_structured_english_terms
authority: bounded_source_test_and_exact_return
backup_state: current_backup_complete_user_report
git_action: prohibited
network_action: prohibited
external_artifact_mutation: prohibited
closure_authority: none
```

## 0. Fresh Session Rule

これは旧Claude SessionのContinuationではない。旧Sessionで形成された因果説明、完了判定、Open Finding処遇、Resource Gateの妥当性評価または「As Designed」判断をCurrent Premiseとして継承しない。

Current Taskは本Handoffだけである。過去Taskの自動再開、Stale TODOの実行、Package 3、Context拡張、Phase 9-2／9-3またはDocs統合へ進まない。

長期Session／反復Compactionによる前提固定化は未確認仮説であり、本Handoffはそれを真因と断定しない。ただしFresh Sessionの目的は、旧Sessionの局所NarrativeをCurrent Authorityから切り離し、Source／Product Evidenceから独立に復旧判断することである。

## 1. Objective

新規`SystemMemoryRoleResourceGate`によって破壊されたDedicated Judge／GuardのProduction Activationを、最小Source DeltaでPre-Claude Baselineへ戻す。

最初のRecovery方針は次で固定する。

```text
TARGETED REPAIR FIRST
FULL RESTORE TO 1f0e70e ONLY AS CONTROLLER-OWNED HARD FALLBACK
```

Claudeは全巻き戻しを実行しない。局所修復後に正経路が戻らない場合、Sourceを追加改造せずTrue Stopし、Codex Controllerへ返す。

## 2. Confirmed Current State

### 2.1 Incident

```text
- MainとBuilt-in以外のDedicated Providerが実UIでLoad不能になった。
- User Manual時、SeleneとQwen3Guardはresource_gate_deniedになった。
- Current Gate算式ではFresh Default Judge Gemmaも通常条件でdenyされる。
- Package 2 Complete／Residual Complete／Blocker NONEは無効化済み。
- Current Working TreeはQuarantined／Unaccepted。
```

### 2.2 Direct Source Cause

```text
New Source:
  src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py

Production Wiring:
  src/margpa_runtime_llm/bootstrap/web_application.py
  RoleProviderLifecycleManager(resource_gate=SystemMemoryRoleResourceGate(...))

Gate Formula:
  required = candidate_artifact_bytes + active_main_artifact_bytes + 3 GiB
  deny when required > psutil.virtual_memory().available
```

`available`はMain Load後の残存Available Memoryである一方、式はMain Artifact Sizeを再加算する。Artifact Size、Runtime Resident Memory、KV Cache、Metal Allocationおよび固定Marginも同一量ではない。この式をParameter Tuningで救済しない。

### 2.3 Misleading Test

```text
tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
```

このTestは名前に`real`／`concurrent_load`を含むが、実ModelをLoadしない。Gateと同じ式をTest側で再計算し、一致をassertする自己参照Oracleである。Product Availability Acceptanceには使用しない。

### 2.4 Recovery Points

```text
Stable Commit:
  1f0e70e47fa058484c4b32f33c6cbca52e0afd2a

Pre-Claude Backup:
  2026-09-02 12:31 User Backup
  Backup git main ref == 1f0e70e
  Critical Source hashes matched Commit

Current Backup:
  COMPLETE（2026-09-03 User Report）
```

Claudeは`git reset`、`git checkout`、`git restore`、Stash、Branch切替、Backup展開またはFile削除を行わない。

## 3. Bounded Read Set

最初に読む対象を次へ限定する。

```text
1. 本Handoff
2. docs/project/shared/history/ai_system_anomalies/claude_code/
   claude_code_sss_resource_gate_foundation_destruction_and_resource_exhaustion_incident_ja_20260903001814.md
3. docs/project/shared/history/ai_system_anomalies/claude_code/
   claude_code_sssss_post_incident_harm_minimization_legal_overreach_and_transparency_failure_ja_20260903002931.md
4. src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py
5. src/margpa_runtime_llm/bootstrap/web_application.py
6. RoleProviderLifecycleManagerとAllowAllRoleResourceGateの定義
7. Resource Gate関連Unit／Integration Test
8. `git diff 1f0e70e --`のうち上記Source／Testに直接関係する範囲
```

不足がSource上で具体的に生じた場合だけ、直接Import／Call先を追加で読む。Routine ProgressごとにPhase Index、Roadmap、全Handoff、全Historyを読み直さない。

### 3.1 Explicit Read Prohibition

次のFileはUserがQuota回復後に読むよう明示しており、本Taskでは読まない。

```text
docs/project/shared/history/planned_work/
phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md
```

## 4. Authorized Mutation Scope

必要最小限の次だけを変更してよい。

```text
- Production Resource Gate wiringをPre-Claude Baselineへ戻すSource
- そのImport／Composition差分
- GateがProductionへ入らないことを証明するFocused Regression Test
- Main＋Gemma／Main＋Qwen3GuardのPositive-pathを証明するTest
- Existing Testのうち、新しい正しいAcceptanceと直接矛盾するGate期待値
- 最終Exact Return Handoff 1件
```

新規`memory_resource_gate.py`はIncident Evidenceである。勝手に削除しない。Productionから切り離し、Quarantined／UnusedとしてExact Returnに記録する。最終的な削除・保存判断はControllerが行う。

## 5. Explicit Non-goals／Prohibitions

```text
- Gate算式の微調整
- 3 GiB Marginの変更
- 新しいMemory Heuristic／Automatic Resource Managerの設計
- Main＋Selene事故の真因確定Claim
- Context 16384／Output 4096・8192のPackage 3
- Phase 9-2／9-3
- Phase 10／11作業
- Roadmap／Public Docs／Portfolio Docs更新
- Current Index／Unresolved Registryの更新
- 既存Historyの変更
- 新規Instruction Document作成
- Model再Download／Network Access
- `/Users/yukitakagi/models`配下の書換え・移動・削除
- `.claude/`作成・更新
- Commit／Push／Branch／Stash
- Claude自身によるPhase Closure／Blocker NONE／完全成功Claim
```

## 6. Work Units

### P0-RG-01 — Read-only Preflight

```text
1. `git status --short`で既存Dirty Treeを記録する。
2. Current Backup CompleteをUser Reportとして受領する。
3. `git diff 1f0e70e`でGateのProduction配線だけを特定する。
4. RoleProviderLifecycleManagerのDefault Resource GateがPre-ClaudeでAllowAll相当だったことを確認する。
5. 本Handoff範囲外の変更を触らない。
```

### P0-RG-02 — Regression Test First

Production Compositionが`SystemMemoryRoleResourceGate`を注入しないことを、既存Composition Testへ追加する。

Test Oracleは「同じGate算式を再計算する」ではなく、次のProduct Contractから作る。

```text
MainがActiveでも、明示選択・Authority-granted Dedicated Provider Activationは
Resource EstimateだけでLoad前拒否されない。
```

Testを先に追加し、Current Sourceで失敗することを確認する。意図したFailure以外が出た場合は原因を分離する。

### P0-RG-03 — Minimal Production Repair

`web_application.py`の`RoleProviderLifecycleManager`構築をPre-Claude Baselineへ戻す。

```text
- `SystemMemoryRoleResourceGate`のProduction injectionを外す。
- Constructor DefaultがAllowAll相当であることを確認して利用する。
- Gemma／Selene／Qwen3Guard Adapter、Authority Gate、Lifecycle、Lease、Unloadは変更しない。
- Resource Gate以外のPackage 1／2成果候補を巻き戻さない。
```

修復目的を超えるRefactorをしない。

### P0-RG-04 — Focused Verification

最低限、次を実行する。

```text
- Production Wiring Test
- Provider Selection／Role Atomicity Test
- Role Lifecycle Manager Test
- Dedicated Adapter Production Wiring Test
- Gemma／Selene／Qwen3Guard Adapter Unit Test
- Judge Live Integrationの該当Focused Test
- Ruff／MypyのTouched Scope
- git diff --check
```

既存の自己参照Gate TestがGreenでもProduct Acceptanceとして数えない。新しいContractと矛盾する期待値は、削除ではなく意味を明示して修正する。

### P0-RG-05 — Real Positive-path Evidence

既存Local Artifactだけを使う。Download／Networkは禁止。

順序を固定する。

```text
1. Main Baseline Load／Inference
2. Main Active + Gemma Activation
3. Gemma実Inference + Strict Decode
4. Gemma OFF／Unload
5. Mainが引き続きActive／Inference可能
6. Main Active + Qwen3Guard Activation
7. Qwen3Guard input／output_candidateの実Inference
8. Qwen3Guard OFF／Unload
9. Mainが引き続きActive／Inference可能
```

各Stepで次を保存する。

```text
- Configured／Active／Executed Provider
- Model／Artifact／Manifest Identity
- Load result
- Inference result
- Typed Failure Code／Reason（失敗時）
- OFF／Unload result
- Main preservation result
- Active process／worker cleanup
```

このTaskではSeleneのMain同時Loadを必須にしない。元Incidentの真因が未確定であり、User Macを再び不必要に危険へ晒さないためである。Seleneは次だけ確認する。

```text
- Gateによる事前denyではなく、明示Authority後にAdapter Preflightへ到達できる。
- Standalone Load Smokeが安全に実行可能な既存条件なら1回だけ実行する。
- Main＋Selene同時LoadはController／Userの別判断へ返す。
```

### P0-RG-06 — Failure Handling

GemmaまたはQwen3GuardのPositive-pathが戻らない場合:

```text
- Gate以外へ推測で修正範囲を拡張しない。
- 原因、Failure Code、最小Reproduction、Touched Filesを固定する。
- Current変更を保持したままTrue Stopする。
- Full Restoreを実行せずControllerへ返す。
```

### P0-RG-07 — Two-stage Internal Review

2回のReviewは完全別観点で行う。

```text
Review A — Product Availability／Regression
  Fresh Default Gemma、Qwen3Guard、Main、Built-in／Main-sharedの正経路。
  「安全拒否」をAvailability成功として数えていないか。
  Existing Acceptanceを失っていないか。

Review B — Safety／Lifecycle／Recovery
  Authority、Load rollback、Lease、OFF／Unload、Main保全、Worker cleanup、
  Shutdown、Failure typing、Dirty Tree保全、Scope逸脱。
```

同じChecklistの言い換えは禁止。Findingがあれば修正し、該当Focused Testを再実行する。

## 7. Acceptance

```text
[ ] Production CompositionからSystemMemoryRoleResourceGateが外れている。
[ ] Gate算式／MarginのTuningをしていない。
[ ] Main＋Gemmaが実Load／Inference／Strict Decodeまで成立する。
[ ] Main＋Qwen3Guardが実Load／Guard inferenceまで成立する。
[ ] Dedicated OFF／Unload後もMainが正常である。
[ ] Built-in／Main-shared QwenにRegressionがない。
[ ] Resource Gateと同じ算式をOracleにしたTestをAcceptanceへ数えていない。
[ ] Seleneは少なくともGate事前denyから解放される。
[ ] Main＋Selene同時Loadの未解決Riskを隠していない。
[ ] Touched Focused Tests／Ruff／Mypy／diff-checkが結果付きで記録される。
[ ] 2回の完全別観点Internal Reviewが結果付きで記録される。
[ ] Current Dirty TreeのUser変更を失っていない。
[ ] Git／Network／外部Artifact Mutationが0。
```

## 8. Exact Stop Conditions

次では質問を乱発せず、Evidenceを固定して停止する。

```text
- Gateを外してもGemma／Qwen3GuardのどちらかがLoad不能。
- MainがCrash／Unload／Not Loadedへ遷移する。
- Gate以外のP0／Critical Regressionを1件でも確認する。
- RepairにDestructive GitまたはBackup Restoreが必要になる。
- Real Artifactが欠損している。
- Network／Downloadが必要になる。
- User Dataまたは外部Artifact Mutationが必要になる。
- Scope外Source変更なしでは進めない。
```

True StopでないMinor判断は、最小安全側の判断を行い、Returnへまとめる。Routine ConfirmationでUserを中断しない。

## 9. Exact Return

完了またはStop時、次を1件のExact Returnへまとめる。

```text
1. Maximum Claim
2. Direct Cause
3. Files Changed
4. Files Deliberately Not Changed
5. Before／After Product Behavior
6. Real Gemma Evidence
7. Real Qwen3Guard Evidence
8. Selene Disposition
9. Focused／Static Verification
10. Review A Findings
11. Review B Findings
12. Open Findings／True Stop
13. Action Inventory
14. Exact Next Action for Codex Controller
```

許可Maximum Claimは次だけである。

```text
P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
```

次はClaimしない。

```text
Phase 9-1 Complete
Package 2 Complete
Closure Ready
Blocker NONE
Production Ready
Full Restore Unnecessary
Main＋Selene Incident Resolved
```

Exact Return後は停止する。Index、Roadmap、Stable Docs、Commit／Push、Package 3へ進まない。
