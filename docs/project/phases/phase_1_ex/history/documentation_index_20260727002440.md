# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727002440
state_at: 2026-07-27 00:24:40 JST
status: current_snapshot
snapshot_of: ../phase_index_ja.md
supersedes: documentation_index_20260726235422.md
source: designer_review
```

本Snapshotは[23:54:22版](documentation_index_20260726235422.md)までの全状態を継承する。

## Added at this Snapshot

- [Lightning Basic Preview Manual Lifecycle Accepted Review](handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Phase Index：変更前原文](operations/phase_index_before_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Phase Index：変更後原文](operations/phase_index_after_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)

```text
Phase Index Before SHA-512:
  382bdf533bb3edd0b95dd713c53eb0b7e07d5c803328d8a820569dd35957f3f9c9209f132e13e6371709f1d245e8e413da9c303bfc8f1673faac4ba94bd3cc82

Phase Index After SHA-512:
  ddc3b2c9fabe6a59e36e3a3ce65d3830d231224e534c25152cf43743fbc8f4010a3110c91a61bfb245473dda56866b5e041c5fe11a87c48725843a164d800c8c

Accepted Review SHA-512:
  037a5802521782e33530390a90ce382205c44e16a1ca6a18c7184ae9599182440d9eff6426f6e6484bf7a1716c3a91ea6c38a1d4f6a8b5688bd6ab45464621c9
```

## Index Snapshot Chain

```text
documentation_index_20260726150349.md
  → documentation_index_20260726154009.md
  → documentation_index_20260726170034.md
  → documentation_index_20260726175318.md
  → documentation_index_20260726180711.md
  → documentation_index_20260726192912.md
  → documentation_index_20260726194949.md
  → documentation_index_20260726202036.md
  → documentation_index_20260726202935.md
  → documentation_index_20260726203948.md
  → documentation_index_20260726213429.md
  → documentation_index_20260726233910.md
  → documentation_index_20260726235422.md
  → documentation_index_20260727002440.md
```

## Current Acceptance State

```text
Linux /proc Test Fixture Repository Review:
  ACCEPTED

Lightning Linux Lifecycle Test:
  PASS／30

Lightning Managed Secrets／Basic Preview Preflight:
  PASS

Lightning Basic Preview Manual Lifecycle:
  ACCEPTED

Start／Status／Health／External Authentication／Generation／Restart／Stop:
  PASS

Traffic-aware Auto-start:
  NOT_DECIDED

Anonymous Public Demo:
  DISABLED
```

## Low-priority Observation

正常Stop完了時にも`state_cleanup=stale_pid_file_removed`と表示される。機能上の異常ではないが、将来のObservability表示改善候補である。

## Active Gate

Lightning Basic Previewの必須Manual Lifecycle Gateは完了した。次はAuto-start Go／No-Go判定またはPhase 1-exの次の承認済みScopeへ進む。
