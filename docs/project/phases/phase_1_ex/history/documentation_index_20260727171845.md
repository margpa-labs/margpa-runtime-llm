# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727171845
state_at: 2026-07-27 17:18:45 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
supersedes: documentation_index_20260727131830.md
source: lightning_stage_b_manual_trial_preparation_and_port_7860
```

本Snapshotは[13:18:30版](documentation_index_20260727131830.md)までの全状態を継承する。

## Added Artifacts

- [Lightning Stage B Manual Trial Preparation／Port 7860](operations/lightning_stage_b_manual_trial_preparation_and_port_7860_20260727171551.md)
- [Current Index Before Change](../../../current/history/index/documentation_index_phase_1_ex_before_lightning_stage_b_manual_trial_preparation_ja_20260727171551.md)
- [Current Index After Change](../../../current/history/index/documentation_index_phase_1_ex_after_lightning_stage_b_manual_trial_preparation_ja_20260727171737.md)
- [Phase Index Before Change](operations/phase_index_before_lightning_stage_b_manual_trial_preparation_20260727171551.md)
- [Phase Index After Change](operations/phase_index_after_lightning_stage_b_manual_trial_preparation_20260727171737.md)

## Recorded State

```text
Repository Preparation:
  ACCEPTED

Lightning Artifact Hash:
  PASS

Permission:
  PASS

Managed Secrets Availability:
  PASS／VALUES NOT RECORDED

Stage B Target Test:
  32 PASSED

Runtime State Permission:
  INITIAL FAIL／LIMITED REPAIR／PASS

Preflight:
  PASS

Manual Preview:
  STOPPED

Foreground run:
  PASS

API Builder Port:
  7860

Running-Studio Public URL Smoke:
  PASS／URL VALUE NOT RECORDED

First Unattended Wake:
  NOT RUN

Second Unattended Wake:
  NOT RUN

Traffic-aware Auto-start:
  UNCONFIRMED
```

## Important Decisions

- API BuilderはForeground `run`を使用し、Background `start`を使用しない。
- API Builder Application Portと`MARGPA_WEB_PORT`を同じ`7860`へ統一する。
- `basic-preview.pid`がない状態は、Foreground `run`では正常である。
- Studio稼働中のPublic URL SmokeだけではTraffic-aware Auto-startを合格にしない。
- 次のGateは、Sleeping Studio、Owner Session完全不在、第三者相当Public URL AccessだけによるFirst／Second Unattended Wakeである。

## Integrity

```text
Current Documentation Index:
404fd5b14f044609f1fb2a61e3f48e8120d4dd6120f20c483ee63993c706fef02d87a70c22816c510d3020850e942e42d34404959deef356de802b4fb815a2de

Phase 1-ex Index:
7b09c8cf4562437d8cfa05e61e837a0884d41bdd96f00cc66dc231a51937bf1ed4b48bd39bfd8000ed865d5c4767aafc26f38fb8084bcae8fc9ff6c5ec56c1f2

Stage B Manual Preparation Record:
c27dbe03842532e6654156799b13c5709b45f0938c11c8861dd80b57e3b7078bbf5de9626357a6208dbcf391635914af131a2ac42a6cbc340cfd73dcd65b146a
```

## Validation

```text
Relative Links Checked    : 258
Missing Links             : 0
Old Identity／Private Path : 0
Public URL Value          : absent
Credential Value          : absent
Stable／After Match        : pass
.DS_Store                 : 0 after five-file cleanup
```

## Boundary

本SnapshotはStage B First Unattended Wake直前までを記録する。First／Second Wake、Traffic-aware Auto-start、Git、GitHub、Public Demo、RAG、Phase 1-ex Final Lossless、Final ReviewまたはBackupを完了状態へ変更しない。
