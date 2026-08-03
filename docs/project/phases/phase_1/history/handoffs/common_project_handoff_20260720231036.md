# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 23:10:36 JST
supersedes: common_project_handoff_20260720222402.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex                     : Accepted Reservation／Not Started
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Current Role Model             : Unchanged
Current Git State              : Not Initialized
Current Docs Layout            : Unchanged
```

## 2. Model Decision

```text
Guard Canonical : Qwen/Qwen3Guard-Gen-0.6B
Guard Local     : DevQuasar GGUF Q8_0を維持
Judge Canonical : AtlaAI/Selene-1-Mini-Llama-3.1-8B
Judge Local     : bartowski GGUF Q5_K_Mを維持
Official Weight : Download Deferred
```

Canonical SourceとDeployment Artifactを分離する。Seleneは日本語未保証のExperimental Judgeであり、唯一のJudgeへ固定しない。

## 3. Phase 1-ex Reservation

- 現設計者役をPhase 1-exで設計統括者役へ変更
- Phaseごとの設計者役配置を可能にする
- 設計統括者役／設計者役／実装者役／対外Docs役の権限再整理
- Git運用へ移行
- Git移行後のDocs運用を定義
- Docs Directory Structureを変更
- 移行完了後に各担当Taskへ通知
- Phase単位Lossless Compilationを導入
- Public Docsを対外Docs役がPhase完了ごとに更新

現在は予約だけで実行しない。

## 4. Lossless Rule

運用、共通ルール、Handoff、Requirements、ADR、Authorization Boundary等は要約・意訳・再解釈せず、Source本文をそのまま再整理する。

Source File、State、Size、SHA-512をManifest化し、統合文書から再抽出したPayloadが元SourceとByte単位で一致することを検証する。不一致時はFail Closedとする。

README等の説明用Derived Docsは編集可能だが、Canonical Compilationの代替にしない。

## 5. Public Docs Reservation

```text
README.md                              # 日本語敬語＋末尾English Abstract
LICENSE                                # 英語公式原文可
docs/public/overview_ja.md             # 日本語
docs/public/concept_ja.md              # 日本語
docs/public/roadmap_ja.md              # 日本語
docs/public/phases/phase_<id>_summary_ja.md
```

READMEへ何を作っているか、現在動く範囲、Phase Roadmap、Lightning公開URL、Setup、Model、Governance、Limitations、License等を記載する。

## 6. Current Entry Points

- [Documentation Index](../documentation_index_20260720231036.md)
- [Phase 1-ex Requirements](../requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md)
- [Lossless Compilation Requirements](../requirements/lossless_phase_document_compilation_requirements_20260720231036.md)
- [Public Docs Architecture](../architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md)
- [Current Model Strategy](../architecture/model_strategy_20260720231036.md)
- [ADR-0016](../adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md)
- [ADR-0017](../adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md)

## 7. Immediate Next Gate

Phase 1-exへ移らず、現在のPhase 1-F Review、Lightning Native Verification、User Manual、User Acceptance、Phase 1完了Gateを先に進める。

## 8. Authorization Boundary

本HandoffはModel Download、Role変更、Task作成、Git操作、Directory変更、Docs Compilation、Public Docs生成、Lightning操作、Backup、GitHub公開を許可しない。
