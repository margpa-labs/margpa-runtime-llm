# P6-GOV-009 — Canonical Mypy Scope訂正

```yaml
document_id: phase_6_gov009_canonical_mypy_scope_correction_20260823222822
status: append_only_correction_active
phase: phase_6
finding_id: P6-CODEX-045
governance_id: P6-GOV-009
owner_role: 設計者兼実装者役
created_at: 2026-08-23 22:28:22 JST
authority: phase_6_codex_sixth_independent_review_canonical_mypy_rework_handoff_ja_20260823222652.md
supersedes_by_correction_only:
  - phase_6_fifth_rework_package_d_final_verification_ja_20260823222047.md
  - phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_20260823222047.md
```

## 1. Correction Scope

既存Fifth Rework Recovery／HandoffはAppend-only Historyとして改変しない。本書がCanonical Mypy Scope分類だけを訂正する。

## 2. Withdrawn Classification

次の分類を撤回する。

```text
`mypy src/ scripts/`が279 files／0 issuesであることをもって、
Canonical／正本Static ContractがPASSしたとする分類。

`mypy src/ scripts/ tests/`の22 Errorを、Canonical Completionの
Non-blockingな既知Test型Gapとして分離する分類。
```

`mypy src/ scripts/`の実行結果そのものは事実だが、Canonical Scopeの代替にはならない。

## 3. Correct Canonical Contract

Repository正本`pyproject.toml`は次を定義している。

```toml
[tool.mypy]
strict = true
files = ["src", "scripts", "tests"]
```

したがってCanonical Command／Scopeは次である。

```text
Command : .venv/bin/python -m mypy
Scope   : src／scripts／tests
Fifth Candidate時点:
  Found 22 errors in 4 files (checked 441 source files)
  Exit Code: 1
Static Contract at Fifth Candidate: FAIL
```

## 4. Required Repair State

Sixth Reworkでは、Exact 4 Test FileをCurrent Production Contractへ正確に型付けし、次を成立させる。

```text
.venv/bin/python -m mypy
  441 files／0 errors／Exit 0
```

Config除外、`Any`化、Assertion弱体化、File-wide Ignoreによる見かけのPASSは禁止する。

## 5. Governance Effect

```text
P6-CODEX-045 at entry : OPEN／MAJOR STATIC CONTRACT
Fifth Candidate       : ADJUST_REQUIRED
Phase 6 Closure       : NOT AUTHORIZED
Technical Source Claim: Production Source矛盾は現時点で未検出
```

修復結果はSixth Rework Completion Recovery／HandoffへAppend-onlyで記録する。本Correctionは過去Errorの不存在を主張せず、Fifth CandidateのStatic判定だけを正確に訂正する。

