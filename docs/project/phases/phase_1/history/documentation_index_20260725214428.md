# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:44:28 JST`
- 更新日時: `2026-07-25 21:44:28 JST`
- Snapshot: `20260725214428`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725212559.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Pure CPU External Native Acceptance  : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725212559.md](documentation_index_20260725212559.md)を継承する。

前SnapshotのPure CPU Changes RequestedはCorrection実装と独立再Reviewにより解消された。

## 3. Correction Status

[implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md](handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md)

## 4. Accepted Re-review

[designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)

判定：

```text
Pure CPU Profile／Runtime Detection : ACCEPTED
Pure CPU Preflight／Setup           : ACCEPTED
Acceptance Contract Correction      : ACCEPTED
Repository Follow-up                : COMPLETE／ACCEPTED
External Native Acceptance          : PENDING
```

## 5. Resolved Findings

### Acceleration

```text
CUDA GPU                 : cuda
CUDA Build CPU Execution : cpu_native
Pure CPU Build           : none
Mismatch                  : Fail Closed
```

Runtime値を選択Profileの`compute.acceleration_api_key`と照合する。

### Model Selection

```text
Canonical : --model-root
Artifact  : Registry Relative Path
Compat    : --model-path Validation
Download  : none
```

指定Artifactと実際にLoadするArtifactを一致させる。

## 6. Independent Verification

```text
pytest Full Suite : 267 passed, 3 deselected
Pure CPU Targeted : 9 passed, 1 deselected
Ruff              : PASS
Mypy              : PASS
Node Markdown     : 5 passed
Shell Syntax      : PASS
uv lock           : PASS／122 packages
Read-only Plan    : PASS
```

External Native Testは未実施であり、Passとは記録しない。

## 7. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 8. Next Gate

```text
User-run Lightning Read-only Preflight
  → Setup Plan
  → Environment Reconstruction
  → Environment Verification
  → Bounded Native Smoke
  → Result Review
  → Cross-environment Final Review
  → Phase 1 Completion Decision
```

## 9. Scoped Authorization

Repository Correctionは完了した。次の外部Lightning操作はユーザー実行Gateである。

本Indexは外部操作、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 10. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。
