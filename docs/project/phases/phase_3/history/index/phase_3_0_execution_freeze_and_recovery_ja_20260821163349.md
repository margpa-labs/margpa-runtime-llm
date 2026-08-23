# Phase 3-0 Execution Freeze／Recovery Entry

```yaml
document_id: phase_3_0_execution_freeze_and_recovery
status: current_recovery_entry
phase: phase_3
subphase: phase_3_0
work_unit: p3_0_wu_003
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_g_wu_004_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 16:33:49 JST
```

Long期戦Mode下のLightweight Recovery Entry（Companion第4.1節適用）。定型§0.0 Boilerplateは省略。

## Current State

```text
Accepted Predecessor : P3-0-WU-001 PASS（Preflight、GO）
Current WU            : P3-0-WU-003 完了 → 次はP3-A-WU-001
Automation Control    : ON（User承認、2026-08-21）
Governance Runtime Mode: off（未変更）
```

## P3-0-WU-002 Baseline（確定・以後の差分比較基準）

```text
Full Test          : 697 passed／3 deselected（60.60s）
Definition Corpus   : 17 Source／18 Definition、全SHA-512一致、JSON Parse 17/17 PASS
                      Corpus Manifest Digest: dc8631643a0d48b272c7ec1c2f99aec5155e40957ec6d0924
                      ce2aaab3ba4fbea930c6ea26c907ba3415cf01e73153287c997942cb312beb572e100d56f21cf7b
                      （Inventory Docと完全一致、Drift 0）
Ruff Format／Check  : PASS（170 files formatted, all checks passed）
Mypy (src/)         : PASS — 117 source files（Phase 2-F Scopeと一致）
Mypy (bare)         : tests/配下に既存11 Error検出（test_conversation_generation.py 3件、
                      test_persistent_web_app.py 8件）。Phase 2-F Scope外・本日変更0・
                      Phase 3 Non-scope（既存Test、audit_evidence／governance_definitions
                      非関連）。Deferred、Non-blocking。
Frontend Build      : PASS
Dirty Tree           : Codex側並行作業Untracked File 2件（DeepSeek関連、Phase 4 Scope）を
                      ユーザーが確認済み。Phase 3 Mutation対象外として分離。
```

## Exact Mutation Manifest（本Freeze自体）

```text
Modified:
  docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md
    （long_running_mode_active: false → true、Activation Timestamp追記）
Created:
  docs/project/phases/phase_3/history/index/phase_3_0_execution_freeze_and_recovery_ja_20260821163349.md
Git Mutation        : 0
Root外Action         : 0
```

## Path Class Freeze（Execution Plan第5節Candidate Write Classから、Phase 3-A以降で使用）

```text
src/margpa_runtime_llm/modules/audit_evidence/**
src/margpa_runtime_llm/modules/governance_definitions/**
src/margpa_runtime_llm/adapters/audit_evidence/**
src/margpa_runtime_llm/adapters/governance_definitions/**
src/margpa_runtime_llm/bootstrap/{audit_evidence,governance_definitions}.py
src/margpa_runtime_llm/web/governance_routes.py（新規）
frontend/src/**（Governance Settings UI、Phase 3-F）
tests/unit/audit_evidence/**, tests/unit/governance_definitions/**
tests/integration/audit_evidence/**, tests/integration/governance_definitions/**
definitions/manifest.json または manifests/<package>.json（Phase 3-C、新規）
docs/project/phases/phase_3/history/**（Append-only）
docs/project/shared/history/automation/**（意味あるCycle Evidenceのみ）
```

## Test Command Freeze

```bash
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/pytest -q
./.venv/bin/ruff format --check src tests
./.venv/bin/ruff check src tests
./.venv/bin/mypy src   # Phase 2-F相当Scope。bare mypyのtests/既存11件は別軸で追跡
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run lint
```

## Forbidden Actions（本Freeze期間中、変更なし）

Git Mutation、Provider Memory、Root外Action、`other/`、User実`runtime_data/`、Phase 3-H以降、Secret／Network／課金——Handoff第4節・Governance第3節のまま。

## Next Exact Route

P3-A-WU-001（Audit Identity／Event Contract）へ進む。
