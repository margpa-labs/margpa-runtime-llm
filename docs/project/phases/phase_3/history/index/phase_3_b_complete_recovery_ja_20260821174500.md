# Phase 3-B Complete／Recovery Entry

```yaml
document_id: phase_3_b_complete_recovery
status: current_recovery_entry
phase: phase_3
subphase: phase_3_b
work_unit: p3_b_wu_003_complete
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_g_wu_004_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 17:45:00 JST
predecessor: phase_3_a_complete_recovery_ja_20260821170500
```

Lightweight Recovery Entry（Companion第4.1節）。

## Current State

```text
Accepted Predecessor : Phase 3-A（完了）
Current WU            : Phase 3-B 完了（WU-001〜003）
Next WU                : P3-C-WU-001（Reference Bundle Manifest／README）
```

## Phase 3-B Summary（Local Append-only Evidence Store）

```text
P3-B-WU-001 Store Root／Scope／Path Safety   : ACCEPTED_LOCAL
P3-B-WU-002 JSONL Append／Receipt／Recovery   : ACCEPTED_LOCAL
P3-B-WU-003 Evidence Store Contract／Regression: ACCEPTED_LOCAL
```

`LocalJsonlEvidenceStore`（`src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py`）を実装。Path Safetyは既存`sqlite_conversation_store.py`のPattern（Symlink拒否・`0o700`Directory・Owner検証・`is_relative_to`によるRoot Containment）を踏襲。Segment Rollover設計（末尾破損Segment検出時は新Segmentへ切替、破損Bytesは非切詰め）を追加設計——Architecture Doc記載の「Crashで末尾にPartial Line」想定に対し、Multi-segment構成でValid Prefixの意味を厳密化した（本SessionのLocal Design判断、Frozen Requirements内）。

Acceptance：Root外Write 0、tmp Fixtureのみ使用（User実`runtime_data/`非接触）、Fault Injection（末尾破損）、Concurrent Append（8 Thread）、Partial Tail非受理・非切詰め、Adapter同値（In-memory／JSONL共通Contract Test）、Absolute Path／Raw Exception非露出——すべてTestで確認済み。

**Port契約修正**：`EvidenceStorePort.read_all`のMethod名を両Adapterで統一（当初`LocalJsonlEvidenceStore`側が`read_valid_prefix`という別名だったため、Contract Test作成時に発覚・是正）。

## Exact Mutation（Phase 3-B累積）

```text
Created:
  src/margpa_runtime_llm/adapters/audit_evidence/__init__.py
  src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py
  tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py
  tests/integration/audit_evidence/test_evidence_store_contract.py
  docs/project/phases/phase_3/history/index/phase_3_b_complete_recovery_ja_20260821174500.md（本File）
Modified:
  tests/unit/audit_evidence/test_identity.py, test_event_contract.py,
  test_canonicalization.py, test_in_memory_evidence_store.py
  （Mypy Strict是正：型注釈追加、不要type:ignore削除、cast追加）
Deleted:
  tests/integration/audit_evidence/__init__.py
  （誤って作成——tests/integration/配下は`__init__.py`を使わない既存慣習と判明し削除）
Git Mutation: 0　Root外Action: 0　User実Data接触: 0
```

## Tests Run／Results

```text
tests/unit/audit_evidence/ + tests/integration/audit_evidence/ : 52 passed
Full Suite                                                      : 749 passed／3 deselected
                                                                    （Baseline 697 + 52 new、Regression 0）
Ruff format／check（Repo全体）                                    : PASS
Mypy（src全体 + audit_evidence Test）                             : PASS — 136 source files
```

## Open Findings

引き続き：Mypy bare（tests/全体）に既存11件Error（Phase 2由来、Phase 3非関連、本Session差分0）。Deferred。

## Forbidden Actions

変更なし。

## Next Exact Route

P3-C-WU-001（Reference Bundle Manifest／README、`definitions/`配下）へ進む。
