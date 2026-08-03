# ADR-0027: Public Demo最小公開／制限Hook延期／Runtime交換性

```yaml
document_id: adr_0027_public_demo_minimal_access_and_deferred_control_hooks
status: accepted
language: ja
created_at: 2026-07-30 14:49:21 JST
owner: 設計統括者役
phase: phase_1_ex
supersedes_in_part:
  - adr_0025_public_demo_auto_start_and_pre_release_gate
```

## 1. Context

Lightning Traffic-aware Auto-start、Basic認証、Model Startup、外部Browser利用およびIdle Sleep復帰は実機で成立した。

当初のADR-0025は、匿名Public Demoを公開する前にRate Limit、Generation Budget、Cooldown、Public Token Hard CapおよびCost保護を必須とした。

その後、次の状況が確定した。

- 現在のDemoを見る人数は多くないと見込まれる。
- 主要な閲覧対象者にはすでに動作画面を提示済みである。
- 現在のLightning環境は低性能CPUであり、常時高負荷利用を想定していない。
- Lightning Credit等は現在の運用上、一定周期でResetされる見込みである。
- 制限機構を先に完成させるより、認証なしで試せる最小公開入口を作る価値が高い。
- 高性能Model、Home Serverまたは外部Cloudへの移行が、当初想定より早く発生する可能性がある。

## 2. Decision

既存Basic認証Previewを維持し、認証なしPublic Demoを別Access Profileとして追加する。

Public Demoは、既存Basic PreviewからAuthentication処理を単純削除して作らない。

```text
basic_preview:
  authentication = basic

public_demo:
  authentication = none
  explicit access profile required
```

Public専用Rate Limit、Generation Budget、Cooldown、追加Token Hard CapおよびCost Guardは、Phase 1-ex Public Demoの必須機能から外す。

ただし、将来追加できるConfig／Port Hookを`off`状態で予約する。

## 3. Existing Boundary

Public専用制限を外しても、既存Web Runtimeの次の境界は維持する。

- Request Validation
- Request Body Cap
- Generation Parameter Validation
- Single Worker
- Model Busy
- Cancel／Shutdown
- Safe Error
- Security Header
- 非永続Conversation

既存境界を削除するDecisionではない。

## 4. RAG Decision

Documentation RAGはAccess Profileで分離する。

```text
basic_preview:
  future RAG eligible

public_demo:
  RAG denied
```

Public DemoではRAG AdapterをLoadせず、Client Request、UIまたはConfig Overrideで有効化できない。

Lightning、Home ServerまたはCloudでDocumentation RAGを利用する将来計画は維持するが、Public Demo公開とは別工程とする。

## 5. Runtime Portability Decision

Public Demo実装と同時に、次の交換境界を維持・検証する。

```text
Model Definition
Model Adapter
Deployment Profile
Web Access Profile
Feature Profile
Platform Lifecycle Adapter
```

高性能Model、GPU付きHome Serverまたは外部Cloudへの移行が早期に発生しても、Public／BasicのAccess設計を作り直さずに対応できる構造を完了条件へ含める。

## 6. Risk Acceptance

制限を`off`にする結果、匿名AccessがStudio Wake、Model Load、CPU時間またはCredit消費を発生させる可能性がある。

現時点では利用規模と環境を考慮し、このRiskを受容する。

次の場合は制限機構の優先度を再評価する。

- 想定外のAccess増加
- Credit消費増加
- GPU／高性能Machineへの変更
- 高性能／高コストModelへの変更
- Home Server公開
- External Cloud公開
- Abuse、長時間生成またはAvailability問題

Risk受容は、将来無制限公開を恒久方針とするDecisionではない。

## 7. Consequences

### Positive

- Public Demoを最小工数で提供できる。
- Basic Previewを安全な検証入口として残せる。
- Current UI機能をPublicでも試せる。
- RAGをPrivate／Publicで分離できる。
- Model／Compute／Cloud交換をAccess設計から分離できる。

### Cost／Risk

- 現時点ではPublic専用Rate／Cost保護が動作しない。
- Anonymous AccessによるWake／Credit消費をApplication側で抑止しない。
- 将来高コスト環境へ移行した場合、制限Hookの実装が必要になる可能性が高い。
- Basic／PublicのConfig、Entry PointおよびTestが増える。

## 8. Superseded Scope

ADR-0025のうち、次をPhase 1-ex Public Demo公開前の必須条件から外す。

- Configurable Global Rate Limit
- Configurable Global Generation Budget
- Configurable Cooldown
- Public専用Max New Tokens Hard Cap
- Public専用Cost Guard

ADR-0025の次は維持する。

- Basic Previewとの分離
- Explicit Public Access Mode
- Tool／Agent／External I/Oの非追加
- Prompt／回答の非永続
- Security Header
- Public RAG無効
- Platform操作のユーザーAuthority
- Public化のユーザー明示判断

## 9. External Action Boundary

本ADRは次を許可しない。

- Lightning Public設定変更
- Basic認証解除
- Anonymous URL公開
- Managed Secrets変更
- Model Download
- Home Server／Cloud構築
- Git／GitHub操作

Repository実装完了と設計統括者Review後に、ユーザーが外部環境を手動設定する。

