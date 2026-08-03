# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260730170710
state_at: 2026-07-30 17:07:10 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - handoffs/implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md
  - handoffs/designer_review_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170710.md
supersedes: documentation_index_20260730161108.md
source: public_demo_stateless_preflight_credential_isolation_and_policy_hook_follow_up_review
```

本Snapshotは[2026-07-30 16:11:08版](documentation_index_20260730161108.md)までの全状態を継承する。

Phase Index Stableは今回変更していない。Follow-up実装Status、設計統括者Reviewおよび本IndexをAppend-only Eventとして追加した。

## Added Event Artifacts

- [Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up 実装Status](handoffs/implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md)
- [設計統括者Review：Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up](handoffs/designer_review_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170710.md)

## Review Decision

```text
F1 Stateless Public Preflight:
  RESOLVED／ACCEPTED

F2 Credential Isolation:
  RESOLVED／ACCEPTED

F3 Effective Optional Control Hook:
  RESOLVED／ACCEPTED

Basic Preview Compatibility:
  NO REGRESSION FINDING

Public Demo Repository Implementation:
  ACCEPTED

Lightning Public Demo Manual Trial:
  GO

Anonymous Public Activation:
  USER DECISION AFTER MANUAL TRIAL

Next GitHub／Public Documentation Sync:
  PUBLICATION HYGIENE CORRECTION REQUIRED
```

## Resolved Follow-up

### F1. Stateless Public Preflight

Public Demo PreflightはBasic Preview用Runtime State、PID、Log、Ownership MarkerおよびLifecycle Lockから分離された。

Project、Platform、Python、uv、Web Entrypoint、Deployment Profile、Model Definition、Model Artifact、BindおよびPublic Access Profileの検査は維持されている。

### F2. Credential Isolation

Public DemoはCommon Script読込を含む最初の子Processより前に、Basic Preview用Credential三項目をPublic Script Process内から除外する。

Basic Preview側のCredential契約は変更されていない。

### F3. Effective Optional Control Hook

`PublicControlPolicyPort`はChat Request／Generation Pipelineへ接続された。

Disabled PolicyはResponse、Streaming、Summary、ThinkingおよびCancel挙動を変更しない。

実制限機能は今回追加していない。

## Publication Hygiene Findings

次回GitHub／公開物同期前に、ユーザーの明示承認を伴う処理が必要である。

```text
P1:
  最新実装Statusの1行に、実ユーザーHome由来の絶対Pathが存在する。
  本Indexでは値を複製していない。
  History文書を無断変更していない。

P2:
  Project Rootおよびdocs/に.DS_Storeが各1件存在する。
  本Reviewでは削除していない。
```

P1およびP2はLightning手動試験のBlockerではないが、次回GitHub／公開物同期のGateとする。

## Verification Evidence

設計統括者役が実行した検証：

```text
Changed File SHA-512:
  Implementer Status記載値と6／6一致

Ruff Check:
  PASS

Ruff Format Check:
  PASS／93 files

Mypy:
  PASS／93 source files

Shell Syntax:
  PASS
```

実装Statusに記録されたEvidence：

```text
Targeted Test:
  92 passed

Repository Full Suite:
  331 passed
  3 deselected

Ruff／Mypy／Shell／uv Lock:
  PASS
```

本ReviewではPytestを再実行していない。Status作成時と現在Source／TestのSHA-512が一致し、Test Evidence対象にDriftがないことを確認した。

## Integrity

```text
Previous Documentation Index:
06228203e8dbc3206f79edb53f7c991d78e19053c8e01ef518a2c4038e54df9519be02c8be7dcdddd9441aee1ef120c3c459b9ed57ef39cd340836a815bb229f

Phase Index Stable／Unchanged:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Implementer Status:
e3faa92de5a7f1159bbd858c777ca77cd4da4992221ba2783c185daba75c391772b80ceefe3630626645f4a46c3bf65a876dc26b5ea267bd044f0363b8c9ab0c

Designer Review:
e3e3e675e2301523fed23795abfadf5fa718f5b38206eb95917fcbf21662e7495b59e755dc75623d5595143c8ff4d129755dd022bd008280454cdf37cfa9f4bd
```

## Validation Scope

- Reviewおよび本Indexを新規追加した。
- 既存Docsを上書きしていない。
- Phase Index Stableを変更していない。
- Source、Config、Script、TestおよびModelを変更していない。
- P1の文書を無断修正していない。
- P2の`.DS_Store`を無断削除していない。
- Project Root外へ触れていない。
- Lightning、GitおよびGitHubを変更していない。
- 次はユーザー担当によるLightning Public Demo手動試験である。
