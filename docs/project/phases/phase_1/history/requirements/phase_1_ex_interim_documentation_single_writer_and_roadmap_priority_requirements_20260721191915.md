# Phase 1-ex完了までのDocumentation単一Writer／Roadmap最優先導線 要件

- 文書ID: `phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 適用開始: 本要件Accepted時点
- 適用終了: Phase 1-ex完了宣言時点
- 関連総合要件: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- 関連Lossless要件: [lossless_phase_document_compilation_requirements_20260720231036.md](lossless_phase_document_compilation_requirements_20260720231036.md)
- 既存Role Policy: [task_role_write_authority_policy_20260719142558.md](task_role_write_authority_policy_20260719142558.md)
- supersedes: なし（Phase 1-ex完了までの期間限定Override）

## 1. 決定

Phase 1-ex完了宣言までは、`docs/`配下に作成する全Documentationを、現在の設計者役担当Taskが単一Writerとして作成する。

これは、既存の役割別Write Scopeに対する期間限定Overrideである。

```text
適用期間:
  本要件Accepted
  ～ Phase 1-ex完了宣言

docs/ Writer:
  現在の設計者役担当Taskのみ

対象:
  docs/配下の全File
  Phase単位Lossless Compilation
  Root Public Docsの設計・作成
  README.md等のPhase 1-ex公開成果物
```

Phase 1-ex完了後のDocumentation Ownershipは、Phase 1-exで確定する新しいRole／Authority Policyに従う。現時点でPhase 2以後の永続的な単一Writer運用を確定しない。

## 2. 単一Writerの対象範囲

現在の設計者役担当Taskは、Phase 1-ex完了まで次をすべて作成する。

- Requirements
- Architecture
- Governance
- ADR
- Operations Policy
- User Manual
- Review
- Documentation Index
- Common Handoff
- Designer Handoff
- Implementer Handoff
- Implementer Statusの文書化
- External Docs Statusの文書化
- Public Docs
- Phase Summary
- Project Continuity Master
- Phase単位Lossless Compilation
- Documentation Migration Record
- Documentation Inventory／Manifest
- Phase 1-ex Completion Evidence
- README、LICENSE、CITATION、NOTICEに関するDocumentation

Rootに配置する次の公開成果物も、Phase 1-ex完了までは現在の設計者役担当Taskが作成する。

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
```

LICENSEの権利条件はユーザー決定を必須とし、設計者役担当Taskが独自にLicense条件を決めない。

## 3. 他担当Taskの扱い

### 3.1 実装者役

実装者役は、Source、Test、Script、許可されたConfig等の実装結果を、会話または明示された報告Payloadとして設計者役へ渡す。

Phase 1-ex完了までは、実装者役自身が`docs/handoffs/implementer_status_*`を含む`docs/`配下へFileを書き込まない。設計者役が、実装者役の報告を根拠としてStatus Documentを作成する。

実装者役の発言を文書化する場合、次を区別する。

- 実装者役が報告した事実
- 設計者役が独立確認した事実
- 設計者役の評価／Review
- ユーザーが確認した事実
- 未確認事項

設計者役は、実装者役の報告内容を勝手に成功扱いへ変更しない。

### 3.2 対外Docs役

対外Docs役は、Phase 1-ex完了までは`README.md`、`docs/public/`、`external_docs_status_*`を含め、Documentation Fileを直接作成しない。

必要な提案、構成案、校正案、公開観点の指摘は、会話または設計者役への入力として提出できる。最終的なFile作成、内容固定、Index反映は現在の設計者役担当Taskが行う。

### 3.3 将来の設計統括者役／Phase別設計者役

現在の設計者役を設計統括者役へ変更する処理は、既存決定どおりPhase 1-ex内で行う。

Phase 1-ex完了までのDocumentation単一Writerは、Role変更後も同一の現在Taskが継続する。Phase別設計者役を作成した場合でも、Phase 1-ex完了前はDocsへ直接書き込ませず、Documentation Payloadを設計統括者役へ返す。

## 4. 既存Policyとの優先関係

適用期間中、Documentation Write Ownershipについて矛盾がある場合は、本要件を優先する。

期間限定でOverrideする例：

- 実装者役による`implementer_status_*`直接作成
- 対外Docs役によるREADME／Public Docs直接作成
- 対外Docs役によるLossless Phase Compilation実施
- Phase別設計者役によるDocs直接作成

Overrideしない事項：

- Source／Test／Script等の実装Ownership
- ユーザーだけが決めるLicense条件
- ユーザーの外部操作権限
- Git／GitHub／Lightning操作のAuthorization Boundary
- Canonical Docsの意味内容
- Append-Only、Timestamp、Public Identity、Privacy Rule

## 5. Append-Only運用

Phase 1-exでDocumentation運用が正式移行されるまで、既存のAppend-Only規則を維持する。

- 作成済みDocsを原則変更しない。
- 内容変更時は新Timestampの新Fileを作る。
- 新Fileから旧Fileまたは影響対象を明示する。
- Documentation Indexも新Timestampで作る。
- 古いDocsと古いIndexを履歴として保持する。
- 新しいTimestampを最新とする。
- File名は英語と`_YYYYMMDDHHMMSS`を使用する。
- 本文は原則日本語とする。

Phase 1-exのMigrationでFile移動、再編、Git管理への変更が必要な場合は、Inventory、Hash、Link検証、Rollbackを先に定義してから実施する。

## 6. Phase単位1File統合の担当

Phase完了ごとの1File統合は、現在の設計者役担当Taskが実施する。

これは要約ではなくLossless Compilationである。

```text
Source Set Freeze
  → Inventory
  → Path／Document ID／State／Size／SHA-512記録
  → 元本文を変更せず格納
  → 再抽出
  → Byte Size／SHA-512照合
  → 全件一致時のみPass
```

次を禁止する。

- 勝手な要約
- 意訳
- 再解釈
- 用語や口調の無断変更
- 重複の勝手な削除
- 矛盾の勝手な解消
- 新旧文書の無断選別
- Authorization Boundaryの変更
- 数値、Version、Hash、Path、Stateの変更

公開不可情報の除外または匿名化は、Lossless Compilation中の書換えとして行わず、独立したPrivacy Scrub工程として記録する。

## 7. READMEのRoadmap最優先要件

ユーザーが公開成果物の中で最も見せたい文書はRoadmapである。

Phase 1-exで作成する`README.md`は、Roadmapを補助リンクまたは末尾の参考資料として扱わず、最優先の閲覧導線として強調する。

対象Roadmap：

```text
docs/public/roadmap_ja.md
```

最終Directory設計でPathが変更された場合も、READMEから実在するCurrent Roadmapへ直接到達できるLinkを維持する。

## 8. README内のRoadmap表示要件

READMEの上部、Project概要の直後または同等に目立つ位置へ、Roadmap専用SectionまたはCalloutを置く。

最低限、次を満たす。

- `Roadmap`を独立見出しまたは視認性の高い導線として置く。
- 「このProjectの現在地、今後のPhase、完成予定像を確認する場合はRoadmapを最初に参照してください」という趣旨を敬語で明示する。
- Roadmapへの直接Linkを置く。
- RoadmapがProjectの中核公開文書であることを伝える。
- Current Phase、実装済み、未完成、将来計画の詳細をREADME内で不完全に再構築せず、Roadmapへ誘導する。
- Roadmap Link切れを公開前TestでFailとする。
- Mobile／GitHub表示でも導線が埋もれない位置に置く。

表示例の趣旨：

```markdown
## Roadmap — 最初にご覧ください

本Projectの現在地、Phaseごとの実装状況、今後追加するRuntime Governance、
Guardrail、Judge、RAG、Agent、および将来R&D統合計画は、Roadmapにまとめています。

→ [Roadmapを確認する](docs/public/roadmap_ja.md)
```

これは文言の固定Templateではない。README本文は敬語を維持しつつ、同等以上に明確なRoadmap導線を作る。

## 9. READMEとRoadmapの責務分離

READMEは次を簡潔に説明する。

- 何を作っているか
- 現在動く範囲
- 最初の起動／公開Demoへの導線
- Roadmapへの最優先導線
- Setup、License、Docsへの入口
- 末尾のEnglish Abstract

Roadmapは次を詳しく扱う。

- 全Phase一覧
- 各Phaseの目的と主要機能
- 実装済み／検証中／未着手／将来予約
- Phase Gateと依存関係
- Runtime Governance Platformへの発展
- EASA、DLAGSA、OCILNS等の将来統合Hook
- 現時点の制約と再評価条件

READMEへRoadmap全文を複製しない。READMEからRoadmapを強調して案内し、Phase情報のCurrent SourceをRoadmapへ集約する。

## 10. 検証条件

Phase 1-ex完了前に次を検証する。

```text
[ ] docs/配下のPhase 1-ex期間中Writerが現在の設計者役へ統一されている
[ ] 他担当Task向けHandoffに直接Docsを書かない境界が通知されている
[ ] Phase単位Lossless Compilationを現在の設計者役が実施している
[ ] Compilationの全Sourceが再抽出可能である
[ ] Byte Size／SHA-512が全件一致する
[ ] README上部にRoadmap専用導線がある
[ ] Roadmap Linkが実在し、GitHub上で解決する
[ ] READMEとRoadmapの実装状態表示が矛盾しない
[ ] README末尾にEnglish Abstractがある
[ ] Public IdentityがNazuna Researchに統一されている
[ ] Credential、個人Path、Private Artifactが公開Docsに含まれない
```

## 11. Completion Boundary

本要件の単一Writer運用は、Phase 1-exの全Completion Gateが合格し、現在の設計者役または移行後の設計統括者役がPhase 1-ex完了を明示的に宣言した時点まで継続する。

単にREADME、Roadmapまたは統合Fileを作っただけでは終了しない。

Phase 1-ex完了後のWriter分担は、その時点のAccepted Role／Authority Policyを正本とする。

## 12. Authorization Boundary

本要件のAccepted化は、Phase 1完了、Phase 1-ex開始、Docs Migration、Lossless Compilation実行、README／LICENSE生成、Git初期化、Commit、Push、GitHub公開またはLightning外部操作を自動許可しない。

現在許可されるのは、Phase 1-ex完了までのDocumentation Writerと、将来READMEのRoadmap最優先導線を要件として固定することだけである。

## 13. Append-Only

既存Role Policy、Phase 1-ex総合要件、Lossless Compilation要件を変更せず、期間限定の単一WriterとRoadmap最優先導線を追加する新Timestamp文書として作成した。
