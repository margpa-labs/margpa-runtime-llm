# Documentation Structure／Task Operations

```yaml
document_id: documentation_structure_and_task_operations
status: current
language: ja
created_at: 2026-07-26 17:00:34 JST
updated_at: 2026-07-27 07:52:36 JST
owner: 設計統括者役
rag_default: true
```

## 1. 目的

本書は、MARGPA Runtime LLMにおけるDocs構造、文書の読み方、History、Phase単位運用、Lossless Compilation、再構築境界、Task間伝達および役割別Write Authorityを一つの共通運用入口へまとめる。

詳細正本：

- [Documentation Rules](../conventions/documentation_rules_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Current Documentation Index](../../current/documentation_index_ja.md)
- [Phase 1-ex Index](../../phases/phase_1_ex/phase_index_ja.md)

本書は両正本の内容を短く置き換えるものではない。構造と運用を横断して解決するための共通入口である。

## 2. Project／Docs Root

```text
Project Root:
margpa-runtime-llm/

Documentation Root:
margpa-runtime-llm/docs/
```

ユーザーが`docs/`、`src/`等の相対Pathだけを示した場合は、Project Root配下として解釈する。

Docsの読取は、明示的なWrite Authorityがない限りRead-onlyで行う。

## 3. Canonical Directory Structure

```text
docs/
├─ project/
│  ├─ current/
│  │  ├─ documentation_index_ja.md
│  │  ├─ requirements/
│  │  ├─ architecture/
│  │  ├─ governance/
│  │  ├─ project_continuity/
│  │  └─ history/
│  │     ├─ requirements/
│  │     ├─ architecture/
│  │     ├─ governance/
│  │     ├─ project_continuity/
│  │     └─ index/
│  ├─ phases/
│  │  └─ <phase>/
│  │     ├─ phase_index_ja.md
│  │     ├─ requirements/
│  │     ├─ architecture/
│  │     ├─ governance/
│  │     ├─ adr/
│  │     ├─ operations/
│  │     ├─ handoffs/
│  │     ├─ user_manual/
│  │     ├─ index/
│  │     └─ history/
│  └─ shared/
│     ├─ conventions/
│     ├─ operations/
│     ├─ task_roles/
│     ├─ schemas/
│     ├─ templates/
│     ├─ user_manual/
│     ├─ design_governance_handoff/
│     └─ history/
│        ├─ conventions/
│        ├─ operations/
│        ├─ task_roles/
│        ├─ schemas/
│        ├─ templates/
│        ├─ user_manual/
│        └─ design_governance_handoff/
└─ public/
   ├─ overview_ja.md
   ├─ concept_ja.md
   ├─ roadmap_ja.md
   └─ history/
      ├─ overview/
      ├─ concept/
      └─ roadmap/
```

Directoryは実Artifactがある場合だけ作る。空Directoryを維持するためだけのDummy Fileは原則作成しない。

## 4. Reading／Resolution Order

通常の担当Task、再開Task、RAGおよび人間の読解は、次の順で開始する。

```text
docs/project/current/documentation_index_ja.md
  → Current Canonical Docs
  → Active Phase phase_index_ja.md
  → Shared Rules／Task Authority
  → 対象PhaseのStable文書
  → 必要な場合だけLossless Compilation
  → Source確認時だけRaw History
```

Raw Historyを最初から全件読む必要はない。監査、矛盾追跡、Source確認、旧判断の復元または明示指定時だけ使用する。

## 5. Documentation Classes

### 5.1 Current

現在有効なProject横断正本を置く。Stable Filenameは最新版への入口として使う。変更履歴はTimestamp付きAppend-only Development Logで保持し、Git Historyに置き換えない。

### 5.2 Phase

Phaseごとの設計、実装連携、Review、Evidence、CompilationおよびHistoryを置く。

### 5.3 Shared

Phase横断のConvention、運用、Schema、TemplateおよびRole Authorityを置く。

### 5.4 Public

人が最初に読む公開用文書を置く。細かな編集履歴ではなくMilestone Historyを保持する。

## 6. Phase Directory

Active Phaseでは、必要なCategoryだけを使用する。

```text
requirements/ : Phase要件
architecture/ : Phase設計
governance/   : Phase固有Governance
adr/          : Phase／Cross-Phase判断
operations/   : Review、Migration、Backup、Release等
handoffs/     : Stable Handoff
user_manual/  : Phase時点の操作手順
index/        : Lossless Index Compilation等
history/      : Raw原文、Status、Review、Handoff、Event
```

Completed Phaseでは、Phase Index、Lossless Compilation、Raw Historyおよび完了Evidenceから当時の状態を再現できるようにする。

### 6.1 Stable Index／Development Log

`phase_index_ja.md`は最新状態へのStable入口である。Stable入口の更新だけでは開発ログを満たさない。

Phase IndexまたはCurrent Indexを変更するたびに、Active Phaseの`history/`へ新しい`documentation_index_YYYYMMDDHHMMSS.md`を追加する。Stable IndexとTimestamp Snapshotは同じDocumentation更新の一組として扱い、片方だけで完了にしない。

Timestamp SnapshotはAppend-onlyであり、Git開始後も継続する。Git履歴はDiff確認に使用できるが、Task間Handoff、Phase再構築および人間向け開発日誌としてのIndex Snapshotを省略する理由にしない。

## 7. History／Append-only

- Historyは原則Immutableである。
- 既存History Fileを編集せず、新しいEvent Fileを追加する。
- Event Filenameは`descriptive_name_YYYYMMDDHHMMSS.md`とする。
- 新Fileに必要に応じて`supersedes`を記載する。
- 古い文書へSuperseded表記を追記しない。
- Privacy、Credential、Secret Scrubだけは理由とRecordを伴う例外とする。
- 新しいTimestampほど新しいEventである。
- Stable文書を更新する場合は、変更前原文と変更後原文をTimestamp付きHistoryとして保存する。
- Append-only Development Log、Handoff、Status、Review、Evidence、Decision、Index SnapshotおよびRaw Sourceは、後続文書へ反映済みでも削除、上書き、統合、圧縮、置換または退役しない。
- Git採用後もこの保持方針を継続し、Git履歴を省略理由にしない。

Historyは開発日誌、判断証跡、Task間引き継ぎおよび監査Evidenceを兼ねる。役目が終わったことを理由に完全削除しない。

History全体は、Rollback、各時点の状態再現、Task再作成、Phase単位Lossless Compilationおよび将来の再検証に使用する。Phase単位で文書をまとめ直す場合、最新版だけでなく当該Phaseの全Append-only Development LogをSource Inventoryへ含める。

### 7.1 Stable Current／Shared／Public Backup

Current、SharedまたはPublicのStable文書を変更する場合、最初に現在の原文を対応Historyへ完全コピーする。

```text
Filename:
  <stable_document_stem>_<phase>_<language>_YYYYMMDDHHMMSS.md

Current Example:
  docs/project/current/architecture/basic_design_ja.md
    → docs/project/current/history/architecture/
      basic_design_phase_1_ex_ja_20260727071234.md

Shared Example:
  docs/project/shared/conventions/documentation_rules_ja.md
    → docs/project/shared/history/conventions/
      documentation_rules_phase_1_ex_ja_20260727071234.md

Public Roadmap Example:
  docs/public/roadmap_ja.md
    → docs/public/history/roadmap/
      roadmap_phase_1_ex_ja_20260727071234.md
```

運用単位：

```text
Stable Source解決
  → 更新前原文Snapshot
  → SHA-512一致確認
  → 関連DocsをSourceとして再構築
  → Stable更新
  → 更新後原文Snapshot
  → SHA-512一致確認
  → Active Phase変更Record
  → Stable／Phase Index更新
  → Append-only Documentation Index Snapshot
```

History Snapshotは原文保存であり、要約、再解釈、整形またはLink修正を行わない。相対LinkがHistory配置では解決しない場合も、原文Snapshot自体は変更せず、変更Record側へ既知例外を記録する。

同一Phase内で何度更新しても、Timestamp付きFilenameを毎回新規作成する。Timestampなしの既存`docs/public/history/roadmap/roadmap_phase_1_ja.md`はLegacy Historyとして保持し、新規Snapshotで置き換えない。

## 8. Raw Documentation Index

現在の配置：

```text
docs/project/phases/phase_1/history/documentation_index_*.md
docs/project/phases/phase_1_ex/history/documentation_index_*.md
```

Phase 1に76件、Phase 1-exに2件のRaw Indexがある。

これらは本文内の相対Linkが`history/`直下を基準にしている。`history/index/`へ単純Moveすると、`adr/`、`operations/`、`requirements/`、`handoffs/`および旧Index間Linkが一段ずれる。

したがって、現Phaseでは移動しない。

Phase切替時に`history/index/`へまとめる案は保留せず、明示的な再検討事項として維持する。ただし、Raw本文、SHA-512、内部Link、Manifest、Compilationおよび担当TaskのPath解決を同時に維持できる設計を先に確定する。

## 9. Lossless Compilation

Phase単位の「まとめ」は要約ではない。

- Source InventoryとSHA-512を固定する。
- 決定、条件、例外、矛盾、未解決事項を削らない。
- Sourceの意味を再解釈しない。
- 各Source PathとRaw History保持先を解決可能にする。
- 重複・矛盾を新しい単一判断へ勝手に統合しない。
- 配置変更に必要なLocal Linkだけを検証可能な形で正規化する。

## 10. Reconstruction Boundary

Migration時点の非除外Raw Sourceは320件である。

```text
project/内で保持:
  Phase 1 Raw Source     307
  Phase 1-ex Raw Source  11
  Internal Total        318

public/で保持:
  Public Current          1
  Public History          1
  Public Total            2
```

したがって：

- `docs/project/`単独で内部Docs 318件を再構築できる。
- `docs/project/`単独ではPublic 2件の本文を再構築できない。
- `docs/project/`と`docs/public/`を合わせれば、非除外Raw Source 320件を再構築できる。
- `.DS_Store`は意図的な除外Metadataであり、再構築対象ではない。

Whole Documentationの復元単位は`docs/`全体とする。`project/`だけをBackupして完全復元可能と誤認しない。

Migration Evidenceは[Legacy Root Retirement Validation](../../phases/phase_1_ex/operations/documentation_legacy_root_retirement_validation_ja.md)を参照する。

## 11. Role／Write Authority

### 11.1 設計統括者役

主なWrite Scope：

```text
docs/project/current/
docs/project/shared/
docs/project/phases/<active_phase>/phase_index_ja.md
Cross-Phase ADR／Architecture／Requirements
Phase Final Review／Migration／Backup／Git／Release設計
```

Project全体要件、Cross-Phase Architecture、Shared Governance、Role Authority、Project ContinuityおよびPhase構成のOwnerである。

### 11.2 Phase別設計者役

Phase 2以降に必要に応じて配置する。

```text
docs/project/phases/<assigned_phase>/requirements/
docs/project/phases/<assigned_phase>/architecture/
docs/project/phases/<assigned_phase>/adr/
docs/project/phases/<assigned_phase>/operations/
docs/project/phases/<assigned_phase>/history/handoffs/designer_*
```

Current、Shared、他PhaseおよびPublicはRead-onlyとする。Cross-Phase変更は設計統括者役へEscalateする。

### 11.3 実装者役

```text
Primary Write:
  src/
  tests/
  scripts/

Accepted Handoff＋許可時:
  config/
  pyproject.toml
  uv.lock
  Root Metadata

Docs Event:
  docs/project/phases/<active_phase>/history/handoffs/implementer_status_*
```

要件、Architecture、Governance、ADR、Current、Shared、Frozen CompilationおよびPublicはRead-onlyとする。

### 11.4 対外Docs役

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/public/
docs/project/phases/<active_phase>/history/handoffs/external_docs_status_*
```

公開向けに読みやすくしても、要件・Architecture・Governance・ADR・Project Continuityの意味を変更しない。

## 12. Authority Resolution

```text
User Explicit Instruction
  → Task Role／Write Authority Policy
  → Active Phase Accepted Handoff
  → 本書
  → Documentation Rules
  → 設計統括者役へEscalation
```

Write Scopeが不明な場合、他担当領域へ黙って書き込まない。

### 12.1 ユーザー承認済み運用の変更禁止

- User Explicit Instructionは本Project内の最上位Authorityである。
- 設計統括者役、Phase別設計者役、実装者役および対外Docs役は、ユーザーが承認した運用を独断で変更できない。
- 設計統括者役のWrite Scopeは、既存運用に従って文書を管理する権限であり、Docs構造、Append-only保持、命名、Git運用、Role Authority、正本境界、公開境界、削除・退役条件またはTask間伝達方式を無許可で変更する権限ではない。
- ユーザーの明示許可なく運用を変更することを禁止する。
- 必要な変更は、提案、影響分析、保持・Rollback計画、ユーザー明示承認、実施、検証、Append-only変更Recordの順で行う。
- Authority、指示または既存運用が曖昧・競合する場合は、現行運用を維持して作業を停止し、ユーザーへ確認する。
- 無許可の運用変更はGovernance Deviationである。発見時は追加変更を止め、変更対象、失われた可能性のある状態、復旧方法および再発防止を記録する。

## 13. Task間情報伝達

- Task間Handoff、Status、Reviewおよび進捗は原則Docsで伝達する。
- Stable Handoffと実行Eventを区別する。
- Status／Review／NotificationはTimestamp付き新規Eventとして追加する。
- Path変更時は、実装者役、対外Docs役および稼働中の関連Taskへ通知する。
- 通知先は旧Pathの存在を前提にしない。
- 受領確認が必要な変更はAcknowledgementをEvidenceとして残す。

## 14. Phase Lifecycle

```text
Phase Design
  → Implementation
  → Designer Review
  → User Acceptance
  → User Test Acceptance
  → 設計統括者役のPhase完了・次Phase移行可能宣言
  → Design Governance Continuity Refresh
  → Design Governance Reconstruction Validation
  → Phase Backup
  → Public Docs／Git／GitHub更新
```

BackupはPhase完了宣言とユーザーTest合格後に取得する。Backupから`.DS_Store`、`.venv/`、Model、Cache、Secret、Local Override等を除外する。

### 14.1 設計統括者役の完全復元

各Phase完了後、Phase Backup直前に、設計統括者役は次を更新・固定する。

- `docs/project/current/documentation_index_ja.md`
- Current Canonical一式
- `docs/project/current/project_continuity/project_continuity_master_ja.md`
- Shared Documentation Rules／Operations／Role Authority
- Completed PhaseのPhase Index、Compilation、Final ReviewおよびAcceptance
- Active／Next Phaseの目的、Scope、Gateおよび開始条件
- Accepted Decision、Open Finding、Known Limitation、未決事項および保留理由
- Source／Config／Runtime／Model／Deployment／External State
- 実装者役、Phase別設計者役、対外Docs役の復元に必要なHandoff入口
- Secret実値を含まないExternal Service状態とユーザー担当操作
- 主要Artifact Path、Version、SHA-512およびBackup対応

設計統括者役専用Historyへ次の形式でRecovery Manifestを追加する。

```text
docs/project/shared/history/design_governance_handoff/
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

Recovery Manifestは、復元対象文書、Hash、Reading Order、最新Accepted Review、未完了作業、次の一手およびKnown External Dependencyを示す。

新しい設計統括者役TaskによるReconstruction Validationは、次を満たす必要がある。

1. 旧Taskの会話記憶を使わずProject Identity、Current Phase、完了済みPhaseおよび次Phaseを説明できる。
2. 現在有効なRequirements、Architecture、Governance、Role AuthorityおよびDocs運用を解決できる。
3. 最新Accepted Review、Open Finding、未決事項、外部操作境界および次の安全な作業を特定できる。
4. 実装者役、Phase別設計者役および対外Docs役を必要な正本とHandoffから再作成できる。
5. Historyを上書きせず、Current／Shared／Publicの変更前後SnapshotとPhase Development Logを追跡できる。
6. Credential、個人情報または非公開ArtifactをDocsへ埋め込まずに復元できる。

Validation結果を`pass`として記録できない場合、Phase Backupを取得しない。

## 15. RAG Scope

Default：

- Current Canonical
- Active Phase Index
- Completed Phase Compilation
- Public Current
- Shared Rules／Operations

Raw Historyは通常検索対象外とする。監査、Source確認、矛盾追跡またはユーザー明示指定時だけ読む。

Phase 1-exの簡易Documentation RAGはMac限定実装でよい。ただしDocument Source、Chunker、Embedding、Index Store、Retriever、Context AssemblerおよびCitationをPort／Adapter境界へ置き、将来Lightning、Home ServerまたはCloudへ追加Adapterで展開できるHookを最初から予約する。

Public DemoではRAGをLoad／Callしない。

## 16. Migration Status

旧Rootのカテゴリ別重複配置は退役済みである。

次の旧Pathを再作成しない。

```text
docs/adr/
docs/architecture/
docs/governance/
docs/handoffs/
docs/operations/
docs/requirements/
docs/user_manual/
docs/documentation_index_*.md
```

原文はPhase HistoryまたはPublic Historyへ保持している。

## 17. Validation Requirements

Docs構造、移動、Compilation、Phase FreezeまたはPublic Cutover時は、少なくとも次を確認する。

- Source Count
- Target Count
- SHA-512
- Missing／Collision
- Stable／Current Local Link
- Raw History既知例外
- Current／Phase Index到達性
- Identity／Credential／Secret
- RAG Default Scope
- Role Authority
- 担当Task通知
- Rollback／Backup

## 18. Language／Translation

```text
Japanese Canonical:
  docs/project/current/*_ja.md
  docs/public/*_ja.md

English Derived:
  docs/project/current/*_en.md
  docs/public/*_en.md

Japanese Only:
  docs/project/phases/
  docs/project/shared/
  Raw History／Handoff／Status／Review
```

英語版は日本語正本と同じDocumentation Refresh単位で作る。英語版だけで新しい要件や判断を追加しない。

英語版は概要、短縮版または抄訳ではなく、日本語正本と同じ粒度の完全な派生版とする。見出し、要件、根拠、設計判断、制約、例外、留意事項、既知の制限、未決事項および参照先を一対一で保持する。自然な英語表現への調整は許容するが、要約、情報省略、意味変更および再解釈は禁止する。

JA／EN Pairの同等性を確認できない場合、そのCurrent／Public文書は更新完了または公開可能と判定しない。Conflict時の正本は常に日本語版である。

Phase 1-exのCanonical／Public生成Stageより前は日本語版だけの暫定更新を許容する。Initial Commit前RefreshではCurrent／PublicのJA／EN Pairを必須とする。

## 19. Pre-initial Commit Refresh

Git運用は未決定である。Git運用設計はPhase 1-ex後半でよいが、設計案と実際のGit操作は分離し、ユーザーの明示承認前にGit初期化、Commit、Branch、Tag、Remote、Push、公開Repository投入または履歴加工を行わない。

将来Gitを採用しても、GitはAppend-only Development Log、Timestamp Snapshot、Raw Phase History、Phase BackupおよびLossless Compilation Sourceを置き換えない。Rollback可能性を維持するため、これらを全て保持する。

Initial Commit前に、Current／PublicのJA／EN、README、License／Terms、Setup、Public Demo、RAG、Identity、Sanitation、Allowlist、Hash、LinkおよびManifestを最終実装状態へ更新する。

匿名Public AccessはこのRefreshとGit公開準備の完了前に有効化しない。

## 20. Deferred Decision

Phase切替時の検討事項：

```text
Raw documentation_index_*.mdをhistory/index/へまとめるか
```

現時点では、相対Linkと原文Hashを守るため現在位置を維持する。

## 21. Current Index History運用

Current Stable Indexは次を正本入口とする。

```text
docs/project/current/documentation_index_ja.md
```

Current Index本文の変更前後原文は、他のCurrent Stable文書と同じく次へ完全Snapshotとして保存する。

```text
docs/project/current/history/index/
documentation_index_<phase>_<language>_YYYYMMDDHHMMSS.md
```

2026-07-27時点で、ユーザーが次の2件を`history/index/`へ配置した。

```text
documentation_index_phase_1_ex_ja_20260727072019.md
documentation_index_phase_1_ex_ja_20260727072057.md
```

両FileはCurrent IndexのStable Historyとして扱い、既存Historyと同じくImmutableとする。後続更新では、更新前原文と更新後原文を新Timestampで追加し、同一Phase内でも上書きしない。

Active Phase直下のRaw `documentation_index_YYYYMMDDHHMMSS.md`は、Phase全体のDocumentation Snapshotであり、Current Index原文Snapshotとは別Artifactである。Current Indexを`history/index/`へ整理したことを、Phase Raw Indexの移動許可へ拡張しない。

## 22. 累積完全版／Information Preservation

本Projectでは、Docsを単なる説明文ではなく、Project状態、判断、役割、復元手順および将来機会を保持する継続性Artifactとして扱う。

次は情報ロスを一切許さない水準で作成・更新する。

- 既存DocsのLossless再整理
- Current Canonical
- Project Continuity Master
- Shared Rules／Operations／Role／Schema／Template
- Phase Lossless Compilation
- Design Governance Handoff／Recovery Manifest

Stable最新版はDiff-onlyにしない。新しいFileや新版だけで現時点の全有効情報を理解できる、累積・自己完結の完全版とする。

```text
Raw History／Accepted Evidenceを保全
  → Source Inventory／SHA-512固定
  → 更新前Stable完全Snapshot
  → 既存有効情報を維持した累積再構築
  → 新情報／訂正／例外／未決事項を追加
  → Stable更新
  → 更新後Stable完全Snapshot
  → Link／意味／Source対応検証
  → Append-only変更Record／Index Snapshot
```

禁止事項：

- 差分だけを書き、過去Stableを読まなければ意味が解けない最新版
- 読みやすさ、重複除去、簡潔化、Git導入またはFile Sizeを理由にした無断削減
- Acceptedな前提、条件、例外、失敗、未決事項、保留理由または復元情報の脱落
- Project Continuityを簡易Statusだけへ縮小すること
- 別DocsへLinkしただけで、当該正本の目的に必要な説明を全て除くこと

訂正は可能だが、更新前原文をHistoryへ残し、何が旧状態で、なぜ訂正し、何が現在有効かを最新版と変更Recordから追跡可能にする。

この運用を徹底する理由は、情報ロスによる再説明必要化、復元不能状態、判断のやり直しおよび機会損失を防ぐためである。後続版はProjectの進展に応じ、原則として粒度と情報量が増加する。

## 23. Public Stable／History運用

Public Currentと対応Historyは次とする。

```text
docs/public/overview_ja.md
  → docs/public/history/overview/

docs/public/concept_ja.md
  → docs/public/history/concept/

docs/public/roadmap_ja.md
  → docs/public/history/roadmap/
```

Public文書も原則追加式とし、更新前後の完全Snapshotを`<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md`で保存する。

- OverviewはProject概要を伝える。300〜500程度を基準とし、必要に応じて追加する。
- ConceptはOverviewとRoadmapを作成・確認した上で、Projectのコンセプトが十分伝わる粒度にする。
- Roadmapは現在の`roadmap_ja.md`並みの粒度を維持し、Phase、状態、主要機能、研究価値、将来構想およびGateをしっかり記録する。

Public向け編集は情報の順序、説明表現および導線を改善できるが、Projectの独自性や重要な将来構想を意図せず普通のLLM開発へ縮約しない。

## 24. 設計統括者役専用Handoff

Stable入口：

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

History／Recovery Evidence：

```text
docs/project/shared/history/design_governance_handoff/
```

原則として各Phase完了後、Phase Backup直前に、Design Governance Handoff、Current、Shared、Project Continuityおよび関連Phase Indexを累積更新する。続いて同Directoryへ次を追加する。

```text
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

設計統括者役TaskがPhase途中で限界へ近づいた場合は、Phase完了を待たず臨時Refreshしてよい。いずれの場合も、旧Taskの会話記憶を使わず、新しいTaskがProject全体、現状態、Accepted判断、Open Finding、外部操作境界および次の安全な作業を復元できなければならない。

設計統括者役が完全復元できれば、Current／Shared／Phase HandoffからPhase別設計者役、実装者役および対外Docs役も再構成可能であることをAcceptance条件とする。
