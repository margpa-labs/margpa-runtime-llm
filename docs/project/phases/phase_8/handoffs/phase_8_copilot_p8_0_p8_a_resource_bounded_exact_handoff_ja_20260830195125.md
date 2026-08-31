# Phase 8 Copilot P8-0／P8-A Resource-bounded Exact Handoff

```yaml
document_id: phase_8_copilot_p8_0_p8_a_resource_bounded_exact_handoff_20260830195125
document_type: exact_execution_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-08-30 19:51:25 JST
phase: phase_8
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 8 Head Task
authorized_packages: P8-0_and_P8-A
implementation_authority: true_after_exact_user_start
network_authority: false
git_authority: false
backup_authority: false
phase_8_closure_authority: false
maximum_claim: P8-A_BOUNDED_COMPLETE_CANDIDATE
```

## 1. Objective

Phase 8の先頭だけを実行する。Phase 7のWeb Fetch Port／Security Scaffoldを再利用し、Userが明示的に与えたPublic `http／https` URLを、OFF既定、Bounded Fetch、Untrusted Evidence、Main Model Context、Citation／PersistenceおよびFailure UIへ接続する。

General Web Search、Automatic Search、P8-B以降または正式Agent Level 1へ進まない。

## 2. Active Contract Priority

```text
Userの最新明示指示
→ 本Exact Handoff
→ Resource-bounded Execution Plan
→ Phase 8 Requirements／Architecture／Acceptance
→ 比例的Autonomy Correction Addendum
→ Copilot Provider固有Rule 3件
→ Phase 8 Base Handoff
```

Provider固有Rule内の機械的三段階、Fresh Task全履歴再読または各WU過剰Docsは、比例的Autonomy Addendumに従い最小十分へ補正する。本TaskではUserが新Taskを明示しているためRoleを新規Bindingするが、Receiptだけで停止せず、同一MessageのExact Startに従って実装へ進む。

## 3. Minimum Mandatory Reading

1. `docs/project/phases/phase_8/handoffs/phase_8_copilot_p8_0_p8_a_resource_bounded_exact_handoff_ja_20260830195125.md`
2. `docs/project/phases/phase_8/operations/phase_8_copilot_p8_0_p8_a_resource_bounded_execution_plan_ja_20260830195125.md`
3. `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
4. `docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md`
5. `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`
6. `docs/project/shared/task_roles/codex_controller_and_delegated_agent_proportional_autonomy_append_only_correction_addendum_ja_20260828223445.md`
7. `docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md`
8. `docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md`
9. `docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
10. `docs/project/phases/phase_8/history/operations/phase_8_p8_0_p8_a_preflight_ja_20260830195125.md`

上記の後は対象Source／Testを直接読む。Phase 3〜7全History、Phase 8 Scope外Docsまたは旧Copilot会話Contextを追加で全走査しない。

## 4. Baseline／Do Not Repeat

```text
Baseline Commit                : 99c7395c027f1d5e5d038b7f453f53b4b2c0cdb0
Phase 7                       : CLOSED
Focused Backend Baseline      : 64 passed
Focused Frontend Baseline     : 1 file／6 passed
P8-0／P8-A Source Mutation     : 0 at entry
```

Phase 7 Local RAG、Web Search Fixture Utility、URL Security、Httpx Fetch、Citation、PersistenceまたはData Controlsを最初から作り直さない。

## 5. Authorized Mutation

- Project Root内でP8-0／P8-Aに直接必要なSource、Test、Frontend、Config、配信Static Artifact。
- `docs/project/phases/phase_8/history/index/`への新規Append-only Recovery。
- `docs/project/phases/phase_8/history/operations/`へのImplementation Freeze／Finding Ledger。
- `docs/project/phases/phase_8/handoffs/`へのExact Return。
- `docs/project/shared/history/automation/`へのCopilot挙動の新規Append-only Evidence。
- 既存`.venv`、既存`frontend/node_modules`を使うFocused／Static／Build。

## 6. Explicitly Forbidden

- Project Root外Read／Write／List／Stat／Temp／Cache／Install。
- Git Read／Mutation、Network、Package Download、Web検索、Real URL Fetch、Provider Memory、User `runtime_data/`、Model Load、Real Browser。
- P8-B〜P8-F、Phase 8 Closure、Phase 9、Roadmap、Backup、Commit／Push。
- General／Automatic Web Search、Search Provider、MCP、External Action、Full Constitution、Agent Level 1完成Claim。

Node v25由来のFrontend環境Failureが出ても、Node／nvmをInstallまたはRoot外探索しない。正確に分類して独立Scopeを継続する。

## 7. Execution

Execution Planの`CP8-01`から`CP8-09`まで順に実行する。各境界でRecovery Indexを作ることは、本TaskではUserがResource 7%を理由に特別指定した必須条件である。

Routine確認、進捗報告または軽微Findingで停止しない。Critical／Major／MVP BlockerだけをReworkし、Minor／HardeningはReturnへ記録する。Resource Hard Stop時はCurrent WUを安全収束し、Stopped-safe Returnを作る。

## 8. Verification／Claim

- Real Networkは`NOT RUN／USER MANUAL GATE`とする。
- Fixture／Mock Transport PASSをReal URL PASSへ昇格しない。
- P8-ACC-001〜012と039を個別評価する。
- P8-ACC-040はP8全体User Manualであり、本TaskではPASS Claimしない。
- Full Canonical SuiteはResourceが十分な場合だけ実施し、不足時はFocused Evidenceを失敗と偽らずClaudeへ渡す。

## 9. Return

Normal End、Resource Stop、Incident Stopのいずれでも次を返す。

1. 最新Recovery Index。
2. Exact Return Handoff。
3. Copilot Automation Evidence。
4. Completed／Partial CPとExact Next CP。
5. Changed Paths、Test、Action Inventory、Open Finding、Temp／Process状態。

Return後はCodex Controller Independent Review待ちで停止し、P8-Bへ進まない。

## 10. Exact Start

```text
Phase 8 Copilot P8-0／P8-A Resource-bounded Implementationを開始する。
```
