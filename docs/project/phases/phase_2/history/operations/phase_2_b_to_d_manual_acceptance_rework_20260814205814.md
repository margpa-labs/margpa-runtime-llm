# Phase 2-B～2-D Manual Acceptance Rework

```yaml
document_id: phase_2_b_to_d_manual_acceptance_rework_20260814205814
status: implementation_validated_manual_retest_required
phase: phase_2
scope:
  - phase_2_b
  - phase_2_c
from_role: プロジェクト責任者兼設計統括者役
to_role: User
created_at: 2026-08-14 20:58:14 JST
technical_blocker: none_after_rework
manual_retest_required: true
git_mutation: none
```

## 1. Manual Acceptance Finding

Phase 2-B～2-DのLocal Private Persistent UX手動受入で、次の2件を検出した。

1. Documentation RAGを有効化したPersistent Conversationで、Retrieval Event受信時に表示された引用元が、Terminal後のCanonical Detail再読込で消失した。
2. Serverを`Ctrl+C`で停止した後、同じPersistent Runtime Dataで再起動するとLifespan Startupが失敗した。

SQLiteのIntegrity Checkは`ok`、Schemaは`READY`、Conversation RecordにCorruptionはなかった。実データの削除、修復、移動または手動Mutationは行っていない。

## 2. Root Cause

### 2.1 Restart Recovery Identity Overflow

Web Runtimeが発番する`conversation_id`はSHA-512 Hexの128文字である。Startup Recoveryは、そのIdentity、Storage Revision、Retry AttemptおよびUUIDを連結して`ConversationOperationId`へ入れていた。`ConversationOperationId`の最大長は128文字であるため、正常な最大長`conversation_id`のRecoveryでValidation Errorとなった。

Existing Testは短いConversation IDとCustom Recovery Operation Factoryを主に使っていたため、Default Factoryの実運用上の長さ組合せを捕捉できていなかった。

### 2.2 Citation Projection Lost on Canonical Rerender

Persistent SSEはRetrieval EventとSafe Citation Projectionを正常にBrowserへ送信していた。しかしTerminal後、BrowserはServerのCanonical Conversation Detailを再読込し、Message DOM全体を再構築する。Citation Metadataは現行のPersistent Message Schemaに保存しないため、その再構築でCurrent Turnの引用表示が消失した。

## 3. Bounded Rework

### 3.1 Recovery Operation ID

Recovery Operation IDを、Domain SeparatorとRecovery LabelのSHA-512 Hex Digestへ変更した。入力Identity長に関係なく128文字に収まり、同じRecovery Labelは同じOperation IDに収束する。

### 3.2 Citation Page-memory Evidence

Persistent Streamの`start`でCurrent Turn IDを受け取り、`retrieval`のSafe Citation ProjectionをそのTurn IDに関連付けてProcess-local Browser Page Memoryに保持する。Canonical Detail再描画の際、同一TurnのAssistant Viewへ引用を再描画する。

次は行わない。

- Citation MetadataのSQLite永続化
- `localStorage`、`sessionStorage`またはIndexedDBへのConversation情報保存
- Public DemoまたはBasic PreviewへのPersistent Binding
- Existing v1 APIの変更
- Actual Runtime Dataの削除または手動修復

Browser Page ReloadまたはServer Restartを越えるCitation Metadata Persistenceは、Phase 2-E Documentation RAG Follow-upの別Contractで再設計する。

## 4. Validation

```text
Focused Rework Tests                : 25 passed
Conversation／Web Regression         : 252 passed
Mypy                                : PASS／111 source files
Ruff Format                         : PASS
Ruff Check                          : PASS
JavaScript Syntax                   : PASS
Full Suite                          : 615 passed／3 deselected
Actual Runtime Data destructive edit: 0
Git Commit／Push                     : 0
```

新規Regressionは、Default Recovery Factoryと最大128文字Conversation IDを組み合わせ、再起動RecoveryがActive Sessionを`interrupted`へ収束させることを検証する。Static Browser Contractは、Current TurnのCitation EvidenceがPage Memoryへ保持され、Canonical Detail再描画で同一Turnへ戻ることを固定する。

## 5. Manual Retest Gate

次のUser Manual Retestが必要である。

1. Existing `runtime_data`を削除せず、同じLocal Persistent起動Commandで再起動できること。
2. 既存Conversation List／Historyが復元されること。
3. Documentation RAGを有効にして新規回答を生成し、回答完了後のCanonical Detail再描画後も引用元が表示されること。
4. Browser Page Reload後にCitationが消えることは現行既知境界であり、Conversation本文の消失とは区別すること。

Manual Retest完了までは、Phase 2-B～2-D Technical Scopeの既存Closureを維持しつつ、Real Browser AcceptanceをCloseしない。
