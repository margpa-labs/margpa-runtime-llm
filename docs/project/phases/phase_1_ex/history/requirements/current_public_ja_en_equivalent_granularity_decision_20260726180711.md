# Current／Public JA／EN同等粒度決定

```yaml
document_id: current_public_ja_en_equivalent_granularity_decision
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-26 18:07:11 JST
owner: 設計統括者役
```

## 1. 決定

`docs/project/current/`および`docs/public/`では、日本語版を正本とし、対応する英語版を派生版として作成する。

英語派生版は概要版、短縮版または抄訳にしない。日本語正本と同じ粒度、情報量および構造を持つ完全な英語版とする。

## 2. 同等性の対象

次の内容を省略せず対応させる。

- 見出しと文書構造
- 機能要件と非機能要件
- 根拠と設計判断
- 制約と例外
- 留意事項
- 既知の制限
- 未決事項
- 参照先

自然な英語表現への翻訳、語順調整および必要な用語説明は許容する。ただし、要約、情報省略、意味の追加、弱化、強化または再解釈は行わない。

## 3. 正本と完了条件

- Conflict時は日本語版を正本とする。
- 英語版だけに新しい要件、判断または例外を追加しない。
- 日本語正本と英語派生版の同等性を確認できない場合、Documentation Refreshは未完了とする。
- Initial Commit前Refreshでは、対象となるCurrent／Public文書のJA／EN Pairと同等性確認を必須とする。

## 4. 対象外

Phase、Shared、Raw History、Handoff、Status、Reviewおよび内部Operationsは日本語のみとする。
