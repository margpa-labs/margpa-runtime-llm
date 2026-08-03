# Phase単位Lossless Documentation Compilation要件

- 文書ID: `lossless_phase_document_compilation_requirements`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 実施予定担当: 対外Docs役
- 正本言語: 日本語
- supersedes: なし

## 1. 目的

Phase完了ごとに、当該Phaseで新規作成または更新してきたDocsをPhase単位の1Fileへ再整理する。

統合文書は次の両方を満たす。

- GitHubで人に見せても問題がない
- Codex Taskを作り直しても即時引き継ぎ可能な粒度を持つ

ただし、運用、共通ルール、権限、Task間情報伝達、要件、Accepted Decision等を勝手に要約、意訳、再解釈してはならない。

## 2. Lossless Principle

Phase統合はSummary Rewriteではなく、Lossless Compilationとする。

```text
Source Documents
  ↓ exact copy + external metadata
Phase Compilation Document
  ↓ extraction verification
Original Bytes Reproducible
```

元本文の内容、用語、口調、順序、Decision、Boundaryを変更しない。

## 3. `verbatim_required`対象

- 運用規則
- 共通ルール
- Task間Handoff
- Role Authority／Write Authority
- Requirements／Acceptance Criteria
- Accepted ADR／Decision
- Architecture Boundary
- Authorization Boundary
- Backup／Git／公開Policy
- Privacy／Security Rule
- Model／Environment／Path情報
- Known Issues／未解決事項
- Review Finding／Test Evidence

## 4. 禁止事項

- 要約
- 意訳
- 再解釈
- 読みやすさを理由とした書き換え
- 用語、口調、表記の無断統一
- 重複の勝手な削除
- 矛盾の勝手な解消
- 新旧記述の無断選別
- 複数文書を混ぜた新しい結論の生成
- Authorization Scopeの拡大または縮小
- 数値、Version、Hash、Path、Stateの変更

## 5. 許可される追加

元本文の外側に限り、次を追加できる。

```text
Source File
Source Document ID
Source State
Source Timestamp
Source Size
Source SHA-512
BEGIN SOURCE
<元内容そのまま>
END SOURCE
```

新旧文書や矛盾文書は双方の本文を保持し、`current`、`historical`、`superseded`、`conflicting`等の状態を外側のManifestで示す。

## 6. Deterministic Compilation

1. Phase対象Source SetをFreeze
2. Path、Size、SHA-512、Document ID、StateをInventory化
3. 決定論的な順序を定義
4. Source本文を変更せず統合
5. 統合Fileから各Source Payloadを再抽出
6. 再抽出PayloadのByte Size／SHA-512を元Sourceと比較
7. 全件一致時だけCompilation Pass
8. 統合File自身のSHA-512とSource Manifestを記録

1件でも不一致ならFail Closedとし、対外Docs役が修正を推測せず設計者役へ返す。

## 7. Public Safetyとの両立

公開不可情報を統合中に書き換えてはならない。次のいずれかを選ぶ。

1. Sourceを正式なPrivacy Scrub工程で先にSanitizeする
2. 公開不可SourceをFile単位で除外し、Path、Hash、除外理由をManifestへ記録する
3. 内部用Lossless Compilationと公開用Derived Documentを分離する

Credential、個人情報、Private Pathを保持するためにLossless原則を利用してはならない。Privacy／Security削除は既存Policyどおり優先するが、削除は統合工程の外で明示的に行う。

## 8. Derived Public Docsとの分離

次は説明用Derived Docsであり、要約・編集可能である。

- `README.md`
- `overview_ja.md`
- `concept_ja.md`
- `roadmap_ja.md`

一方、Phase Compilation、共通ルールCompilation、Handoff CompilationはLosslessを必須とする。Derived DocsをCanonical RequirementsやLossless Handoffの代替にしない。

## 9. Review Gate

- 対外Docs役: Compilation実施、Manifest、Public Safety Scan
- Phase設計者役: Phase内Source Setと内容整合を確認
- 将来の設計統括者役: Cross-Phase RuleとCurrent Setを確認
- ユーザー: 必要に応じて公開前受入

現在のPhase 1-ex前は、設計者役がReview責務を持つ。

## 10. Timing

```text
Phase Test完了
  → Phase Review
  → Lossless Compilation
  → Derived Public Docs更新
  → Privacy／Integrity Review
  → Phase Final Gate
  → Backup
  → GitHub反映
```

統合文書がBackup対象である場合、Backup確定後に内容を変更しない。

## 11. Authorization Boundary

本書はPhase 1-ex以後の要件予約である。現在のDocs統合、既存Docs削除、Git操作、Public Docs生成、Script実装、Directory変更を許可しない。

