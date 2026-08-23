# Phase 3-C Complete／Recovery Entry

```yaml
document_id: phase_3_c_complete_recovery
status: current_recovery_entry
phase: phase_3
subphase: phase_3_c
work_unit: p3_c_wu_004_complete
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_g_wu_004_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 19:15:00 JST
predecessor: phase_3_c_wu001_recovery_ja_20260821182000
```

Lightweight Recovery Entry（Companion第4.1節）。Phase 3-C全体（WU-001〜004）を1件に統合（ADR-3-012準拠、Artifact乱造回避）。

## Current State

```text
Accepted Predecessor : Phase 3-C-WU-001（完了）
Current WU            : Phase 3-C 完了（WU-001〜004）
Next WU                : P3-D-WU-001（Trusted Adapter Registry）
```

## Phase 3-C Summary（Definition Package／Provider／Repository State）

```text
P3-C-WU-001 Reference Bundle Manifest／README         : ACCEPTED_LOCAL（前Entry記録済み）
P3-C-WU-002 Provider Contract／Empty Provider          : ACCEPTED_LOCAL
P3-C-WU-003 Filesystem Provider／Manifest Loader        : ACCEPTED_LOCAL
P3-C-WU-004 Repository State／Quarantine Policy         : ACCEPTED_LOCAL
```

**WU-002**：`DefinitionProviderPort`（`describe／load_package`）、State軸4種（Provider／Package／Source／Definition、architecture§5.3準拠で分離）、`EmptyDefinitionProvider`実装。`definitions=0`を`EMPTY`という正式State（`UNAVAILABLE`/`FAILED`と区別）として扱うことをTestで確認。

**WU-003**：`FilesystemDefinitionProvider`実装。既存`sqlite_conversation_store.py`のPath Safety Patternを踏襲（Symlink拒否・Root Containment・`..`/絶対Path拒否）。実`definitions/`Corpus（17 Source）に対するIntegration Testで全件`SourceState.LOADED`を確認。

**WU-004**：`resolve_package_state`／`resolve_definition_states`（Partial Acceptance Policy）を実装。設計判断（Local Judgment）：
- Package-level `QUARANTINED`は「Manifest自体のDigest不一致」または「Source側のStructural Violation（Path不正等）」という**Package全体の信頼性問題**にのみ発動。
- 通常のDigest／Size Mismatch（1 Source破損）は、そのDefinitionだけを`INVALID`にし、Package自体は`VALIDATED`のまま維持——Valid Sibling保持（Acceptance要件）。
- `KNOWN_SCHEMA_IDS`（Reference Bundle 3 Adapter Class）外のSchema IDは`DefinitionState.UNSUPPORTED`。Trusted Adapter Registry未実装（Phase 3-D）を見越した前方互換的Guard。

Acceptance：Unknown Schema=`unsupported`、Digest Mismatch=`invalid`（Sibling保持でPackageは`validated`維持）、Structural Violationのみ`quarantined`、Emptyへの Silent変換0（Verification欠落時は`INVALID`、無言で0件Empty扱いしない）——すべてTestで確認済み。

## Exact Mutation（Phase 3-C累積、WU-002〜004分）

```text
Created:
  src/margpa_runtime_llm/modules/governance_definitions/domain/states.py
  src/margpa_runtime_llm/modules/governance_definitions/domain/errors.py
  src/margpa_runtime_llm/modules/governance_definitions/domain/source_verification.py
  src/margpa_runtime_llm/modules/governance_definitions/domain/repository_policy.py
  src/margpa_runtime_llm/modules/governance_definitions/ports.py
  src/margpa_runtime_llm/modules/governance_definitions/application.py
  src/margpa_runtime_llm/adapters/governance_definitions/__init__.py
  src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py
  tests/unit/governance_definitions/test_empty_provider.py
  tests/unit/governance_definitions/test_filesystem_provider.py
  tests/unit/governance_definitions/test_repository_policy.py
  tests/integration/governance_definitions/test_filesystem_provider_real_bundle.py
  docs/project/phases/phase_3/history/index/phase_3_c_complete_recovery_ja_20260821191500.md（本File）
Modified:
  src/margpa_runtime_llm/modules/governance_definitions/domain/__init__.py（累積Export追加）
Deleted: NONE
Git Mutation: 0　Root外Action: 0　User実Data接触: 0
```

## Tests Run／Results

```text
tests/unit/governance_definitions/ + tests/integration/governance_definitions/ : 35 passed
Full Suite                                                                       : 784 passed／3 deselected
                                                                                    （Baseline 697 + 87 new、Regression 0）
Ruff／Mypy（Repo全体）                                                            : PASS — 145 source files
```

## Open Findings

引き続き：Mypy bare（tests/全体）に既存11件Error（Phase 2由来、Phase 3非関連、本Session差分0）。Deferred。

## Forbidden Actions

変更なし。

## Next Exact Route

P3-D-WU-001（Trusted Adapter Registry）へ進む。
