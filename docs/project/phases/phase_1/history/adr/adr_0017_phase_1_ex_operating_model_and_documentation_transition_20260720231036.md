# ADR-0017 Phase 1-exにおける役割・Git・Documentation運用再整備

- 文書ID: `adr_0017_phase_1_ex_operating_model_and_documentation_transition`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. Context

長期Codex Taskでは、会話量、要約継承、新旧Decision混在、Review対象肥大化により、設計精度と引き継ぎ精度の運用Riskが増える。

ただし現在の設計者役を即時に変更せず、Phase 1-ex「運用再整備」で役割、Git、Docs、Directory、通知を一体的に再設計する。

## 2. Decision

Phase 1-exで次を実施する予約をAcceptedとする。

1. `設計統括者役`、`設計者役`、`実装者役`、`対外Docs役`の責務とDocs権限を再整理
2. 現設計者役を`設計統括者役`へ変更
3. 各Phaseに専用の`設計者役`を配置可能にする
4. Git運用へ移行
5. Git移行後のDocs運用を要件定義
6. `docs/` Directory構造を変更
7. 構造変更完了後、各担当Taskへ新構造、権限、Current Entry Pointを通知
8. Phase単位の公開DocsとLossless統合を導入

## 3. Current State Preservation

Phase 1-ex開始・移行完了までは次を維持する。

```text
Current Role : 設計者役
Git          : 未導入
Docs Rule    : Current Append-Only／Timestamp Rule
Docs Layout  : Current Directory Structure
Task Notice  : 未実施
```

本ADRの作成時点で役職変更、Git初期化、Directory移動、担当通知を行わない。

## 4. Future Role Model

```text
設計統括者役
  ├─ Project全体設計
  ├─ Phase構成
  ├─ Cross-Phase整合
  ├─ 共通Policy／Architecture境界
  ├─ Phase開始用設計書
  └─ Phase最終Review／移行判定

Phase別 設計者役
  ├─ Phase詳細要件／設計
  ├─ Accepted上位設計の具体化
  ├─ 実装担当Handoff
  └─ Phase内Review
```

Phase別設計者役は、ユーザー要求や実装上のEvidenceに応じ、上位要件から大きく外れない範囲で再設計できる。

次は設計統括者役またはユーザーへEscalateする。

- Project全体Phase構成の変更
- 共通Port／Governance Core／Security Boundaryの変更
- Accepted ADRの破棄
- Privacy／Backup／公開Policyの変更
- 他PhaseへMaterial Impactを与える変更
- ユーザー要求との矛盾

## 5. Git／Docs Transition

Git導入後、現在のStrict Append-Only Timestamp Docs、Git History、Current Canonical Docs、Public Docs、Task Handoffの役割重複を再整理する。

詳細方式はPhase 1-ex内で要件化し、Migration、Inventory、Link更新、Rollback、担当通知を伴う。Directoryを先に変更してから要件を考えることを禁止する。

## 6. Consequence

- 長期Task一つへ全Phase詳細を集中させない
- Project全体整合とPhase内詳細を分離できる
- Git HistoryとDocsの重複を制御できる
- 各Phase完了Snapshotを人間公開とTask Handoffの両方に利用できる
- Role変更とDirectory変更の途中状態を明示的に管理する必要がある

## 7. Authorization Boundary

本ADRはPhase 1-ex実施内容の予約である。現在のRole変更、Task作成、Git初期化、Directory変更、File移動、各担当への通知、外部公開を許可しない。

