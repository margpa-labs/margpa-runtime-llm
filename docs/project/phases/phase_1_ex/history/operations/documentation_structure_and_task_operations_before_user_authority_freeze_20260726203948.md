# Documentation Structure／Task Operations

```yaml
document_id: documentation_structure_and_task_operations
status: current
language: ja
created_at: 2026-07-26 17:00:34 JST
updated_at: 2026-07-26 17:53:18 JST
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
│  │  └─ project_continuity/
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
│     └─ task_roles/
└─ public/
   ├─ roadmap_ja.md
   └─ history/
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

現在有効なProject横断正本を置く。Stable Filenameを使い、Git開始後はGit Historyで変更を追跡する。

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

Historyは開発日誌、判断証跡、Task間引き継ぎおよび監査Evidenceを兼ねる。役目が終わったことを理由に完全削除しない。

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
  → Phase Backup
  → Public Docs／Git／GitHub更新
```

BackupはPhase完了宣言とユーザーTest合格後に取得する。Backupから`.DS_Store`、`.venv/`、Model、Cache、Secret、Local Override等を除外する。

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

Git運用設計はPhase 1-ex後半でよい。ただしInitial Commit前に、Current／PublicのJA／EN、README、License／Terms、Setup、Public Demo、RAG、Identity、Sanitation、Allowlist、Hash、LinkおよびManifestを最終実装状態へ更新する。

匿名Public AccessはこのRefreshとGit公開準備の完了前に有効化しない。

## 20. Deferred Decision

Phase切替時の検討事項：

```text
Raw documentation_index_*.mdをhistory/index/へまとめるか
```

現時点では、相対Linkと原文Hashを守るため現在位置を維持する。
