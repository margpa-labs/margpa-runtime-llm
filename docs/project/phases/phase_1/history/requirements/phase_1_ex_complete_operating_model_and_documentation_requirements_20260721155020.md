# Phase 1-ex 運用・Documentation・公開再整備 総合要件

- 文書ID: `phase_1_ex_complete_operating_model_and_documentation_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- Architecture: [phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md](../architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md)
- ADR: [adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md](../adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md)
- Lossless Compilation: [lossless_phase_document_compilation_requirements_20260720231036.md](lossless_phase_document_compilation_requirements_20260720231036.md)
- 公開名義・Access・License: [phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md](phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)
- Phase 10 R&D Hook: [phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md](../governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)
- supersedes: `phase_1_ex_operations_reorganization_requirements_20260720231036.md`

## 1. 文書の目的

本書は、これまで複数文書と会話で予約されたPhase 1-exの実施内容を、実行前の総合要件として再統合する。

Phase 1-exは機能追加Phaseではなく、MARGPA Runtime LLMを継続開発、Task分業、Backup、Git、GitHub公開、将来の長期研究開発へ耐えられる運用状態へ移行するPhaseである。

既存の詳細Policy、ADR、Lossless Compilation要件、公開名義・License要件は引き続き有効である。本書はそれらの内容を縮小せず、Phase 1-ex全体の親入口を提供する。

## 2. Phase Identity

```text
Phase ID      : Phase 1-ex
Name          : 運用再整備
Position      : Top-level Phase 1完了後／初回GitHub公開前
Type          : Operations／Documentation／Repository Transition
State         : Accepted Reservation／Not Started
Primary Goal  : 継続開発可能で公開可能な確定運用へ移行する
```

## 3. 現在の非実行境界

ユーザーがPhase 1-ex開始を明示するまでは、次を実行しない。

- 設計者役から設計統括者役への変更
- Phase別設計者Taskの新設
- 役割権限の実変更
- Git初期化、Commit、Tag、Remote設定、Push
- DocsのMove、Rename、削除、Directory Migration
- Stable Canonical Docs、README、LICENSE等の実生成
- Lossless Compilationの実行
- 公開用Staging Treeの生成
- GitHub公開
- Phase 10 R&D機構の実装または統合

現在のAppend-only、Timestamp、Role Authority、Directory構造を維持する。

## 4. Phase 1-ex開始前提

Phase 1-exは、Top-level Phase 1の完了条件と順序を満たした後に開始する。

最低限の前提：

- Phase 1-AからPhase 1-Hまでの対象ScopeがAcceptedである。
- Mac User Acceptanceが合格している。
- Lightning Mandatory Gateと公開UI GateのDispositionが確定している。
- Current User ManualがPhase 1機能を反映している。
- 設計者役がPhase 1完了と次Phase着手可能を宣言している。
- ユーザーがPhase 1最終Test合格を宣言している。
- Phase 1確定SnapshotのBackup要否と実行順が確定している。

Phase 1-ex実行中にPhase 1機能へMaterial Changeが入った場合、必要なReviewとUser Acceptanceを再実行する。

## 5. 役割・Authority再整備

Phase 1-exで次の役割を正式に再整理する。

```text
設計統括者役
Phase別 設計者役
実装者役
対外Docs役
```

### 5.1 設計統括者役

現在の設計者役を、Phase 1-ex内で設計統括者役へ変更する。

責務：

- Project全体要件、Architecture、Phase構成
- Cross-Phase整合
- 共通Port、Governance Core、Security／Privacy Boundary
- Accepted ADR／Policy管理
- Phase開始用上位設計とHandoff
- Phase最終Review、移行判定、Escalation判断
- Stable Canonical Docsの内容責任
- Project Continuity Masterの正本責任

### 5.2 Phase別設計者役

Phaseごとに専用設計者役Taskを配置可能にする。

- 設計統括者役から上位要件、制約、受入境界を受け取る。
- Phase内要件、Architecture、ADR、実装Handoffを具体化する。
- ユーザー要求またはEvidenceにより、上位設計から大きく外れない範囲で再設計できる。
- Cross-Phase影響、共通Policy変更、権限拡大は設計統括者役へEscalateする。

### 5.3 実装者役

- `src／tests／scripts`をStanding Scopeとする。
- `config／pyproject.toml／uv.lock／Root Metadata`はAccepted Handoffとユーザー許可を必要とする。
- Requirements、Architecture、Governance、ADR正本はRead-onlyとする。
- 実装またはFollow-upごとにStatusを作成する。

### 5.4 対外Docs役

- README、公開説明Docs、Phase Summary、CITATION、NOTICEを担当する。
- Lossless Phase Compilationを、決定論的なProcedureに従って実施する。
- Canonicalな技術内容をPublic向けに黙って変更しない。
- Stable Canonical Docsの編集作業を担当する場合も、内容Ownerの設計統括者役によるReviewを必要とする。
- LICENSEの権利条件はユーザー決定を必須とする。

### 5.5 Authority再定義対象

- DirectoryごとのStanding／Conditional Write Scope
- Read-only Scope
- Handoff、Status、Review、Index Ownership
- Git、Backup、Release、Public Export権限
- Phase開始／完了Gate
- Cross-Phase Escalation
- Canonical DocsとDerived Public DocsのOwner
- Project Continuity Masterの更新責任

## 6. Git移行

Phase 1-exからGit運用へ移行する。

Phase 1-exで次を要件定義し、検証してから実行する。

- Repository初期化Point
- Initial Commit Allowlist
- Branch Strategy
- Commit単位、Message規則
- Phase Tag／Release規則
- Backup Snapshot、Manifest、Commit、Tagの対応
- Dirty State Gate
- Remoteと公開Repositoryの対応
- Commit Author／Email／Account帰属
- `.gitignore`、Secret Scan、Binary／Model除外
- Rollback／Restore
- Public Staging TreeとDevelopment Treeの関係
- Git HistoryとDocs Historyの役割分担

公開Repository：

```text
Owner       : margpa-labs
Repository  : margpa-labs/margpa-runtime-llm
Author Name : Nazuna Research
```

Commit Author Nameは`Nazuna Research`とする。Commitから個人GitHub Accountへ辿れることは許容するが、個人EmailやAccount HandleをDocsへ不要に記録しない。

## 7. Documentation運用移行

### 7.1 Filename／Language

Phase 1-ex後に新設または移行するDocsのFile名とDirectory名は英語を使用する。

```text
File／Directory Naming : English／lower_snake_caseを基本
Japanese Body          : Required by default
Language Suffix        : _ja
```

Model ID、Protocol、Class、License、Definition ID等の正式識別子は原表記を保持する。

### 7.2 Git移行前後の履歴モデル

```text
Before Git
  → Timestamp付きAppend-only Docs

After Git
  → Stable Canonical Filenameを更新
  → Git Historyが差分履歴を保持
  → Immutable Phase Compilationは別Artifactとして保持
```

既存Timestamp DocsはHistorical Evidenceとして削除しない。Stable Docsへ再整理したことを理由に、元文書を破壊、上書き、無断要約しない。

### 7.3 Directory Migration

移行前に次を作成する。

- Current File Inventory
- Target Directory Tree
- Current／Historical／Superseded／Conflicting分類
- Move／Keep／Compile／Exclude Manifest
- Relative Link更新計画
- Write Authority Mapping
- Validation Procedure
- Rollback Plan

Directoryを先に変更し、その後に正本関係を考えることを禁止する。

## 8. Stable Canonical Public Documents

Phase 1-exで、対外向け説明と技術正本を兼ねる次の5文書を作成する。

```text
docs/
├─ requirements_specification_ja.md
├─ system_architecture_ja.md
├─ technology_selection_ja.md
├─ basic_design_ja.md
└─ runtime_governance_specification_ja.md
```

### 8.1 `requirements_specification_ja.md`

- Project目的、利用対象、Scope
- 機能要件
- 非機能要件
- Platform／Resource制約
- Security／Privacy／Audit要件
- Model／Governance交換性
- Phase境界、Out of Scope、受入条件
- 未実装機能と将来要件の明示

### 8.2 `system_architecture_ja.md`

- System全体構造
- Layer／Module責務
- Dependency方向
- Application Core、Adapter、Port
- Local／Lightning／Cloud／Hybrid配置
- Data／Control／Event Flow
- Trust／Authority Boundary
- Future External R&D Extension Hookの配置

### 8.3 `technology_selection_ja.md`

日本語文書名は「技術選定書」とする。

- 採用技術、Version、Support Range
- 採用理由
- 不採用／保留候補と理由
- Platform／Backend互換性
- Canonical ModelとDeployment Artifact
- 将来の交換条件
- 関連ADRとの対応
- 既知のRiskと再評価条件

### 8.4 `basic_design_ja.md`

- API、UI、Config、Model、Storage、Governanceの基本構造
- 外部／内部Interface
- Module接続
- State、Error、Cancellation、Securityの基本方針
- Directory／Config／Schemaの基本設計
- 詳細実装へ渡すBoundary

詳細設計書はPhase 1-exの必須成果物にしない。既存Granular DocsとSourceを維持し、将来必要になったSubsystemだけ任意に作成する。

### 8.5 `runtime_governance_specification_ja.md`

- Runtime Governanceの目的と思想
- ARGD／DAGDの位置づけ
- GD 0件でも成立する構造
- 未知のGD、任意JSON、将来GDの汎用受入
- Registry、Loader、Validator、Compiler、Instance
- Shared Control Plane＋Distributed Governance Point
- `off／observe／enforce`
- Layer ON／OFF、依存、競合、Capability
- State、Score、Deviation、Severity、Action
- Audit、Evidence、Repair、Rebind、Enforce、Reinitialize
- 権限やPolicyを新しく生成しないBoundary
- Phase 10 External R&D Hook

### 8.6 作成原則

- 既存正本をSource Inventory化してから作る。
- 決定事項、未決事項、例外、Known Issueを混同しない。
- 未実装事項を実装済みと書かない。
- 読みやすさを理由にAccepted Boundaryを変更しない。
- Stable Docs間の重複は参照で抑制し、正本Ownerを明示する。

## 9. Derived Public Documents／Root Files

対外Docs役が次を作成または更新する。

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

- README本文は日本語の敬語とし、末尾にEnglish Abstractを置く。
- READMEへ実在するLightning公開URLを記載する。架空URLを置かない。
- LICENSEは英語正本を許容する。
- NOTICEは日本語と英語を使用する。
- CITATION.cffは英語でCFF 1.2.0へ準拠する。
- Overview、Concept、Roadmap、Phase Summaryは日本語とする。
- 将来`*_en`を追加可能とするが、現在は必須にしない。

Stable Canonical DocsとDerived Public Docsを混同しない。READMEやOverviewは説明用であり、Canonical Requirementsを置換しない。

## 10. Project Continuity Master

Taskを丸ごと新規作成しても即時再開できるよう、次を作成する。

```text
docs/project_continuity/
└─ project_continuity_master_ja.md
```

本Fileは公開可能なProject Continuity正本とする。

```text
classification : public_project_continuity
public_export   : true
github_public   : include
language        : Japanese
filename        : English
```

最低限、次を統合する。

- Project目的、思想、優先順位
- Current Phase、完了、未完了、保留
- 全ArchitectureとModule責務
- Model、Backend、Artifact、配置
- Platform、Python、Dependency、Deployment Profile
- Config構造、優先順位、Layer ON／OFF
- Runtime Governance全体
- Guardrail、Judge、Repair、Agent、RAG等の将来要件
- 役割、Write Authority、Handoff、Review、Index規則
- Docs、Git、Backup、Release、公開運用
- Public Identity、Repository、License Stage
- Accepted ADR／Decision
- Known Issues、未解決事項、再評価条件
- 次の作業、開始条件、禁止事項
- Task再開時の読込順序
- Source Document Map
- Phase 10 Original R&D Hook

単なる短い要約にせず、Decision、Boundary、例外、未決事項を分離する。運用規則等の意味を勝手に再解釈しない。

公開Fileであるため、個人Path、Credential、Secret、実会話Log、Private Artifactを含めない。公開可能性と継続性を両立する。

## 11. Lossless Phase Compilation

Phase完了ごとに、そのPhaseで作成されたDocsをPhase単位で再整理する。

これはSummary RewriteではなくLossless Compilationである。

- Source SetをFreezeする。
- Path、Document ID、State、Size、SHA-512をInventory化する。
- 元本文を変更せず格納する。
- 統合Fileから元Payloadを再抽出する。
- Byte SizeとSHA-512を比較する。
- 1件でも不一致ならFail Closedとする。
- 矛盾文書も勝手に解消せず、外部Metadataで状態を示す。

Privacy ScrubはCompilation外で明示的に行う。公開用Derived Docsと内部／公開Lossless Compilationの関係をPhase 1-exで確定する。

## 12. 公開名義・Privacy

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
Repository Owner             : margpa-labs
Public Repository            : margpa-labs/margpa-runtime-llm
```

公開候補から次を除外する。

- 法的氏名、個人連絡先、個人Profile
- 個人固有Absolute Path、Hostname、OS Account名
- Credential、Secret、Token、Private Key
- `.venv`、Model Weight、`models` Symlink
- Cache、Bytecode、Coverage、`.DS_Store`
- Local Log、実会話、RAG資料、Local Override

第三者の正式名称、Model ID、Repository、License、Citation、Hashは勝手に置換しない。

## 13. GitHub SourceとLightning UIのAccess境界

### GitHub

- 初期公開はEvaluation-onlyのSource-availableとする。
- Open Sourceとは主張しない。
- 閲覧、評価、Clone、Fork等の範囲をLICENSEで定義する。
- 商用、Production、再配布、派生物、AI Training等の扱いを明示する。

### Lightning Public UI

- 公開UIの通常機能は自由に操作、評価可能とする。
- Prompt、New Chat、公開設定、生成、停止、再試行を許可する。
- UI利用はSource再利用、Model取得、管理Access、妨害行為の権利を付与しない。

## 14. License Staging

初期Stage：

```text
Classification : Source-available／Proprietary Evaluation-only
Open Source     : No
Primary File    : LICENSE
```

一定の完成後、ユーザー判断でOSS化できる。OSS化対象Version、過去Release、Contributor権利、Third-party License、変更日を記録する。

Top-level LicenseをModel、ARGD／DAGD、第三者GD、Dependency等へ一括適用しない。

## 15. Backup／Phase-end／GitHub Sequence

```text
Implementation／Test完了
  → Designer Review
  → User Acceptance
  → Phase完了／次Phase着手可能宣言
  → Lossless Compilation
  → Stable／Derived Public Docs更新
  → Privacy／License／Integrity Review
  → Backup Candidate
  → Archive Sanitation
  → Manifest／SHA-512／Restore検証
  → Backup確定
  → Git Commit／Tag／GitHub反映
```

最終順序は既存Dual Gate Policyとの整合をPhase 1-exで確定する。BackupとGitHubは同一Source Snapshotを指す。

## 16. Public Archive／Repository Exclusion

公開TreeとBackup CandidateをAllowlist方式で作る。

除外対象：

```text
.venv/
models／models Symlink
*.gguf
.git/              # ZIPから除外。Git Repository自体では別管理
Cache／Bytecode／Coverage
.DS_Store
Credential／Secret
var／Local Runtime Data
Temporary／Editor File
Local Override
```

Modelは名称、Canonical Source、Artifact、Revision、Format、Quantization、SHA-512、配置手順だけをManifestへ残す。

## 17. Phase 10 Original R&D Hook

本体の一通りの完成後、別Project／別Taskで開発される次の独立R&D機構を疎結合統合できるHookを残す。

1. 例外認識型安全統治機構
2. 分散証跡型例外認識エージェント統治安全機構

Coreへ固有実装を依存させず、汎用External Governance Provider Port、Capability、Event、Evidence、Standard Resultで接続する。両機構が存在しなくてもMARGPA Runtime LLM本体は完全に動作する。

公開情報量と詳細は[Phase 10 R&D Hook正本](../governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)に従う。

## 18. Migration Validation

Phase 1-exでは最低限、次を検証する。

- InventoryとTarget Tree一致
- Relative Link Check
- Current／Historical正本解決
- Stable Docs相互参照
- Lossless再抽出とSHA-512一致
- Filename English／Body Japanese
- Public Identity／PII／Secret Scan
- Model／Binary／Symlink／Venv除外
- LICENSE／NOTICE／CITATION整合
- CFF Schema Validation
- Reproducible Setup
- Static／Unit／Integration／Native Test
- Archive Manifest／Restore
- Git Clean State／Commit／Tag対応
- Task Handoffからの再開試験
- 各担当TaskへのMigration通知

## 19. Phase 1-ex Completion Gate

次がすべて成立するまでPhase 1-ex完了を宣言しない。

- Role／Authority再編Accepted
- Git Workflow Accepted／実動作確認済み
- Docs Directory Migration完了
- Stable Canonical Docs 5件完成・Review済み
- Project Continuity Master完成・再開試験済み
- Public Root／Derived Docs完成
- Lossless Compilation Procedure合格
- Privacy、License、Attribution、Integrity合格
- Backup／Restore合格
- 全担当Taskへの新構造通知完了
- Rollback手順確認
- ユーザー最終受入
- 初回GitHub公開対象Commit／Tree確定

## 20. Out of Scope

- 詳細設計書の網羅的作成
- Phase 10 R&D機構そのものの実装
- 未公開のR&D Algorithm／核心部分の記述
- OSS化の即時実行
- Model WeightのRepository収録
- Phase 2以降の機能実装

## 21. Authorization Boundary

本書はPhase 1-exの総合要件予約を更新する。

本書作成だけでは、Phase 1-ex開始、Role変更、Git操作、Docs Migration、Stable Docs実生成、README／LICENSE等の生成、Backup、GitHub公開、Phase 10実装を許可しない。
