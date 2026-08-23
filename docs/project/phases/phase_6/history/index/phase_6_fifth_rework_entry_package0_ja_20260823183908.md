# Phase 6 Fifth Rework — Recovery Entry（Package 0: Entry／Recovery Freeze）

```yaml
document_id: phase_6_fifth_rework_entry_package0
status: recovery_entry
phase: phase_6
package: package_0
role: Claude側設計統括者役
created_at: 2026-08-23 18:39:08 JST
governing_handoff: phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md
```

## Current Package／Work Unit

Package 0（Entry／Recovery Freeze）。Mandatory Reading完了、Current Diff／Active Process／
Scratch／Model State確認完了。Package Aへ進む直前。

## Last Completed Action

Fifth Independent Review Rework Handoff（`phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md`）
を全文読了。Mandatory Reading Order記載の13文書は、本Session内で既に全文読了済み
（Requirements／Architecture／Acceptance Matrix／Execution Plan／Role Authority Matrix／
Task Role Write Authority Policy／統合Governance文書／Fourth Independent Review Handoff／
自著Fourth Rework Complete Candidate Handoff／自著Fourth Rework Acceptance Rederivation／
P6-GOV-006／DeepSeek Quantization Complete Candidate Handoff／DeepSeek Quantization
Completion Evidence）——Session Context内に内容を保持しており、本Entry作成時点で
矛盾／古い記述は検出していない。

## Completed Findings

なし（Package 0はEntry Freezeのみ、Source Mutation未実施）。

## Open Findings（Severity／Current Impact）

```text
P6-CODEX-034 CRITICAL／REQUIRED — Judge/Repair実行中のRuntime Model Switch Unload競合
P6-CODEX-035 CRITICAL／REQUIRED — Switch後MAIN Role Binding消失
P6-CODEX-036 CRITICAL／REQUIRED — Governance Capability/BindingがBootstrap Qwenに固定
P6-CODEX-037 CRITICAL FUNCTIONAL／REQUIRED — DeepSeek Multi-turn Chat Template/EOS非互換
P6-CODEX-038 CRITICAL PATH SAFETY／REQUIRED — Recording Path Check-then-use TOCTOU残存
P6-CODEX-039 CRITICAL EVIDENCE／REQUIRED — Validation/Acceptance/Return Contract未達
P6-CODEX-040/P6-GOV-007 CRITICAL GOVERNANCE EVIDENCE／REQUIRED — 存在しないUser Override記録
```

全件Open。Current Impact：Fourth Rework Complete Candidateは受理されず、Phase 6は
Do Not Close状態。

## Exact changed files／Exact new files

Package 0時点でのSource Mutationは0件。Git Working Treeには本Session以前からの
大量のUncommitted Change（全Phase 6 Rework、Modified 62件、Untracked 152件、
Commit未実施のまま蓄積）が存在するが、これはFifth Rework開始前からの既存状態であり、
Fifth Rework自身の変更ではない。Fifth Rework自身が変更するFileは、各Package完了時の
Recovery Entryで個別に列挙する。

## Executed Commands／Exit Codes／Test Counts

```text
git status --porcelain | wc -l  → 214（Exit 0、Read-only）
ps aux | grep margpa_runtime_llm.entrypoints  → 該当なし（Exit 0、Read-only）
ls .venv/.t/  → 既存Scratch多数確認（Exit 0、Read-only、削除等一切なし）
ls docs/.../history/index/  → 既存Recovery Index一覧確認（Exit 0、Read-only）
```

Test実行は本Package内では未実施（Package Aから開始）。

## Active Process／Model Load／Scratch State

```text
Active Process: margpa_runtime_llm.entrypoints系のProcessは0件（前Session終了時にKill済み）。
Model Load State: 現在、実Model（Qwen／DeepSeek）はいずれもUnload状態
  （Preview Serverが起動していないため）。
Scratch State: .venv/.t/配下に他Session由来の既存Directory多数（r*, f*, m2, final9等）——
  本Task（Fifth Rework）はこれらに一切触れず、新規作成が必要な場合は
  `.venv/.t/phase_6_fifth_rework_<timestamp>/`配下のみ使用する。
```

## User runtime_data Contact Count

0（Package 0はRead-onlyのRepository状態確認のみ）。

## Root-outside／Git／Network／Provider Memory Action Count

0。

## Artifact／Snapshot／DigestのCurrent State

```text
Qwen Artifact: main.qwen3-4b-q4-k-m、sha512=f182f1d4...（前Session確認値、未変更）
DeepSeek Artifact: main.deepseek-r1-0528-qwen3-8b-q4-k-m、
  sha512=b32af428...（前Session確認値、未変更）
Config Definition Files: config/models/qwen3_4b_q4_k_m.toml、
  config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml——前Session作成のまま、
  本Entry作成時点で未変更。
```

## Exact Next Action

Package A（Runtime Switch Integrity、対象P6-CODEX-034／035／036）を開始する。
最初の実施内容：

```text
1. src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
   のBusy判定（ConversationServiceBusyGate、active_request_id依存）を読み、
   Judge/Repair Background実行中にMain Leaseが解放されている実際のWindowを
   Sourceレベルで再確認する。
2. src/margpa_runtime_llm/modules/runtime_model_control/application/
   runtime_model_controller.py のbegin_switch()を読み、MAIN Role Binding
   再構築が欠落している箇所を特定する。
3. src/margpa_runtime_llm/bootstrap/runtime_governance.py を読み、
   RuntimeGovernanceCompositionがBootstrap一回限りで構築されている箇所を特定する。
```

## Exact Resume Command／Resume手順

```text
1. 本Entryを読む。
2. `git status --porcelain`で、本Entry作成時点からのDiffを確認する
   （Fifth Rework自身が加えた変更のみが増分として現れるはずである）。
3. 上記「Exact Next Action」からPackage Aを再開する。
4. Package A完了条件（Handoff §5）を満たしていない場合、未完了のFindingから
   継続する。
```
