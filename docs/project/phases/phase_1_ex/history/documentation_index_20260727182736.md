# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727182736
state_at: 2026-07-27 18:27:36 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
supersedes: documentation_index_20260727171845.md
source: lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation
```

本Snapshotは[17:18:45版](documentation_index_20260727171845.md)までの全状態を継承する。

## Added Artifacts

- [Lightning Stage B Unattended Wake Failure／Private Bootstrap Preparation](operations/lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation_20260727182736.md)
- [Current Index Before Change](../../../current/history/index/documentation_index_phase_1_ex_before_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_ja_20260727182736.md)
- [Current Index After Change](../../../current/history/index/documentation_index_phase_1_ex_after_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_ja_20260727182736.md)
- [Phase Index Before Change](operations/phase_index_before_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_20260727182736.md)
- [Phase Index After Change](operations/phase_index_after_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_20260727182736.md)

## Recorded State

```text
Running-Studio Public URL Smoke:
  PASS

First Unattended Wake:
  FAILED

Sleep／Restart Terminal Environment:
  NOT PERSISTED

Project／Model／Environment Artifact:
  PERSISTED

Managed Secrets:
  AVAILABLE／VALUES NOT RECORDED

Runtime State Permission:
  REVALIDATION／LIMITED REPAIR REQUIRED

Private Bootstrap:
  PREPARED／INTERNALLY REVIEWED

Private Bootstrap Repository Inclusion:
  NONE

Private Bootstrap Lightning Validation:
  USER ACTION PENDING

First Wake Retest:
  NOT RUN

Second Unattended Wake:
  NOT RUN

Traffic-aware Auto-start:
  UNCONFIRMED
```

## Important Decisions

- Artifactの永続性と、Terminal Export、Process StateおよびRuntime Permissionの永続性を分離して扱う。
- API BuilderではForeground `run`契約を維持し、その前段でPrivate Bootstrapが起動前提を再構築する。
- Private BootstrapはRepository外Artifactとし、Source全文および正確な起動Commandを公開候補Docsへ保存しない。
- CredentialはManaged Secretsだけから受け取り、値をCode、Docs、StatusまたはRuntime Stateへ保存しない。
- Private BootstrapはOwner、Symlink、Mode、固定Path、PortおよびCredential存在をFail Closedで検査する。
- 内部Review合格だけではTraffic-aware Auto-startを合格にせず、Lightning実機のFirst／Second Wake Evidenceを要求する。

## Verification

```text
Private Bootstrap Ruff:
  PASS

Private Bootstrap Mypy strict:
  PASS

Private Bootstrap Python Syntax:
  PASS

Simulated Bootstrap Tests:
  3 PASS

Existing Lifecycle Unit Tests:
  32 PASS
```

## Integrity

```text
Current Documentation Index:
11c44b5fee55d0e7679263f2cf56972e20f230c0a772aa113d646a4f669534b16615db7cec013394159819f38b5819dd874efb9f9ff45046d6b6c861bab646db

Phase 1-ex Index:
42d5ab86ba1f0d59c060315d65878e430594ee81fd9b0dbea73725c60a4b581f9660c6b1cbdc3d5f591ad7d225631154b8dc945f5ba08933543a1118e8646794

Failure／Bootstrap Preparation Record:
8167427643bcac3f86882914d3132c9b61724dc405ea0bf7e070c8192b64cc8c8a58740ad1073cf430ac64bb44ba7798941c5c25e2dc3918421e9c61cd4eb278
```

## Documentation Validation

```text
Stable／New Record Relative Links Checked:
  259

Missing Links:
  0

Phase Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Current Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Private Bootstrap Source:
  NOT RECORDED

Exact Private Startup Command:
  NOT RECORDED

Public URL／Credential Value:
  NOT RECORDED
```

## Boundary

本Snapshotは、First Unattended Wake Failureの記録と、Repository外Private Bootstrapの内部作成・Review完了までを示す。

Private BootstrapのLightning配置、Preflight、Test、Manual Run、API Builder On-start変更、First Wake再試験、Second Wake、URL持続性、Traffic-aware Auto-start、Public Demo、Git、GitHub、RAG、Phase 1-ex Final Lossless、Final ReviewまたはBackupを完了状態へ変更しない。
