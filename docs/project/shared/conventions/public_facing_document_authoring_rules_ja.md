# 対外向け公開Document作成Rules

```yaml
document_id: public_facing_document_authoring_rules
document_type: shared_stable_convention
document_state: current
language: ja
created_at: 2026-09-02 00:50:58 JST
updated_at: 2026-09-02 11:48:24 JST
decision_authority: user
owner: Nazuna Research
applies_to:
  - docs/public
  - employment_portfolio_documents
  - external_explanatory_materials
history_policy: append_only
```

## 1. Purpose

本Rulesは、MARGPA Runtime LLMの対外向け公開Document、就職・転職用Portfolio、技術説明資料およびDemo紹介文を作成するときの共通基準である。

内部の設計正本、Evidence、Failure Ledger、Handoffおよび研究記録を、そのまま外部へ転記するためのRulesではない。事実の正確性を維持しながら、初見の読者が短時間でProjectの価値、実装範囲、技術力および現在地を理解できる形へ再構成する。

## 2. Reader Assumption

対外向けDocumentの読者は、次を知らない前提とする。

- Repositoryの存在、Directory構造および内部File名。
- 過去Phase、会話Log、略称、内部用語および設計判断の経緯。
- MARGPA Runtime LLMを共同で開発してきたContext。
- 内部Docsへアクセスする方法。
- 個別Testで使用した題材、検証コードおよび固有名詞。

「過去に説明済み」「正本に書いてある」「Link先を読めば分かる」を前提にしない。各Documentは、想定用途の範囲で単体完結させる。

## 3. Author Voice

### 3.1 `User`を一人称として使わない

Nazuna Research自身が作成・提示する資料で、作成者を`User`と呼ばない。

Bad:

```text
Userが指定したURLを取得する。
User Macで確認した。
User登録Documentを検索する。
```

Preferred:

```text
指定したURLを取得する。
実機Macで確認した。
登録Documentを検索する。
```

作成主体を明示する必要がある場合は、`Nazuna Research`、`本Project`または自然な主語省略を使う。製品機能として一般利用者を指す必要がある場合だけ、文脈に応じて`利用者`、`操作する人`等を使用する。

### 3.2 内部Agent視点を持ち込まない

Codex、Claude、Copilot等の内部開発担当視点で「ユーザーへ返す」「ユーザー確認待ち」と書かない。対外資料では、開発工程上の事実として`独立Review`、`実機確認`、`手動承認`、`最終判断`等へ置き換える。

## 4. Readability

### 4.1 初見で意味が通る文章

- 一文に一つの主張を置く。
- 名詞、略語、Slash区切りおよび英単語を過剰に連結しない。
- 内部用語を使う場合は、初出時に一般的な言葉で意味を説明する。
- 抽象概念だけを並べず、何ができるのか、何を実装したのかを先に示す。
- 主語、対象、状態および時制を曖昧にしない。
- 読み手が前のSectionへ何度も戻らなくても理解できる順序にする。

### 4.2 技術者以外にも入口を作る

採用担当者、技術面接官、Software EngineerおよびAI Engineerのいずれが読んでも、最初の数Sectionで次を把握できる構成にする。

1. 何を作っているか。
2. 一般的なChat Applicationと何が違うか。
3. 現在どこまで動くか。
4. どの技術を使っているか。
5. どのように品質を確認しているか。
6. 次に何を作るか。

詳細な設計説明は、この入口が成立した後に置く。

### 4.3 難解な内部文をそのまま使わない

内部Docsで正確な文章でも、前提知識が必要なら対外向けには難解である。Internal Contract、Authority、Evidence、Lifecycle等を使う場合も、読者が理解できる結果や目的へ翻訳する。

Bad:

```text
Configured／Active／Executed IdentityをFrozen Envelopeで保持する。
```

Preferred:

```text
設定したModelと実際に実行されたModelを区別し、切替後も追跡できるようにしている。
```

## 5. Truthfulness and Strategic Disclosure

### 5.1 嘘を書かない

- 未実装を実装済みと書かない。
- Fixture、Preview、CandidateおよびFutureを完成機能に見せない。
- Test合格だけで実機動作を確認済みと書かない。
- 一度だけ観測した成功を安定運用済みと一般化しない。
- `世界初`、`唯一`、`最先端`、`完全`等を比較Evidenceなしで使用しない。

### 5.2 正直さと全件開示を混同しない

対外向けDocumentは、内部Failure LedgerやController Review Reportではない。事実を歪めない範囲で、目的に不要な不利情報、Raw Error、長いIncident経緯および内部Rework回数を自発的に列挙しない。

次を区別する。

```text
False Claim:
  未成立なのに成立済みと書く。

Strategic Omission:
  読者の理解に不要な内部Failure詳細を掲載しない。

Honest Current State:
  成立範囲を示し、未完成部分は「調整中」「次工程」と簡潔に示す。
```

### 5.3 不利な表現を必要以上に強調しない

内部では`FAIL`、`ADJUST`、`unavailable`、`malformed_output`等を正確に残す。一方、就職用Portfolioでは、採用判断に必要な場合を除きRaw CodeやIncident詳細を掲載しない。

Bad:

```text
品質Acceptanceに失敗し、使用不能で、Server Restartでのみ復旧した。
```

Preferred:

```text
実機での安定動作と切替後の復帰を追加検証している。
```

ただし、現在利用できない機能を「利用可能」と書くことはStrategic OmissionではなくFalse Claimである。

### 5.4 完了と完全を分離する

ProjectでAccepted／ClosedとなったPhaseは、Portfolio上では`完了`と書ける。後続改善があることを理由に、過去Phaseの成果を過度に弱く書かない。

`Phase完了`は「全ての将来改善が不要」という意味ではない。必要なら、完了した基盤と現在調整している追加機能を別文で示す。

## 6. Information Density and Length

- Portfolio用RoadmapとTechnology Selectionは、原則1 Fileあたり150〜200行程度を目安とする。
- 全Sectionを同じ長さにしない。
- Project理解へ直結する目的、成果、技術、検証および現在地を厚くする。
- 内部経緯、細かなFailure、長い免責および将来候補の羅列は薄くするか省略する。
- 表は比較しやすい情報に限定し、長文をTable Cellへ詰め込まない。
- 箇条書きは意味の近い項目をまとめ、似た表現を水増ししない。

行数は品質の代理ではない。150〜200行の範囲でも、重要度によって情報粒度を変える。

## 7. Standalone Document Rule

### 7.1 閲覧不能な参照先へ誘導しない

Portfolio受領者がGitHub Repository、Local Repositoryまたは内部Docsへアクセスできるとは限らない。

次のような結びを使用しない。

```text
詳細は通常版Roadmapを参照する。
Architecture Documentを参照する。
内部FileへのRelative Linkを参照する。
```

読者に必要な情報は、対象Document内へ記載する。Repository内Pointerは内部Metadataや開発用Evidenceでは有効だが、対外本文の説明不足を補う手段にしない。

### 7.2 Metadata

冒頭には通常どおりYAML Metadataを置く。最低限、次を含める。

```yaml
document_type: <type>
document_state: <state>
language: ja
created_at: <timestamp>
updated_at: <timestamp>
public_author: Nazuna Research
project: MARGPA Runtime LLM
edition: <edition>
current_phase: <phase>
```

対外本文に不要なLocal Absolute Path、Private Identifier、Thread ID、Secret、Tokenおよび閲覧不能な参照Pointerは掲載しない。

## 8. Portfolio-specific Content Boundary

### 8.1 Include

- Projectの目的と利用イメージ。
- 実装済みCapabilityと代表的な画面領域。
- Phase単位のProgressと現在地。
- 一般的な採用技術と選定理由。
- Architecture上の責務分離を平易に説明した概要。
- Test、Static Analysis、Build、実Modelおよび実機確認の進め方。
- Software Engineering、AI EngineeringおよびProject Management上の成果。
- 現在調整中の内容を簡潔に示した次工程。

### 8.2 Exclude

- 個別Testで使用した人物名、作品名、団体名、質問文および検証コード。
- 私的会話、個人情報、Local Path、Secret、Credentialおよび内部Debug情報。
- 独自Algorithm、内部Protocol、Rule構成、Conflict解決方式および再現可能な設計Recipe。
- 内部Agentへの叱責、Failure Evidence、Provider固有Incidentの詳細。
- 読者が利用できないRepository内Fileへの参照要求。
- 競争優位を再現できる内部構造や未公開研究Asset。
- Portfolioの理解に不要なRaw Error Codeと長い未解決一覧。

LLM名、Library名、Framework名、Database名および一般的な技術方式は、選定内容として必要なら記載できる。

## 9. Terminology

- `User`ではなく、主語省略、`指定した`、`登録した`、`実機`、`利用者`等を文脈に応じて使う。
- `User Mac Manual`は、対外向けには`実機Macでの確認`、`実機確認`または`Manual Test`とする。
- `User Attention`は、対外向けには`Human Attention`または`確認負荷`とする。
- Internal Role名は、必要なら`設計`、`実装`、`Independent Review`等の一般的役割へ置き換える。
- 日本語で自然に説明できる箇所へ無理にEnglishを残さない。
- 一般的な技術用語は、業界で通用する表記を維持できる。

## 10. Structure Template

Roadmap系の基本Flow：

```text
Metadata
Project Overview
Current Capabilities
Development Progress
Phase Progression
Current Focus
Verification
Next Milestones
Representative Deliverables
Engineering Value
Current Position
```

Technology Selection系の基本Flow：

```text
Metadata
Selection Principles
Decision Criteria
Current Technology Stack
Model Strategy
Application Architecture
Data／Retrieval
Frontend／UX
Quality／Operations
Deferred／Not Selected
Deployment Boundary
Current Status
```

元FileのFlowと視覚的形式を尊重するが、情報価値が低いSectionを機械的に残さない。

## 11. Append-only History

`docs/public/`のStable Documentを更新する前に、更新前全文を対応するHistory Directoryへ保存する。

```text
Roadmap              -> docs/public/history/roadmap/
Technology Selection -> docs/public/history/technology_selection/
Demo Images          -> docs/public/history/demo_images/
Overview             -> docs/public/history/overview/
Concept              -> docs/public/history/concept/
```

- History FileはTimestamp付きFile名とする。
- 保存済みHistoryを上書き、修正、削除または再利用しない。
- Stable DocumentだけをCurrentへ更新する。
- 更新後にHistory SnapshotとStableの役割を混同しない。
- 新しいPublic Documentも、最初の改訂前に初版をHistoryへ保存する。

## 12. Stable Public Document Update Cadence

公開Documentは、役割に応じて通常更新対象と保護対象を分離する。

### 12.1 通常更新対象

次の2 Fileは、Phase設計、Phase Ready、Phase ClosureおよびCurrent計画変更に合わせ、従来どおり更新する。

```text
docs/public/roadmap_ja.md
docs/public/roadmap_summary_ja.md
```

更新時はCurrent State、次工程、完了Phaseおよび既知の主要境界を正直に反映し、対応するAppend-only Historyを残す。

### 12.2 原則保護対象

次の3 FileはRoutine Phase進行、最小Closureまたは内部Finding追加だけでは更新しない。

```text
docs/public/roadmap_portfolio_edition_ja.md
docs/public/technology_selection_portfolio_edition_ja.md
docs/public/technology_selection_ja.md
```

更新可能なTriggerは次に限定する。

- Phase 10のAll-Docs Integrationで全体整合を取る時。
- 最小Closureではない通常Full Closureで、公開内容の再統合が必要な時。
- Nazuna Researchから明示的な更新指示がある時。

保護対象は「古いから自動更新する」「Roadmapを更新したので機械同期する」「関連Sourceが変わったのでついでに直す」という理由だけで変更しない。

更新Authorityが成立した場合も、本RulesのStandalone、Strategic Disclosure、Professional PresentationおよびAppend-only Historyを適用する。

## 13. Review Checklist

公開前に次を確認する。

1. 初見の読者が3分でProjectの目的、規模、現在地を把握できるか。
2. 作成者を`User`と呼んでいないか。
3. 一文が長すぎず、内部用語の前提なしで読めるか。
4. 嘘、誇大Claim、未成立機能の完成扱いがないか。
5. 必要のない不利情報やRaw Failureを過剰開示していないか。
6. Current／Candidate／Fixture／Futureの境界が正直か。
7. 個別Test題材、個人情報、Private PathおよびSecretがないか。
8. 閲覧不能なFileやRepositoryへ説明を丸投げしていないか。
9. 内部Recipeや競争優位を再現できる情報がないか。
10. 各Sectionの粒度が重要度に合っているか。
11. YAML Metadataがあり、`public_author: Nazuna Research`になっているか。
12. 更新前版をAppend-only Historyへ保存したか。

## 14. Acceptance

対外向け公開Documentは、次を満たした場合に完成候補とする。

- 単体で読める。
- 初見でも難解文書になっていない。
- Projectの幅と技術的深さが自然に伝わる。
- 内部情報を大量に開示せず、実績を過度に弱く見せない。
- 事実とCurrent Stateに反しない。
- 転職用PortfolioとしてProfessionalな印象を維持する。
- History、Metadataおよび公開境界が守られている。

本Rulesに反する場合、内部Docs上の文章が正確であっても、対外向けDocumentとしてはRework対象とする。
