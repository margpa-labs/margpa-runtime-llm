# Phase 6 Codex Sixth Independent Review — Canonical Mypy Exact Rework Handoff

```yaml
document_id: phase_6_codex_sixth_independent_review_canonical_mypy_rework_handoff_20260823222652
status: adjust_required_active_on_receipt
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-23 22:26:52 JST
source_handoff: phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_20260823222047.md
independent_review_result: adjust_required
finding_id: P6-CODEX-045
closure_state: do_not_close
rework_scope: test_typing_only_unless_test_reveals_source_contract_failure
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Decision

Fifth Rework Complete Candidateを現時点では受理しない。

D-4は`mypy src/ scripts/`をPASSとし、`mypy src/ scripts/ tests/`の22 Errorを「既知Test型Gap」「Production／Script正本Scopeと分離」と分類した。しかし、Repository正本の`pyproject.toml`は次を明示している。

```toml
[tool.mypy]
strict = true
files = ["src", "scripts", "tests"]
```

したがって、引数なしCanonical Commandである`.venv/bin/python -m mypy`の正本Scopeは`src／scripts／tests`であり、Current ResultはExit 1である。22 ErrorがD-4以前から存在することは、Phase 6 Closure時のCanonical Static Check FailureをNon-blockerへ変更する根拠にならない。

## 2. Independent Reproduction

ControllerがProject Root内Task専用Cacheを使用し、次を再実行した。

```text
Command:
  TMPDIR=<Project Root>/.venv/.t/phase_6_controller_independent_review_20260823222500/tmp
  MYPY_CACHE_DIR=<Project Root>/.venv/.t/phase_6_controller_independent_review_20260823222500/mypy
  PYTHONDONTWRITEBYTECODE=1
  .venv/bin/python -m mypy

Result:
  Found 22 errors in 4 files (checked 441 source files)
  Exit Code: 1
```

対象：

```text
tests/unit/inference/test_model_access_coordinator.py                         12
tests/unit/runtime_observability/test_local_filesystem_recording_writer.py    1
tests/unit/bootstrap/test_repair_live_integration.py                          6
tests/unit/bootstrap/test_judge_live_integration.py                           3
Total                                                                         22
```

## 3. Finding

### P6-CODEX-045 — Canonical Mypy Scope Failure

判定：`MAJOR STATIC CONTRACT／REQUIRED`。

Current Errorは、Event wait Callableが`bool`を返すこと、MonkeyPatch引数型欠落、Module内部Importへの型上の非公開Access、Optional narrowing不足、metadata typeの過広定義、Test DoubleのSignature型欠落、既に絞り込まれたLiteralへの非重複比較等である。

SourceのProduction Contract変更を必要とするEvidenceは現時点でない。4 Test Fileの型をCurrent Source Contractへ正確に合わせる最小Reworkを行う。

## 4. Mandatory Reading

1. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_final_verification_ja_20260823222047.md`
2. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_20260823222047.md`
3. `pyproject.toml`の`[tool.mypy]`。
4. 本Handoff。

開始時に`history/index/phase_6_sixth_rework_canonical_mypy_entry_ja_<timestamp>.md`を新規作成する。

## 5. Exact Allowed Mutation Scope

原則として次の4 Test Fileだけを変更する。

```text
tests/unit/inference/test_model_access_coordinator.py
tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
tests/unit/bootstrap/test_repair_live_integration.py
tests/unit/bootstrap/test_judge_live_integration.py
```

加えて、次の新規Append-only Docsだけを許可する。

```text
docs/project/phases/phase_6/history/index/phase_6_sixth_rework_*.md
docs/project/phases/phase_6/history/operations/phase_6_gov009_canonical_mypy_scope_correction_*.md
docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_sixth_rework_complete_candidate_handoff_*.md
```

Testを正しく型付けした結果、Production Source Signature自体の矛盾が露出した場合だけ、Source Mutation前にRecovery EntryへExact Findingと必要Pathを記録する。単にMypyを通すためのSource緩和、`Any`化、Global Ignore、Config除外は行わない。

## 6. Required Corrections

### Model Access Coordinator Tests

- `threading.Event.wait`を`Callable[[], None]`へ直接渡さず、待機後に`None`を返す型付きHelperを使う。
- `pytest.MonkeyPatch`等のFixture引数へ型を付ける。
- Moduleの非公開`threading`属性を型上直接参照せず、Current Test意図を維持する安全なMonkeyPatch方法へ変更する。
- `INTERNAL_TASK_PREEMPTION_FAILED`へ既にLiteral narrowingされた後の`is not MODEL_BUSY`冗長比較を削除するか、型上重複しない形へ整理する。Test意味を弱めない。
- Thread Race／Preemption／Shutdownの挙動を変えない。

### Recording Writer Test

- `metadata_fields`を`SafeRecordingEnvelope`のExact value unionへ合わせる。
- 広い`object`を型Ignoreで押し込まない。

### Repair／Judge Tests

- Test Double、MonkeyPatch対象、callback、request／cancellationへCurrent Protocolと一致する型を付ける。
- Optional結果は1回取得して`assert result is not None`後に参照し、Repeated Optional CallでNarrowingを失わない。
- Unused Ignoreを除去し、必要なIgnoreを追加して隠さない。
- Runtime挙動、Assertion、Failure Injectionを弱めない。

## 7. Governance／Evidence Correction

既存D-4 Recovery／Handoffを直接編集しない。新規Append-only `P6-GOV-009` Correctionを作成し、次を記録する。

```text
撤回:
  `mypy src/ scripts/`をCanonical／正本ScopeのPASSとする分類。

訂正:
  pyproject.tomlのfiles設定により、引数なしCanonical Mypy Scopeは
  src／scripts／tests。Fifth Candidate時点は22 Error／Exit 1。

修復後:
  Canonical `.venv/bin/python -m mypy` 441 files／0 errorsを要求。
```

## 8. Required Verification

Project Root内Task専用Temporary／Cacheを使い、次を実行する。

1. 4 Test FileのFocused Pytest。
2. `.venv/bin/python -m mypy`を引数なしで実行し、441 files／0 errors／Exit 0。
3. Ruff Format Check／Ruff Checkを4 Test Fileへ実行。
4. Backend Fullを実行し、既存1560 passed／6 deselected以上、Regression 0。

Test-only型修正のため、Frontend、実Model Matrix、D-1〜D-4、Citation Browser Evidenceを再実行しない。既存EvidenceをSource／Frontend非変更と照合して再利用する。

## 9. Completion Contract

次を新規作成する。

1. `history/index/phase_6_sixth_rework_canonical_mypy_complete_ja_<timestamp>.md`
2. `history/operations/phase_6_gov009_canonical_mypy_scope_correction_ja_<timestamp>.md`
3. `handoffs/phase_6_codex_designer_implementer_sixth_rework_complete_candidate_handoff_ja_<timestamp>.md`

Returnに次を含める。

```text
Canonical Mypy: <files count>／0 errors／Exit 0
Focused Pytest: <exact>
Backend Full: <exact>
Ruff: <exact>
Exact changed/new files
Source／Frontend／Real Model semantic mutation: 0
Project Root外Action: 0 in this Rework
Provider Memory Internal Contact: 0
Git／Network／User runtime_data: 0
Open Technical Critical／Major: 0
Next Action: Controller Independent Re-review
```

Phase 6 Closure、Current／Roadmap、Git、Backup、Temporary CleanupまたはPhase 7へ進まず、Controllerへ直接返して停止する。

## 10. Prohibitions

- Mypy ErrorをConfig除外、`ignore_errors`、File-wide Ignore、無根拠な`Any`で消さない。
- Assertion、Race、Failure Injectionを削除・緩和しない。
- Project Root外、Provider Memory、User runtime_data、Network、Gitへ触れない。
- Task-owned Temporaryを自己判断で削除しない。
- Existing History／Evidenceを直接改変しない。
