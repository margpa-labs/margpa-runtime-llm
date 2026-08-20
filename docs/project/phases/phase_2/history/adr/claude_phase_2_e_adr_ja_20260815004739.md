# Claude Phase 2-E ADR

```yaml
document_id: claude_phase_2_e_adr_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from_role: Claude Phase 2-E設計担当者役
to_role: Claude設計統括者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 00:47:39 JST
language: ja
source_architecture: claude_phase_2_e_architecture_20260815004739
```

## ADR-P2E-001: SwitchboardはObservation Layerとし、既存Security Gateを置き換えない

**決定**：Runtime Composition Switchboardは既存3ComponentのState解決ロジック（Local／Loopback／認証チェックを含む）を置き換えず、解決済み結果を写像するだけの追加層とする。

**代替案と却下理由**：
- (a) 既存`if/elif`分岐を全面的にRegistry駆動へ書き換える → 却下。Security-criticalなGate（Public/Basic Preview非Binding等、NFR-5）を扱う既存コードは複数Phaseで検証済みであり、単一Phaseでの全面置換はRegressionRiskが高い。Handoff §10で「Scope外変更を勝手に拡張しない」ことが明示されている。
- (b) Registryを完全に独立させ、既存Componentを登録しない → 却下。「Foundation」という名称と、Handoff §6.1の要求（実在するComponentの状態を扱うSwitchboard）を満たさない。

**結果**：Foundationとしての要求（Typed Descriptor／State区別／Seam）を満たしつつ、既存の検証済みSecurity境界への影響をゼロにする。

## ADR-P2E-002: Citation EvidenceはConversation永続化と同一DB・同一Transactionに格納する

**決定**：新規`turn_citations`Tableを既存`conversations.sqlite3`（Scope単位）に追加し、既存Turn Commitと同一`BEGIN IMMEDIATE`Transaction内でCommitする。

**代替案と却下理由**：
- (a) 独立したCitation専用DB／Storeを新設 → 却下。Assistant CompletionとCitation EvidenceのAtomicity（FR-3.5、Handoff §9必須検証項目）を満たすには2-Phase CommitまたはSagaパターンが必要になり、新しい失敗モード（片方だけCommit）を生む。既存のCAS Transactionに相乗りすれば、Atomicityおよび既存Crash Recovery（`recover_incomplete_conversations()`）をそのまま再利用でき、新しいRecovery経路の実装・検証コストを避けられる。
- (b) Message本文へCitationをJSON埋め込み → 却下。FR-3.1（Assistant Message本文への暗黙埋め込み禁止）に直接抵触する。

**結果**：Atomicity・Crash Recovery・Idempotencyを新規実装ゼロで継承する。追加Riskは、既存`commit()`のTransaction Scopeが広がることによる潜在的なLock保持時間の増加のみであり、Citation書込はTurn完了時（Streaming終了後）の1回だけで既存のModel生成中Lock非保持原則（NFR-8）には影響しない。

## ADR-P2E-003: Component KeyはClosed Enumにせず、Validated Opaque Stringとする

**決定**：`ComponentKey`は既存`_OpaqueIdentifier`パターンに準ずるPattern-validated文字列とし、Component種別をCore CodeへHard-codeしない。

**根拠**：Task Role／Write Authority Policy §10.0.2 General Hard-code Prohibitionに従う。将来Componentが追加される際、Core（`contracts.py`／`application.py`）の変更を要求しない設計とする。

## ADR-P2E-004: Fail-closed Citation読み取り（Unavailable≠Not-present≠Corrupt）

**決定**：Citation読み取りは`not_present`（正常：Citationなし）／`unsupported_schema_version`／`corrupt_record`を明示的に区別したUnavailable型で返し、いずれの場合もConversation本体の取得を失敗させない。

**代替案と却下理由**：
- (a) Citation破損時にConversation取得全体を失敗させる → 却下。Citationは補助Evidenceであり、Message本文の可用性より優先されない（既存のRAG `UNAVAILABLE`状態が会話継続を妨げない設計思想と整合）。
- (b) 全ての異常を単一の`null`へ収束させる → 却下。Handoff §9「RAG OFF／Unavailable／0件／Warning／Failureの区別」の精神に反し、運用時の障害切り分けができなくなる。

## ADR-P2E-005: Governance Seamは`off`固定のPlaceholder Fieldとし、評価ロジックは実装しない

**決定**：`ComponentDescriptor.governance_seam_mode`は`Literal["off"]`のみを許容する型とし、`observe`／`enforce`の評価ロジックは一切実装しない。

**根拠**：Handoff §6.1「将来の`off／observe／enforce`へ接続できるSeamを予約するが、Phase 2-EではFull Governance Engineを実装しない」との明示的Scope境界。Runtime Governance Specification自体が`status: current_planned_not_implemented`であり、Phase 2-Eで先取り実装するとPhase 3以降の設計変更時にBreaking Changeを生む。

## ADR-P2E-006: Frontend統合はDetail Fetch経路への最小追加とし、既存描画関数は変更しない（実装調査により確定）

**決定**：`src/margpa_runtime_llm/web/static/app.js`の`loadPersistentDetail()`（実装調査でExact Line確認済み、Architecture §6参照）にのみ、Response JSONから`state.persistentCitationEvidence`Mapへの書き込みを追加する。`renderCitations()`／`renderPersistentDetail()`／SSE経路（`handlePersistentEvent()`）は無変更とする。

**根拠**：実装調査（`grep`＋`Read`）により、Client-side Data Model（`state.persistentCitationEvidence`）と描画関数（`renderCitations()`）が既にSSE経由のPage Memory入力に対応済みであり、不足しているのはDetail Fetch側からの同一Mapへの入力経路のみであることを確認した。既存描画関数・既存Client State Shapeを変更する必要はなく、新しいData Sourceを1本追加するだけで要件（Reload／Resume／再Open後のCitation復元）を満たせる。当て推量ではなく実Source確認済みのため、本ADRを確定として記録する（Research Asset Mutation Control §11「対象Fileを完全列挙できるか」を満たした状態）。

## Status

```text
Current Point            : ADR Frozen
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（設計段階）
Open Current Blocker      : NONE
Controller-owned Next Work: Mutation Manifest／Acceptance Matrix／Implementer Handoff作成
Deferred Evidence         : NONE
Exact Next Route          : Mutation Manifest作成へ進む
```
