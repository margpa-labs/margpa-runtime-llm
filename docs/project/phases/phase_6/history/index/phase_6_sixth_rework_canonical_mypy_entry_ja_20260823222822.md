# Phase 6 Sixth Rework — Canonical Mypy再開Entry

```yaml
document_id: phase_6_sixth_rework_canonical_mypy_entry_20260823222822
status: recovery_entry_active
phase: phase_6
rework: sixth_rework_canonical_mypy
owner_role: 設計者兼実装者役
created_at: 2026-08-23 22:28:22 JST
authority: phase_6_codex_sixth_independent_review_canonical_mypy_rework_handoff_ja_20260823222652.md
authority_sha512: 849b27ec1ca95998f2422b92e40f58958eb8184c633f8add36942123ae22747c6f1d0204dc35112b5714a4d2a80ea940c634f556e1221ecb753d9f089fe2f815
previous_candidate: phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_20260823222047.md
phase_closure_state: do_not_close
```

## 1. Current Position

```text
Finding                    : P6-CODEX-045
Severity                   : MAJOR STATIC CONTRACT／REQUIRED
Canonical Mypy Command     : .venv/bin/python -m mypy
Canonical Scope            : src／scripts／tests
Current Result             : 22 errors in 4 files／441 files／Exit 1
Source Contract Failure    : NONE identified at entry
Active Process／Model Load : 0
```

`pyproject.toml`の`files = ["src", "scripts", "tests"]`をCanonical Scopeとする。Fifth Candidateの`mypy src/ scripts/` PASSをCanonical Static Contract PASSと分類した部分はP6-GOV-009でAppend-only訂正する。

## 2. Exact Allowed Test Mutation

```text
tests/unit/inference/test_model_access_coordinator.py
tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
tests/unit/bootstrap/test_repair_live_integration.py
tests/unit/bootstrap/test_judge_live_integration.py
```

Config除外、`Any`化、File-wide Ignore、Assertion／Race／Failure Injection弱体化は行わない。TestをCurrent Production Protocolへ正確に型付けする。

## 3. Task-owned Temporary／Cache

```text
.venv/.t/phase_6_sixth_rework_20260823222822/
  pytest/
  cache/tmp/
  cache/mypy/
  cache/ruff/
```

すべてProject Root内に固定し、自己判断で削除しない。

## 4. Planned Verification

```text
Focused Pytest:
  .venv/bin/python -m pytest <4 exact test files> -q -p no:cacheprovider \
    --basetemp=<task root>/pytest/focused

Canonical Mypy:
  .venv/bin/python -m mypy

Ruff:
  .venv/bin/python -m ruff format --check <4 exact test files>
  .venv/bin/python -m ruff check <4 exact test files>

Backend Full:
  .venv/bin/python -m pytest tests/ -q -p no:cacheprovider \
    --basetemp=<task root>/pytest/backend_full
```

Frontend、実Model、D-1〜D-4、Citation Browser EvidenceはSource／Frontend非変更を照合して再利用し、再実行しない。

## 5. Action Inventory at Entry

```text
Project Root外Action           : 0
Provider Memory Internal Contact: 0
Git Mutation                   : 0
Network Action                 : 0
User runtime_data Contact      : 0
Source／Frontend Mutation      : 0
```

## 6. Exact Next Action

P6-GOV-009 Correctionを新規作成し、4 Test Fileの22 ErrorをCurrent Source Contractへ合わせて最小修正する。Production Source Signature矛盾が露出した場合だけ、新規RecoveryへFindingを記録してからSource範囲を再評価する。

