# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725200001.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up      : Accepted／Ready for Implementation
Combined Manual Edge Tests                   : Deferred until Phase 1-I Review
Phase 1-F Lightning Pure CPU Repository Hook : Accepted／Ready for Implementation
Lightning Pure CPU Preflight Addendum        : Accepted／Ready for Implementation
Lightning Environment Reconstruction         : User-run／External Gate
Simple RAG Implementation                    : After Phase 1-ex
Simple RAG Missing docs/ Contract             : Accepted Reservation
Mac Simple RAG                               : Optional Local Implementation
Lightning Simple RAG                         : Hook Only／Default OFF
Top-level Phase 1 Completion                 : Not Declared
Phase 1-ex                                   : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725200001.md](documentation_index_20260725200001.md)を継承し、次を追加する。

- Mac／Lightning共通のSimple RAG `docs/` Availability Contract
- `docs/`不存在時の明示的Unavailable Result
- Lightning Pure CPU Preflightの既存Script拡張方針
- Lightning環境再構築をユーザー実行とする運用境界

## 3. Simple RAG Availability Requirements

[simple_rag_documentation_availability_requirements_20260725201016.md](requirements/simple_rag_documentation_availability_requirements_20260725201016.md)

## 4. Accepted ADR

[adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md](adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md)

## 5. Future Implementer Reservation

[designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md](handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md)

本HandoffはPhase 1-ex完了後用であり、現時点のRAG実装を許可しない。

共通Contract：

```text
Component OFF:
  docs/を探索しない。
  Startup Errorにしない。

Component ON／明示利用＋docs/ missing:
  state=unavailable
  reason_code=docs_directory_missing
  docs/が設置されていないため参照できません。
  index loadなし
  retrievalなし
  additional model callなし
```

## 6. Lightning Pure CPU Preflight Addendum

[designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)

実装担当は既存の`preflight_lightning_ai_studio.sh`を優先的に拡張する。

```text
cuda-gpu  : CUDA Build／GPU Execution
cuda-cpu  : CUDA Build／CPU Execution
cpu-native: Pure CPU Build／CPU Execution
```

既存`--cpu-only`の意味をPure CPUへ変更しない。CPU-native経路では`nvidia-smi`、`nvcc`、CUDA CompilerまたはGPU Allocation Probeを呼び出さない。

## 7. User／Implementer Boundary

### 実装担当

- Preflight Repository実装
- Pure CPU Setup Script
- Profile
- Automated Test
- User-run Command Procedure
- Status Report

### ユーザー

- Lightning Environment Reconstruction
- Project／Model配置
- Setup Command実行
- Native Smoke
- Public Access確認

外部操作の結果をRepository TestだけでPassとみなさない。

## 8. Scoped Authorization

現在実装可能：

- Phase 1-I
- Lightning Pure CPU Repository Follow-up
- Lightning Pure CPU Preflight Addendum

現在実装不可：

- Simple RAG
- Project Documentation Explainer
- 外部Lightning操作
- Model Download
- Phase 1-ex開始
- Git／GitHub操作

## 9. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 10. Next Reports

```text
docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md
docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md
```

Pure CPU StatusにはPreflight Addendumの結果も含める。

## 11. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。
