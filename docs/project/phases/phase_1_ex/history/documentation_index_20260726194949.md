# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260726194949
state_at: 2026-07-26 19:49:49 JST
status: historical_reconstructed
snapshot_of: ../phase_index_ja.md
supersedes: documentation_index_20260726192912.md
reconstruction_source: recorded_patch_sequence
reconstruction_fidelity: exact_logical_state_with_history_relative_links_rebased
```

本Snapshotは[19:29:12版](documentation_index_20260726192912.md)までの全状態を継承する。

## Added at this Snapshot

- [ADR-0026 Lightning Basic Preview Lifecycle／Managed Secrets](../adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [実装担当向け Lightning Basic Preview Lifecycle Scripts Handoff](handoffs/implementer_handoff_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726194949.md)

## Active Implementation Boundary

```text
許可:
  Project-side Read-only Preflight
  Platform-side Manual Checklist
  Repository内Basic Preview Lifecycle Script
  関連Test

対象外:
  Public Demo本体
  匿名Access
  RAG
  Dependency変更
  Lightning側File配置
  Secret／Hook／Port設定
  Platform変更
  Git操作
```

## Remaining Phase 1-ex Scope

17:53:18版の12項目を維持する。
