# 設計者役担当タスク 引き継ぎ

- 文書ID: `designer_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: 設計者役担当タスク
- 正本言語: 日本語
- 共通引き継ぎ: [common_project_handoff_20260718174637.md](common_project_handoff_20260718174637.md)

## 1. 役割

- 要件の再整理・統合
- Architecture設計
- 技術候補比較
- Decision確定前のTrade-off提示
- ADR作成
- 未決事項管理
- 実装者向け仕様作成
- User決定事項の正本反映

## 2. 現在の設計者

この初期Snapshotを作成したTaskが設計者役を担当している。

## 3. 現在の完了事項

- Project目的統合
- Hardware制約整理
- 設計原則確定
- Initial Model選定
- Quantization選定
- Model Storage設計
- Runtime Governance基本方針
- ARGD／DAGD参照・要約
- Guard／Judge方針
- Audit基本要件
- Docs運用規則

## 4. 次の設計議題

Project全体のDirectory構成を設計する。

重点：

- Python Package名
- Domain／Application／Ports／Adapters
- Model Runtime
- Governance Runtime
- Guardrail
- Audit
- Storage
- API／UI
- Config
- Tests
- Runtime Data
- Git管理境界
- Cloud交換境界

## 5. 設計時の禁止事項

- 未決事項を勝手に確定扱いしない
- ARGD／DAGD原文を黙って改変しない
- Userの優先順位をModel性能中心へ変更しない
- 16GDを初期実装へ膨らませない
- FrameworkをDomain Logicにしない
- 実装許可前にSourceを作らない

## 6. 更新方法

実質的な設計変更は新Timestamp FileとADRを作る。

[documentation_rules_20260718174637.md](../requirements/documentation_rules_20260718174637.md)に従う。
