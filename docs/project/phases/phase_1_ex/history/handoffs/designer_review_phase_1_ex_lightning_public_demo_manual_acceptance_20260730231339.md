# Phase 1-ex Lightning Public Demo Manual Acceptance Review

```yaml
document_id: designer_review_phase_1_ex_lightning_public_demo_manual_acceptance
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-30 23:13:39 JST
owner: 設計統括者役
source_review: designer_review_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170710.md
manual_evidence: ../operations/lightning_public_demo_and_basic_preview_manual_acceptance_20260730231339.md
external_operation_owner: user
supersedes: null
```

## 1. Result

```text
Public Demo Repository:
  ACCEPTED

Lightning Public Demo:
  ACCEPTED

Anonymous Access:
  ACCEPTED

Basic Preview:
  ACCEPTED／PRESERVED

Basic Authentication:
  ACCEPTED

LLM Web Runtime:
  ACCEPTED

Public／Basic Separation:
  ACCEPTED

Rollback Drill:
  NOT_RUN／NON_BLOCKING
```

前ReviewでGOとしたLightning Public Demo手動試験は合格した。

Public DemoとBasic Previewの両方でWeb画面およびLLM動作が成立し、認証なしPublic SurfaceとBasic認証付きPreview Surfaceの分離も確認された。

## 2. Test Procedure Incident

初回Target Testの20件失敗は、Public用`MARGPA_WEB_ACCESS_PROFILE`をTarget Testより先にExportしたManual Procedureの順序不備により発生した。

Basic Preview Test Fixtureが親Environmentを継承し、Public ProfileをBasic Contractとして検査したため、全件が同じ`invalid_profile_contract`で停止した。

Source、Config、SHA-512、転送またはLightning Runtimeの不具合ではない。

訂正方法：

```text
Target Test:
  Public Profile Exportより前に実行

or

Pytest Process:
  env -u MARGPA_WEB_ACCESS_PROFILE
```

Project Fileの修正は不要であり、行っていない。

## 3. Manual Evidence

ユーザー報告：

```text
Public Demo:
  問題なし

Basic認証:
  問題なし

LLM画面:
  問題なし

Cold Start:
  23:01から23:03
  約2分
```

Cold Startは観測値であり、Cache影響を含む可能性がある。保証値にはしない。

Public URL、Credential、Account IDおよび個人識別情報は文書へ保存していない。

## 4. Rollback Decision

Rollback手順は定義済みだが、今回は実行していない。

Prototypeの現在Gateでは非Blockerとする。

Public DemoはAPI BuilderのStop／Disable、Auto-start OFFおよびPublic Link無効化により停止でき、Basic Preview設定は独立して保持されている。

Rollback未実施をPassとは記録せず、`NOT_RUN`として保持する。

## 5. Remaining Boundaries

Public Demoは次の状態を維持する。

```text
Documentation RAG:
  denied

Optional Public Controls:
  all off

Tool／Agent／External Operation:
  not added

Basic Credential:
  not read／not forwarded

Basic Preview Lifecycle State:
  not referenced
```

Publication Hygieneとして前Reviewで検出した次は、次回GitHub／公開物同期前の別Gateとして残る。

```text
Latest Implementer Status:
  実ユーザー由来絶対Path 1件

Project:
  .DS_Store 2件
```

本Manual Acceptance Reviewでは無断修正・削除していない。

## 6. Next Gate

Phase 1-ex Public Demo基盤を完了扱いとし、次工程へ進む。

```text
Next:
  Mac限定簡易Documentation RAG
  External Environment Adapter Hook
```

Public DemoへDocumentation RAGをLoad／Callしない。

Local Macを初期実行対象とし、Basic Previewは将来利用可能な`eligible`境界だけを維持する。Lightning、Home Server、AWS、Azureその他の外部環境は、CoreへHardcodeせず追加Adapterで接続可能なHookとして設計する。
