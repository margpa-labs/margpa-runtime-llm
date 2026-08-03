# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260730161108
state_at: 2026-07-30 16:11:08 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - handoffs/implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md
  - handoffs/designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md
  - handoffs/implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md
supersedes: documentation_index_20260730144921.md
source: public_demo_repository_review_and_follow_up
```

本Snapshotは[2026-07-30 14:49:21版](documentation_index_20260730144921.md)までの全状態を継承する。

Phase Index Stableは今回変更していない。実装Status、Review、Follow-up Handoffおよび本IndexをAppend-only Eventとして追加した。

## Added Event／Handoff Artifacts

- [Public Demo Minimal Access／Runtime Portability 実装Status](handoffs/implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md)
- [設計統括者Review：Public Demo Minimal Access／Runtime Portability](handoffs/designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md)
- [実装担当向け Stateless Preflight／Credential Isolation／Policy Hook Follow-up](handoffs/implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md)

## Review Decision

```text
Explicit Web Access Profile:
  ACCEPTED

Basic Preview Compatibility:
  NO REGRESSION FINDING

Model／Deployment／Access Separation:
  ACCEPTED

Public Demo Repository Implementation:
  CHANGES_REQUIRED

Lightning Public Demo Trial:
  NO_GO

Anonymous Public Access:
  BLOCKED
```

## Required Follow-up

### F1. Stateless Public Preflight

Public DemoをBasic Preview用Runtime State、PID、Log、Ownership MarkerおよびLifecycle Lockから完全に分離する。

Project、Environment、Deployment、Model、Artifact、Bind、Public Access Profile、RAG拒否およびControl `off`の検査は維持する。

### F2. Credential Isolation

Public Demoの最初の子Processより前に、Basic Credential三項目をPublic Script Process内から除外する。

`preflight`、Python、uv、その他子Processおよび最終Web ProcessへCredentialを渡さない。

### F3. Effective Optional Control Hook

`PublicControlPolicyPort`を`app.state`へ保存するだけでなく、実際のChat Request／Generation PipelineへInterface経由で注入する。

Disabled Policyでは既存Response、Streaming、Cancel、Summary、ThinkingおよびUI挙動を変更しない。

## Implementation Boundary

実装担当は、Follow-up Handoffに列挙したProject内Source、Script、Testおよび新規Statusだけを変更できる。

次はユーザー担当または今回Scope外である。

```text
Lightning Studio
API Builder
Port
Public URL
Managed Secrets
Upload
Sleep／Wake
Model Artifact
Git／GitHub
Anonymous Public Access
```

Follow-upの実装Statusと設計統括者役のAccepted再Reviewが揃うまで、Lightning Public Demo作業へ進まない。

## Verification Evidence

設計統括者役が実行したRead-only検証：

```text
Implementer Status SHA-512:
  16／16一致

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
  80 passed

Repository Full Suite:
  319 passed
  3 deselected
```

本ReviewではPytestを再実行していない。Status作成時と現在SourceのSHA-512が一致し、Test対象SourceにDriftがないことを確認した。

## Integrity

```text
Previous Documentation Index:
af39087b30c215ea8821d716aaaf88ffae4a4b57beb73ce3f859d68b9d38472dd89ef91a991bb6bb9837caa4a41e5f9983a255c2526111c8069439df8229d579

Phase Index Stable／Unchanged:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Implementer Status:
317647da6344f76fc701b8d67538421115f81fb4bdf554c1f9df50d6c4e4f9422932c3caea58f2c10f78475497254d741caa7bc3a53e9b161a2850c13914cf02

Designer Review:
0a5e2a748894ef06de1cebc35774029dc1063052bf2da6c6d99f2dfedc370bf33eaa74be241fc7489b2260a76337969d9f6a7336a7822ffab454fc558440785a

Follow-up Handoff:
bff453fc1644056a79b3c13756f50ba4eb06ee4ae77d767d031edfe13013c5239393eeb4c19a55acd79ee436de98f9b32efaa09f182563877a187e5c4dcc0719
```

## Validation Scope

- Review、Follow-up Handoffおよび本Indexを新規追加した。
- 既存Docsを上書きしていない。
- Phase Index Stableを変更していない。
- Source、Config、Script、TestおよびModelを変更していない。
- Project Root外へ触れていない。
- Lightning、GitおよびGitHubを変更していない。
- Follow-up完了後は新Timestampの実装Status、再ReviewおよびIndex Snapshotを追加する。
