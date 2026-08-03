# Phase 1-ex完了までのDocumentation単一Writer 共通Handoff

- 文書ID: `common_documentation_single_writer_until_phase_1_ex_completion`
- 状態: `current`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 対象: 設計者役、将来の設計統括者役、Phase別設計者役、実装者役、対外Docs役
- 正本言語: 日本語
- Requirements: [phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md](../requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md)
- Latest Index: [documentation_index_20260721191915.md](../documentation_index_20260721191915.md)
- supersedes: なし（Phase 1-ex完了までの共通通知）

## 1. 即時適用事項

Phase 1-ex完了宣言までは、`docs/`配下の全Fileを現在の設計者役担当Taskが作成する。

```text
Single Documentation Writer : 現在の設計者役担当Task
Effective Until             : Phase 1-ex Completion Declaration
Scope                       : All docs/ Files and Phase 1-ex Public Docs
```

## 2. 各担当の対応

### 実装者役

- 実装結果、Test結果、変更File、Known Issueを会話または報告Payloadとして設計者役へ渡す。
- Phase 1-ex完了までは`implementer_status_*`を含むDocsを直接作成しない。
- Source／Test／Script等の実装Scopeは別途Accepted Handoffに従う。

### 対外Docs役

- README、Public Docs、CITATION、NOTICE、Phase Summary、Lossless Compilationを直接作成しない。
- 提案または校正Payloadを設計者役へ渡すことはできる。
- Phase 1-ex完了後のOwnershipは新Policy確定まで未決定とする。

### Phase別設計者役

- Phase内設計Payloadを現在の設計者役または移行後の設計統括者役へ返す。
- Phase 1-ex完了前はDocsへ直接書き込まない。

## 3. Phase Compilation

Phase単位の1File統合も現在の設計者役が担当する。

- Summary RewriteではなくLossless Compilationとする。
- 元本文を変更しない。
- Source Inventory、Size、SHA-512を記録する。
- 再抽出後のByte Size／SHA-512が1件でも不一致ならFail Closedとする。
- Privacy Scrubは別工程として記録する。

## 4. README Roadmap Priority

Phase 1-exで作成するREADMEは、`docs/public/roadmap_ja.md`を最優先の閲覧導線として上部で強調する。

Roadmapは、このProjectの現在地、全Phase、実装状況、将来機能、独立R&D統合Hookを示す中核公開文書として扱う。

README内でRoadmapを単なる末尾Linkまたは補助資料として扱わない。

## 5. Authorization Boundary

本HandoffはDocs Writerの一時統一を通知する。Source変更、Phase 1-ex開始、Git操作、GitHub公開、Lightning操作またはLicense条件決定を許可しない。

## 6. Append-Only

既存のRole別Write Scope文書を変更せず、Phase 1-ex完了までの期間限定Overrideを新しい共通Handoffとして追加した。
