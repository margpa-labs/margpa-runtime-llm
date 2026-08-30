---
document_id: phase_8_entry_branch_ui_hide_and_archived_chat_management_reservation_20260830175855
document_type: append_only_planned_work_implementation_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-08-30 17:58:55 JST
decision_authority: user
authority_owner: Nazuna Research
target: phase_8_entry
depends_on:
  - phase_7_closure
  - phase_8_design_and_preflight
implementation_authorized: false
---

# Phase 8 Entry — Branch UI非表示／アーカイブ済みChat管理予約

## 1. 決定

Phase 8冒頭のBounded UI Workとして、次の二件を実装候補へ追加する。

1. Chat Branch機能のUIを既定非表示にする。
2. 設定画面のデータコントロールへ、アーカイブ済みChatの管理画面を追加する。

## 2. Chat Branch UI

Branchは、同じTurnから異なる会話経路を比較する機能であり、Context Window増加とは概念上
別Capabilityである。しかし、現行User運用では利用価値が低く、回答下部の操作UIを占有する。
PoC／MVPの可読性を優先し、Phase 8冒頭でUIを既定非表示にする。

### 2.1 保持するもの

- Branch Domain Data。
- Branch Persistence。
- Branch API／既存会話の互換性。
- 既存Branchを読める能力。

### 2.2 非表示対象

- `このBranchを選択`等のBranch選択Control。
- 現行Chat画面でBranch操作を促す付随UI。

### 2.3 実装方針

Source／Data／APIを削除せず、表示層だけを可逆的に非表示にする。将来の研究比較、設定または
Feature Flagから復元できる構造を維持する。既存Branch Historyを破壊、移行または削除しない。

## 3. アーカイブ済みChat管理

設定画面の既存`データコントロール`内へ、`アーカイブ済みのChatを管理`入口を追加する。

### 3.1 Phase 8対象

- 管理Button。
- Modal／Panelでアーカイブ済みChat一覧を表示。
- Chat Title。
- 作成日または既存Schemaで正確に取得可能なTimestamp。
- 対象Chatを開く。
- Archiveを解除する。
- 再読込み。
- Archive解除後は手動`再開`なしで送信可能な既存契約を維持する。

Chat数が多い場合に初期画面を遅くしないよう、管理画面を開いた時のLazy Load、Bounded Pageまたは
既存List APIの範囲内で取得する。全ChatをApplication起動時に無条件展開しない。

### 3.2 Phase 8では見送るもの

- 完全削除。
- Turn、Branch、Citation、Judge Evidence、Recording等を跨ぐCascade Delete。
- Retention Policy／TTL／自動削除。
- 全Export／一括Deleteを実装済みとする表示。

完全削除はData Lifecycle、Historical Evidence、孤立Record、Citation／Recording整合および
Audit方針を別途設計してから扱う。Archive解除と完全削除を同じIconまたはActionとして扱わない。

## 4. Acceptance Candidate

1. Branch Data／APIを保持したまま、通常ChatのBranch操作UIが既定表示されない。
2. 既存Conversation／Branch／CitationにData Migrationまたは破損がない。
3. データコントロールからアーカイブ済みChat一覧を開ける。
4. 各行でTitleと正確なTimestampを確認できる。
5. 一覧からChatを開ける。
6. Archiveを解除できる。
7. 解除後、手動`再開`なしで送信できる。
8. ArchivedのままのChatを勝手にActiveへ変更しない。
9. 完全削除Actionまたは未実装Capabilityの虚偽表示がない。
10. 多数Chatがあっても通常のServer／UI起動を不必要に遅くしない。

## 5. Scope／Authority

本予約は、Phase 8開始、Source／Test／Config Mutation、Git、Backup、Phase 7 Closureまたは
完全削除の実装Authorityを与えない。Phase 7 Closure後のPhase 8 Design／Preflightで、既存API、
UI SurfaceおよびTest範囲を確認してから実装する。

