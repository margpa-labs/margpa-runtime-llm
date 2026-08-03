# Public Demo Scope Reduction／RAG Separation／Runtime Portability Decision Record

```yaml
document_id: public_demo_scope_reduction_and_runtime_portability_decision
status: accepted
language: ja
created_at: 2026-07-30 14:49:21 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. User Decision

Public Demoの現時点の利用者は多くないと見込まれるため、Rate Limit、Budget、Cooldownおよび追加Cost制限を今回必須にしない。

将来必要になる可能性は残るため、制限機構は無効なHookとして予約する。

既存Basic認証Previewは維持し、Public Demoは別入口として認証なしで作る。

## 2. Feature Separation

```text
Basic Preview:
  Basic Authentication
  将来Documentation RAG利用可能

Public Demo:
  Authentication None
  Documentation RAG強制無効
```

Public Demoは現在のPhase 1 Web機能を原則維持する。以前の設計にあったSummary ModeおよびThinkingのPublic強制無効は今回の必須条件にしない。

## 3. Portability Priority

Model、Cloud、Home ServerおよびCompute環境の交換時期が早まる可能性がある。

実装では次を分離する。

- Model Definition
- Model Adapter
- Deployment Profile
- Web Access Profile
- Feature Profile
- Platform Lifecycle Adapter

Public Demoへ現在のQwen、GGUF、llama.cpp、Lightning CPUまたは固定Pathを直接埋め込まない。

## 4. Accepted Documents

- [ADR-0027](../../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md)
- [Requirements](../../requirements/public_demo_minimal_access_and_runtime_portability_requirements_ja.md)
- [Architecture](../../architecture/public_demo_access_profile_and_runtime_portability_architecture_ja.md)
- [Implementer Handoff](../handoffs/implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md)

## 5. Preservation

ADR-0025、従来Requirementsおよび従来Architectureは削除・上書きしない。

今回の後継文書がPublic専用制限の必須性、Public Feature範囲および早期Runtime交換対応について一部を置き換える。

## 6. External Boundary

本Record作成時点では、実装、Lightning変更、認証解除、Public URL変更、Model変更、Git操作または外部Service変更を行わない。

