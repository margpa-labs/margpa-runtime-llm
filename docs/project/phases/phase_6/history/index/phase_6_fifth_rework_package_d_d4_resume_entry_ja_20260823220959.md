# Phase 6 Fifth Rework — Package D D-4 Final Verification再開Entry

```yaml
document_id: phase_6_fifth_rework_package_d_d4_resume_entry_20260823220959
status: recovery_entry_resume
phase: phase_6
package: package_d
material_boundary: d_4_final_verification_resume
owner_role: 設計者兼実装者役
created_at: 2026-08-23 22:09:59 JST
authority: phase_6_codex_controller_package_d_d4_final_verification_authority_ja_20260823220803.md
authority_sha512: e6d97e964d52b8c1606f94a52f0e1dc3f61b5df011beb7a6a3930f2fa3d898f0aa61bc6a391f9d6af1c39fa293259d5d3957e2bc2c8fc558d7f524f71ac22796
previous_entry: phase_6_fifth_rework_package_d_stopped_safe_provider_memory_metadata_contact_ja_20260823220510.md
phase_closure_state: do_not_close
```

## 1. Resume State

```text
D-1 Governance／Evidence Correction : COMPLETE
D-2 Acceptance 84-ID Rederivation  : COMPLETE
D-3 Real Model Runtime Matrix      : COMPLETE（20／20 PASS）
D-4 Final Verification             : RESUMED／NOT YET EXECUTED
Active Process by this Task        : 0
Active Model Load                  : 0
Source／Test Mutation in D-4       : 0
```

Package A〜CおよびD-1〜D-3を再実行しない。既知のExact Targetだけを使用し、Project Root全体の再Inventoryを行わない。

## 2. P6-CODEX-043 Controller Disposition

```text
Classification                      : INCIDENTAL_PARENT_ENUMERATION
Direct .claude Targeting            : 0
Internal Traversal／Content Read     : 0
Write／Delete／Repair／Execute       : 0
Semantic Use as Authority／Recovery : 0
Current Technical Impact            : NONE
Current Transition Impact           : NONE
Disposition                         : RECORDED／REVIEWED／NON-BLOCKING
```

Provider Memory内部Accessは引き続き禁止する。P6-CODEX-043はProvider Memory Contact Countへ加算しない。

## 3. Task-owned D-4 Temporary Root

```text
.venv/.t/phase_6_fifth_rework_d4_20260823220959/
  pytest/
  cache/
  logs/
```

Test Temporary、Python／Ruff／Mypy Cacheおよび必要なLogは上記Project Root内Pathへ固定する。自己判断で削除せず、Final ReturnでCleanup Gateへ渡す。

## 4. Exact Verification Commands

Environment共通:

```text
TMPDIR=<Project Root>/.venv/.t/phase_6_fifth_rework_d4_20260823220959/cache/tmp
PYTHONDONTWRITEBYTECODE=1
RUFF_CACHE_DIR=<Project Root>/.venv/.t/phase_6_fifth_rework_d4_20260823220959/cache/ruff
MYPY_CACHE_DIR=<Project Root>/.venv/.t/phase_6_fifth_rework_d4_20260823220959/cache/mypy
```

Planned Commands:

```text
.venv/bin/python -m pytest tests/ -q -p no:cacheprovider \
  --basetemp=.venv/.t/phase_6_fifth_rework_d4_20260823220959/pytest/backend_full

.venv/bin/python -m pytest \
  tests/unit/runtime_model_control/ \
  tests/unit/runtime_governance/ \
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py \
  tests/integration/web/test_runtime_model_control_mutation_routes.py \
  tests/integration/conversation/test_persistent_citation_evidence.py \
  tests/integration/web/test_persistent_web_app.py \
  -q -p no:cacheprovider \
  --basetemp=.venv/.t/phase_6_fifth_rework_d4_20260823220959/pytest/focused

.venv/bin/python -m ruff format --check src/ scripts/ tests/
.venv/bin/python -m ruff check src/ scripts/ tests/
.venv/bin/python -m mypy src/ scripts/
.venv/bin/python -m mypy src/ scripts/ tests/

npm run typecheck
npm run lint
npm run test
npm run build
```

`pyproject.toml`の既定Marker `not model_smoke`に従い、Backend Fullは実Hardware Testを除外する。実ModelはD-3のCurrent CPU Fallback MatrixとPackage B／Cの既存Evidenceを照合し、無意味に再実行しない。

## 5. Acceptance Targets

```text
P6-ACC-007:
  D-3 Conversation／Regenerate／Branch Selectと、Citation永続・復元・非破壊の
  Web／Persistence Integration Testを組み合わせて再導出する。

P6-ACC-058:
  USER_MANUAL_ACCEPTANCE_GATE。Technical Complete CandidateのBlockerにしない。

P6-ACC-077:
  HISTORICAL_NONCONFORMANCE_RECORDED。PASSへ変更しない。
```

## 6. Action Inventory at Resume

```text
Package D Cumulative Root-outside Action: 1 known incident（P6-CODEX-042）
Current D-4 Cycle Root-outside Action: 0
Root-outside Persistent Artifact: 0 known
Provider Memory Internal Contact: 0
Git Mutation: 0
External Network Action: 0
User runtime_data Contact: 0
```

## 7. Exact Next Action

上記Task-owned Directoryを作成し、Backend Fullから順にD-4 Verificationを実行する。通常Failureは最小範囲で修正して再検証する。Open Technical Critical／Major 0、D-4一式PASS、P6-ACC-007成立の場合は、P6-ACC-058／077を指定DispositionのままFifth Rework Complete Candidateへ進める。Phase 6 Closureへは進まない。

