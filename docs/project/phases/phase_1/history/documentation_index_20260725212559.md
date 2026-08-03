# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725201016.md`

## 1. Current Position

```text
Phase 1-G Minimal Web Surface                  : Complete／Accepted
Phase 1-H Summary Mode／UI Language            : Complete／Accepted
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Combined Manual Edge Tests                     : Passed
Phase 1-F Pure CPU Profile／Preflight／Setup    : Implemented
Phase 1-F Pure CPU Native Acceptance Contract  : Changes Requested
Phase 1-F Pure CPU External Native Validation  : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725201016.md](documentation_index_20260725201016.md)を継承し、次を追加する。

- Phase 1-I Repository Review
- Mac Web Manual Acceptance結果
- Phase 1-I Accepted
- Phase 4 Markdown／Code Snippet／Busy UX予約
- Pure CPU Repository Review
- Pure CPU Native Acceptance Correction Handoff

## 3. Implementer Status

- [implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md](handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md)
- [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)

## 4. Phase 1-I Review

[designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md](handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md)

判定：

```text
Repository Implementation : ACCEPTED
Mac Manual Acceptance     : ACCEPTED
Security Boundary         : ACCEPTED
Phase 1-I                 : COMPLETE／ACCEPTED
```

Manual PASS：

- User／Assistant Copy
- UI／Response Language
- Summary
- New Chat Context Reset
- New Chat during Generation
- Stop during Summary
- Reload
- Multi-tab Busy
- Thinking Dependency
- Thinking／Final Separation
- Completion Markdown

## 5. Phase 1-I Deferred Presentation

Phase 4へ延期する。

- Streaming中の段階的Markdown
- Markdown Table
- Code Snippet Language Label
- Assistant本文／Code Block分離
- Code Block個別Copy
- Syntax Highlight候補
- Busy具体Message／汎用Statusの二重表示整理

Current Streaming Plain Text／Completion Markdownは設計どおりであり、Phase 1-I Failureではない。

## 6. Pure CPU Review

[designer_review_phase_1f_pure_cpu_repository_20260725212559.md](handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md)

判定：

```text
Profile／Preflight／Setup Direction : ACCEPTED
Native Acceptance Contract         : CHANGES REQUESTED
External Native Acceptance         : PENDING
Overall Pure CPU Follow-up          : NOT YET ACCEPTED
```

## 7. Pure CPU Blocking Finding

新Pure CPU ProfileとRuntimeは次を使う。

```text
acceleration_api = none
```

Native Acceptance ScriptのCPU Branchは次を固定している。

```text
acceleration_api = cpu_native
```

正しいPure CPU Runtimeでも`runtime_evidence_matches_profile`がFalseになるため、LightningへUpload／再構築する前に修正する。

また、Setupの`--model-path`は実際にはExpected Model Root Layoutを前提とするため、Option Contractを明確化する。

## 8. Correction Handoff

[designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)

次の実装者Statusを要求する。

```text
docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_YYYYMMDDHHMMSS.md
```

## 9. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Phase 1-I／Pure CPU Targeted   : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Node Safe Markdown             : 5 passed
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

Mac Model Smokeを追加実行した時点では、既存Web Runtimeが同じQwen ModelをMemory Mapしており、二重Context作成が失敗した。ユーザーのWeb実生成は合格しているため回帰とは断定せず、Phase 1 Final GateでWeb Runtime停止後に再実行する。

## 10. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 11. Next Gate

```text
Pure CPU Acceptance Correction
  → Implementer Status
  → Designer Review
  → User-run Lightning Rebuild／Native Test
  → Cross-environment Final Review
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
```

## 12. Scoped Authorization

Correction Handoffに記載したRepository修正へ着手可能である。

次は自動許可しない。

- 外部Lightning操作
- Model Download
- Git／GitHub
- Phase 1 Completion宣言
- Backup
- Phase 1-ex開始
- Simple RAG実装

## 13. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。
