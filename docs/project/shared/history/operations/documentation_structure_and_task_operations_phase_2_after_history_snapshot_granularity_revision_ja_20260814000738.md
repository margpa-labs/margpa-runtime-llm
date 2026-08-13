# Documentation Structure／Task Operations

```yaml
document_id: documentation_structure_and_task_operations
status: current
language: ja
created_at: 2026-07-26 17:00:34 JST
updated_at: 2026-08-14 00:07:37 JST
owner: 設計統括者役
rag_default: true
```

## 1. 目的

本書は、MARGPA Runtime LLMにおけるDocs構造、文書の読み方、History、Phase単位運用、Lossless Compilation、再構築境界、Task間伝達および役割別Write Authorityを一つの共通運用入口へまとめる。

詳細正本：

- [Documentation Rules](../conventions/documentation_rules_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)
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

### 2.1 Project Root外操作の全面禁止

通常のProject作業境界は、次のProject Root内部だけである。

```text
margpa-runtime-llm/
```

Project Root外のPath、Temporary Directory、Desktop、Home Directory、Model置場、Cloud環境、外部Repositoryまたは外部Serviceに対する読取、走査、作成、Copy、変更、削除、Move、Archive、展開、Metadata変更、Permission変更およびCommand実行は、ユーザーが対象とActionを当該作業について明示許可した場合を除き絶対に行わない。

ToolやSandboxが操作を許可していること、担当RoleにWrite Authorityがあること、作業効率が上がること、公開準備に必要と思われること、過去に似た操作を許可されたことは、いずれもユーザー許可の代替にならない。

Project内のSymbolic Linkが外部Pathを指す場合も同様である。Link先を暗黙にProject内部扱いせず、ユーザーの明示許可なしに追跡しない。

### 2.2 Bulk／Sanitation／公開準備の実行順

広範な検査、Sanitation、置換、削除、公開用Copy作成または一括変更は、次のGateを順番どおり通過させる。

```text
Read-only Inventory
  → 検出結果と候補差分の提示
  → 元Project／作業用Copy／公開用Copyの対象確認
  → ユーザーのBackup完了宣言
  → 変更内容の明示承認
  → 承認対象だけを変更
  → Before／After Diffと復旧可能性の報告
```

対象確認またはBackup完了宣言が欠けている場合、ユーザーの依頼に置換・削除の文言が含まれていても実変更へ進まず、Read-only結果を返して停止する。

元Projectを保全したままユーザーがDesktop等へ作業用Copyを作る予定である場合、そのCopyの作成・削除・公開操作はユーザー担当とし、Task側はユーザーからCopy Pathと許可Actionを明示されるまで触れない。

違反発生時は、追加修復、削除、再生成、帳尻合わせまたはEvidence更新を勝手に行わない。直ちに停止し、変更・削除・外部作成Artifactを完全列挙し、ユーザーの復旧指示を待つ。

### 2.3 Research Asset Mutation Control

Project内外のMutationに関する実行Protocolは、[Research Asset Mutation Control](research_asset_mutation_control_ja.md)を正本とする。

全担当の初期Modeは`read_only`である。Mutationは、対象Root、対象種別、対象Path、許可Action、禁止Action、外部Access、Symbolic Link、Before Inventory、Proposed Diff、Backup完了、Rollback、復元不能性および最終承認を保持するMutation Authorization Envelopeが全件成立した場合だけ許可する。

```text
Read-only Inventory
  → Proposed Diff
  → Target Kind／Root Confirmation
  → User Backup Complete
  → Final User Approval
  → Minimal Mutation
  → Before／After Validation
```

Manifest Schema：

```text
../schemas/mutation_authorization_manifest_schema_v1.json
```

人間確認Template：

```text
../templates/mutation_authorization_manifest_template_ja.md
```

本Protocolを、Shell、Patch、Python、Browser、Connector、Git、Cloud、Image Tool、Archive Tool、Sub-agent、別Taskまたは自動化への委譲で迂回しない。

無許可MutationのCostには、Backup増加、保存容量消費、Project横断差分検証、有料AI利用による現金損失、ユーザーの再説明・監督負担、精神的疲労、研究時間喪失、復元不能および研究・公開機会損失を含む。担当が損失規模を把握できない場合、Riskを小さいと推定せず停止する。

### 2.4 Command提示と実行許可の完全分離

「コマンドをくれ」「手順を教えて」「ここに出して」「僕がやる」「キミがやるんではなく」等は、Textの提示だけを許可し、Command／Tool／Filesystem／External Actionの実行を絶対に許可しない。

実行は、当該ターンでユーザーが正確な対象とActionに対し「キミが実行して」等と明示した場合だけ可能とする。否定、訂正、目的の説明、作業の流れ、過去の許可、Approval UI、Sandbox Escalation、Tool PermissionまたはRole Authorityは、実行許可へ読み替えない。曖昧な場合はCommandだけを提示し、ユーザーに操作を残す。

詳細正本は[Research Asset Mutation Control](research_asset_mutation_control_ja.md)第3.1節とする。

### 2.5 推測禁止／100%明確化Gate／Workspace境界

- 「良かれ」「推測」「話の流れ」「過去の許可」「役割上必要に見える」をAuthorizationとして使用しない。
- 意図、対象、Action、Root、Mutation有無、外部Accessまたは副作用に1%でも不明点があれば、当該作業を開始・継続しない。担当内の技術・設計・実装・Docs判断は直属上位Role、Cross-Role／Cross-Phase／委譲境界は最高責任者役、ユーザー意図・最上位規則・Root／Authority拡張・External／Secret／Destructive・Human-only GateはユーザーへEscalateする。
- 本Project作業の外周境界は`MARGPA-RUNTIME-LLM/`とし、その外部へ当該ターンの明示許可なく触れない。
- 外周境界内も、当該ターンで許可されたRoot／Pathだけを作業対象とする。同じ親Directoryに存在することはAccess許可ではない。
- `other/`はユーザー専用領域として許可対象から除外し、明示的な一時解除がない限りRead／List／Search／Stat／Execute／Write／Metadata変更／Symlink追跡の全てを禁止する。
- 未許可DirectoryへCopy Folder、Temporary Artifact、Stage、CacheまたはBackupを勝手に作らない。
- Phase 2以降の半自動／ほぼ自動Orchestration実験は、事前承認済みEnvelope内だけの別運用であり、本原則の例外または現在作業への包括許可ではない。

詳細正本は[Research Asset Mutation Control](research_asset_mutation_control_ja.md)第3.2節および第3.3節とする。

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

Phase IndexまたはCurrent Indexを確定更新するたびに、Active Phaseの`history/index/`へ新しい`documentation_index_YYYYMMDDHHMMSS.md`を追加する。Stable IndexとTimestamp Snapshotは同じDocumentation更新の一組として扱い、片方だけで完了にしない。RoutineなTask／Work UnitごとにStable Indexを更新するのではなく、第7.2節のMaterial Documentation Boundaryで集約する。

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

同一Phase内で複数のMaterial Documentation Boundaryを確定した場合、各BoundaryのTimestamp付きFilenameを新規作成する。Timestampなしの既存`docs/public/history/roadmap/roadmap_phase_1_ja.md`はLegacy Historyとして保持し、新規Snapshotで置き換えない。

### 7.2 History Snapshot Granularity／Material Documentation Boundary

Historyの目的は、情報Loss防止、Rollback、Task再開、正本再構築および監査可能性である。Snapshot件数の最大化それ自体を目的にしない。作業精度または復元性に必要なEvidenceは省略しないが、必要性を示せないRoutineなTask、Subtask、軽微な文言訂正、Test再実行、Review往復またはWork Unitごとに、Stable全文、Phase Index全文およびDocumentation Index全文を反復複製しない。

完全Snapshotの標準単位はTask数ではなく、最高責任者役または当該Document Authorityを持つRoleがRiskと復元性から動的に定める`Material Documentation Boundary`とする。代表例は次である。

- Subphaseの設計Freeze、実装完了、最終ReviewまたはClosure
- 複数Work Unitを束ねるMilestoneまたはMaterial Work Packageの確定
- Stable正本の意味、Schema、Authority、Path、Source of Truthまたは復元境界が変わる更新
- 大規模Mutation、不可逆操作、高Risk MigrationまたはTask交代の直前／直後
- Compact Evidenceだけでは旧Task会話なしの正確な再開が保証できない地点
- ユーザーが完全Snapshotを明示指定した地点

一つのMaterial Documentation Boundaryでは、原則として変更前完全Snapshotを1件、確定後完全Snapshotを1件だけ作る。同じBoundary内の途中状態は、必要に応じて小さなAppend-only Status、Receipt、Review、Correction RecordまたはDelta Manifestへ集約し、Stable全文の再複製で代用しない。CorrectionでStable本文が変わらない場合は、Correction Recordだけを追加し、同一内容の完全Snapshotを作り直さない。

Task／Work Unit単位の中間記録には、少なくとも次のうち再開に必要な項目だけを保持する。

- 現在地、状態および次Action
- 変更対象Pathまたは対象なしの明示
- 最新Validation結果
- 未解決のCurrent Blockerまたは`NONE`
- Authority／Scope／責任移転がある場合のFrom／To
- 再開時に必要な差分、Digestまたは参照先

次のいずれかが成立した場合は、集約より完全Snapshotを優先する。

- 復元不能、情報Loss、Authority混線または正本不明のRiskがある
- 複数Stable文書の整合更新で、部分状態を残すと誤読される
- HistoryやSchemaのMigration、Source Freeze、Lossless CompilationまたはPhase完了Gateである
- Task／Provider／Context喪失時にCompact Evidenceだけでは復旧できない

本節は、Material Documentation Boundaryに対する変更前後Snapshot、Append-only保持、History Immutable、Lossless Compilationおよびユーザー指定Backupを弱化しない。既存Historyを削除、圧縮、統合または遡及変更する許可にもならない。以後は「Taskごとに全文Snapshot」ではなく、「復元性に必要な大きな意味境界ごとに全文Snapshot」を標準とする。

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

主なMeaning Ownership／ユーザー明示時の更新担当Scope：

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

Automation中はユーザー承認済み到達線、Assigned Phase AuthorityおよびWork Unitの内側で、設計判断、担当Implementerへの伝達、局所Review、Finding解決および再作業指示を自律的に行う。通常運転中も同じRole／Docs Authorityを使い、ユーザーが追加または変更した要件を取り込む。例外、重大問題、Scope外、Cross-Phase影響または定義済みGateだけを上位RoleへEscalateし、Routine判断ごとの確認を要求しない。

### 11.3 実装者役

Context、安全性または実装規模上の必要がある場合、Phaseごとに専用実装者役を新規配置できる。

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

実装者役は、Accepted Design、Handoff、許可Path、Source／Test Write Scopeおよび完了条件の内側で、実装方法、局所修正、再Test、担当内EvidenceおよびStatusを自律的に判断する。要件／Architecture変更、Scope外Mutation、重大Finding、受入条件不成立または定義済みReview GateでPhase Designerへ返す。Routine実装ごとにPhase Designerまたは最高責任者役へ確認しない。

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

### 11.5 Docs Authorityの独立解決

Roleの実行権限とDocsの扱いを別の軸で解決する。対象文書を読めることは、そのStable本文、HistoryまたはIndexを変更できることを意味しない。

```text
READ                         : Exact Authorized Docsの読取のみ
CREATE_NEW                   : Work Unit用Index／Handoff／Status等の新規作成
APPEND_NEW                   : Role所有の新規History／Review／Evidence追加のみ
EXISTING_WRITE_USER_EXPLICIT : 既存StableはユーザーのExact Authorization後だけ更新
REVIEW_ONLY                  : Review／Finding作成のみ
DENY                         : 実行不可
```

詳細なDocument Class×Roleの上限表は[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)を正本とする。通常運転とAutomationは同じRole／Docs Matrixを使う。Phase固有のRole Viewは、正本Matrixを書き換えず、Current Authorization Instance、Work UnitおよびExact Pathにより狭いViewだけを作る。

既存Stable文書への直書きはModeを問わず、ユーザーがExact TargetとActionを明示した場合だけ成立する。上位Roleの指示、Accepted Envelope、Meaning OwnershipまたはRole兼務だけでは成立しない。更新時は、更新前Snapshot、Stable更新、更新後Snapshot、Change RecordおよびIndex Snapshotを一つのDocument Transactionとする。

既存Historyは全Roleに対してImmutableであり、新規Event追加Authorityと既存Event Mutation Authorityを分離する。

## 12. Authority Resolution

```text
Human-defined Supreme Rules
  → Current User Direction／User-approved Completion Line
  → Common Role／Docs Authority Matrix
  → Work Unit Index／Handoff／Role View
  → Documentation Rules
  → Scope外はProject Controller／Design Governor／UserへEscalation
```

通常運転ではユーザーがTaskへ要件を追加・変更でき、Project Controllerと担当Roleがその時点の指示へ整合させる。Automationではユーザー承認済み到達線の内側をProject ControllerがWork Unitとして連結し、各Roleは`ROLE_ALLOWED`範囲をActionごとの再確認なしに完了へ進める。

最高責任者役は、Role AuthorityとWork Unitを委譲した後も全Routine Actionの逐次承認者にならない。各Role／Taskは委譲範囲内を自律判断し、例外、Conflict、Scope外、Cross-Phase影響、重大Risk、Resource／Provider異常または定義済みGateだけを直属の上位Roleへ送る。直属の上位Roleで解決できる事項を、さらに上位またはユーザーへ直接Micro-escalateしない。

Modeごとに同じRole権限、Docs権限またはDocumentation判断規則を複製しない。Write Scopeが不明な場合、他担当領域へ黙って書き込まない。

### 12.1 ユーザー承認済み運用の変更禁止

- User Explicit Instructionは本Project内の最上位Authorityである。
- 設計統括者役、Phase別設計者役、実装者役および対外Docs役は、ユーザーが承認した運用を独断で変更できない。
- 設計統括者役のWrite Scopeは、既存運用に従って文書を管理する権限であり、Docs構造、Append-only保持、命名、Git運用、Role Authority、正本境界、公開境界、削除・退役条件またはTask間伝達方式を無許可で変更する権限ではない。
- ユーザーの明示許可なく運用を変更することを禁止する。
- 必要な変更は、提案、影響分析、保持・Rollback計画、ユーザー明示承認、実施、検証、Append-only変更Recordの順で行う。
- Authority、指示または既存運用が曖昧・競合する場合は、現行運用を維持して対象Actionを停止する。担当内の技術・設計・実装・Docs解釈は直属上位Role、Cross-Role／Cross-Phase／委譲境界は最高責任者役、ユーザー意図・最上位規則・Root／Authority拡張・External／Secret／Destructive・Human-only GateはユーザーへEscalateする。
- 無許可の運用変更はGovernance Deviationである。発見時は追加変更を止め、変更対象、失われた可能性のある状態、復旧方法および再発防止を記録する。

## 13. Task間情報伝達

- Task間Handoff、Status、Reviewおよび進捗は原則Docsで伝達する。
- Stable Handoffと実行Eventを区別する。
- 固定されたIndex／Handoff／Status／Review Packageを、全作業、全Roleまたは全Taskへ一律に要求しない。
- 必要Artifactは、当該Document Authorityを委譲されたRole／Taskが、Work Unit種別、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery要件、Provider Capability、情報Loss、復元性、CostおよびContextから都度動的に判断する。Cross-Role対象、競合または上位Gateは最高責任者役が調整する。
- IndexはNavigation／Recovery入口、Handoffは責任／Authority／入力／次Actionの移転、Statusは進捗／停止／失敗／完了／Recovery Stateの永続化、Review／Acceptanceは独立判定、Evidenceは監査／復元／再現性が必要な場合だけ作る。
- 一つのArtifactが複数責務をLosslessに満たせる場合は統合し、必要性を示せないArtifactを作らない。
- Handoff、Status、Review、Request、Acknowledgementその他、Role／Task間で責任、Authority、入力、判定または次Actionを移転するArtifactには、論理的な送信元`from_role`と宛先`to_role`を必須とする。単一Role内記録や機械的Evidenceに意味のないFrom／Toを強制しない。Evidenceを別Roleまたはユーザーへ提出する場合はFrom／Toを付ける。
- Indexを作る場合は`owner_role`、`upstream_role`、`intended_readers`、Work Unit IDおよびStateを記録する。
- Requirements／Designを作る場合はOwnerとDecision Authorityを記録する。
- Status／Review／NotificationはTimestamp付き新規Eventとして追加する。
- Read-only Roleの記録を別Roleが代行する場合も、論理的著者、`from_role`および`to_role`を保持する。
- Path変更時は、実装者役、対外Docs役および稼働中の関連Taskへ通知する。
- 通知先は旧Pathの存在を前提にしない。
- 受領確認が必要な変更はAcknowledgementをEvidenceとして残す。

ArtifactのExact Name、件数または固定Packageを共通CoreへHard-codeしない。許可Document Root／ClassはProject BindingとRole Viewで与え、当該Authorityを持つRoleが必要性を判断して担当内Exact Pathを固定する。Cross-Role対象または競合は最高責任者役が調整する。独立した機械的Resolverを前提にせず、判断責任は通常運転とAutomationで共通とする。この判断は既存Stableへの直書き、既存History Mutation、許可外Document ClassまたはAuthorized Root外へのAuthorityを生成しない。

Task単位の標準完了連鎖は次とする。

```text
Implementer完了報告
  → Phase Designer Review／局所Accepted／必要なら再作業
  → Phase DesignerのTask完了報告
  → Project Controller／Design Governor Review／完了判定案
  → User Acceptance
  → 次のWork Unit
```

初期Automation PilotではTask／有界Work Unit単位でHuman Acceptanceを保持する。Evidence、安全性、安定性および有効性を確認した後、同じ階層契約をSubphase、Phase、Project単位へ段階的に拡張する。

## 14. Phase Lifecycle

```text
Phase Design
  → Implementation
  → Designer Review
  → Phase Final Check
  → Finding解決／Follow-up／再Review
  → 例外的に延期するItemの完全記録／ユーザー承認
  → User Acceptance
  → User Test Acceptance
  → 設計統括者役のPhase完了・次Phase移行可能宣言
  → Design Governance Continuity Refresh
  → Design Governance Reconstruction Validation
  → 設計統括者役が「Phase Backupを取得してください」と明示
  → Phase Backup
  → Backup Manifest／Hash／Restore Verification
  → Public Docs／Git／GitHub更新
```

Phase Final Checkは個別Subphase Reviewの結果だけでなく、Phase全体の要件、統合、Test、Cross-environment、Security／Privacy、Docs、Recovery、Open Findingおよび次Phase入口を検査する。Findingは原則として当該Phase内で全て解決する。`non-blocker`のLabelだけで延期せず、安全性、受入条件、正確性、互換性および復元性に未解決影響がないことを検証し、影響、理由、Owner、対応Phase、再開条件、検証方法およびユーザーの明示承認が揃った場合だけ例外的に延期できる。

BackupはPhase完了宣言とユーザーTest合格後に取得する。設計統括者役は、ユーザーが自発的にBackupを取得する予定であっても、Gate到達時に必ず取得を促し、完了報告を推測で代替しない。また、Directory Migration、Bulk Edit、Schema／Storage変更、Git／公開変更、Cloud再構築、破壊的操作、長期作業またはTask不安定化等の規模・Riskに応じ、Phase途中でもBackup Checkpointを勧告する。Phase途中のBackupは最終Phase Backupを代替しない。Backupから`.DS_Store`、`.venv/`、Model、Cache、Secret、Local Override等を除外する。詳細正本は[Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)とする。

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
  docs/project/current/**/*_ja.md
  docs/project/shared/**/*_ja.md
  docs/public/**/*_ja.md

English Derived:
  docs/project/current/**/*_en.md
  docs/project/shared/**/*_en.md
  docs/public/**/*_en.md

Japanese Only:
  docs/project/phases/
  **/history/**
  Raw History／Handoff／Status／Review
```

英語版は日本語正本と同じDocumentation Refresh単位で作る。英語版だけで新しい要件や判断を追加しない。

英語版は概要、短縮版または抄訳ではなく、日本語正本と同じ粒度の完全な派生版とする。見出し、要件、根拠、設計判断、制約、例外、留意事項、既知の制限、未決事項および参照先を一対一で保持する。自然な英語表現への調整は許容するが、要約、情報省略、意味変更および再解釈は禁止する。

英語版を当該Refreshの作成対象へ含めた場合は、JA／EN Pairの同等性を確認できないCurrent／Shared／Public文書を当該英語版作成作業の完了と判定しない。Conflict時の正本は常に日本語版である。

Phase 1-ex Stage 6で作業余力がある場合は、Current／Shared／Publicの非History Stable文書について`_en`派生版を作る。作成すると決定した場合は、概要・抄訳ではなく日本語正本と同じ粒度で一式を作る。余力がない場合は後日またはPhase 2前半へ延期し、英語版未作成をPhase 1-ex、初回Commit、BackupまたはPhase 2移行の自動Blockerにしない。

`docs/project/current/history/**`、`docs/project/shared/history/**`および`docs/public/history/**`は、英語派生版の対象から再帰的に除外する。

## 19. Pre-initial Commit Refresh

Existing Repository継続、Historical Contributor保持、専用SSH経路、Source→Target Integration、Branch／Commit／Draft PR／Merge、Publication Sanitation、Direct `main`のRisk-based例外、Backup対応、Push Gate、Remote Postflightおよび単一Git Root移行はAcceptedである。設計案と実際のGit操作は引き続き分離し、ユーザーの対象ごとの明示承認前にCopy、Delete、Git Add、Commit、Branch、Tag、Push、Merge、History RewriteまたはRemote変更を行わない。

将来Gitを採用しても、GitはAppend-only Development Log、Timestamp Snapshot、Raw Phase History、Phase BackupおよびLossless Compilation Sourceを置き換えない。Rollback可能性を維持するため、これらを全て保持する。

Git管理開始後も、Phase Final Commit／Push前に、Current／Shared／Public、README、License／Terms、Setup、Public Demo、RAG、Identity、Sanitation、Allowlist、Hash、Link、Manifestおよび承認済みLanguage Scopeを最終実装状態へ更新する。

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

## 25. Shared Categoryの使用条件

次は任意Categoryである。

```text
docs/project/shared/schemas/
docs/project/shared/templates/
docs/project/shared/user_manual/
```

必要なSchema、TemplateまたはPhase横断User Manualがある場合だけ使用する。不要な場合は使わなくてよく、Directoryの存在を理由にArtifact作成を強制しない。

Artifactを作成・更新した場合は、対応する次のHistoryへ変更前後原文を保存する。

```text
docs/project/shared/history/schemas/
docs/project/shared/history/templates/
docs/project/shared/history/user_manual/
```

Docs運用は既存の`docs/project/shared/operations/`を専用Stable Categoryとし、変更前後原文は`docs/project/shared/history/operations/`へ保存する。命名、言語、Immutable性等の純粋な規約は`shared/conventions/`に置き、Operationsから参照する。

権限管理は既存の`docs/project/shared/task_roles/`を専用Stable Categoryとし、変更前後原文は`docs/project/shared/history/task_roles/`へ保存する。

既存専用Categoryがあるため、意味が重複するDocs Operations用DirectoryまたはAuthority用Directoryを追加しない。

## 26. Public Roadmap Lifecycle

最新版はTimestampなしのStable Filenameとする。

```text
docs/public/roadmap_ja.md
```

更新時は、更新前と更新後の完全原文だけを次の形式でHistoryへ保存する。

```text
docs/public/history/roadmap/
roadmap_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Stable最新版自体をTimestamp付きFilenameへ変更しない。

Roadmapを更新する際は、毎回次を再評価する。

1. 現在の進捗
2. 完了済み／進行中／未着手／保留／再評価待ち
3. Active Phase／Next Phase
4. Phase Gate、Backup、公開およびGit状態
5. 新規追加された要件
6. 既存要件の変更、優先順位および移動先
7. 将来の研究機能、独立R&D HookおよびPlatform拡張
8. Known Limitation、Dependencyおよび留意事項

新規要件を漏らさない。後続Phaseへ移動した要件は削除せず、状態と移動先を示す。Roadmapを「最初に予定したPhase一覧」だけへ固定せず、Projectの現在進捗と要件増加を累積反映する。

## 27. Phase 2以降のHistory Index予約

Phase 2開始時から、各PhaseのIndexは次へ分離する。

```text
docs/project/phases/<phase>/
├─ phase_index_ja.md
├─ index/
│  └─ Phase Lossless Compilation等
└─ history/
   └─ index/
      └─ documentation_index_YYYYMMDDHHMMSS.md
```

役割：

- `phase_index_ja.md`：現在のPhase状態へ入るTimestampなしStable入口
- `index/`：PhaseのLossless Compilation等
- `history/index/`：Phase Index更新に対応するAppend-only Documentation Index Snapshot

Phase Index更新時は、Stable更新前後の保存規則に加え、新しいDocumentation Index Snapshotを`history/index/`へ追加する。新Snapshotは旧Snapshotを上書きしない。

本規則はPhase 2開始から適用する。Phase 1／Phase 1-exの既存Raw `documentation_index_*.md`は現在位置と内部相対Linkを維持し、別途ユーザー承認を得たMigrationなしに遡及移動しない。

## 28. 全Stable文書のFilename原則

TimestampなしのStable Filenameを維持する規則はRoadmapだけに限定しない。次の全てへ共通適用する。

- `docs/project/current/`のCurrent Canonical
- `docs/project/shared/`のShared Stable
- `docs/public/`のPublic Current
- 各Phaseの`phase_index_ja.md`
- Phase Requirements／Architecture／Governance／ADR／Operations等のStable文書
- Phase単位Lossless Compilation
- 既存DocsのLossless再整理後に作る最新版正本
- Project Continuity Master
- Design Governance Handoff

最新版の入口は、人間、TaskおよびRAGが固定Pathから解決できるTimestampなしFilenameとする。

```text
Stable Latest:
  <descriptive_stable_name>_<language>.md
  phase_index_ja.md

History／Event:
  <stem>_<phase>_<language>_YYYYMMDDHHMMSS.md
  descriptive_event_YYYYMMDDHHMMSS.md
  documentation_index_YYYYMMDDHHMMSS.md
```

Timestampを付けるのはHistory SnapshotおよびEvent Artifactだけである。Stable最新版へTimestampを付けて新しいFileを増やし、どれが正本かをFilename比較で判断させる運用にしない。

`roadmap_ja.md`はこの共通規則の説明に使用した例の一つであり、Roadmapだけの特別扱いではない。

## 29. 再構築区分と二周方式

Project全体の大規模再構築は、一括上書きではなく次の区分へ分け、各区分でBefore／After Snapshot、SHA-512、Link、Source Scopeおよび情報欠落を確認する。作業中にSource量や依存関係が判明した場合は、区分を5、6またはそれ以上へ安全に再分割できる。ただし対象Artifactを黙って落とさない。

```text
区分1:
  Source Inventory
  Project Continuity Master 第1周
  Roadmap 第1周

区分2:
  Current Canonical全体

区分3:
  Phase 1 Final Lossless再整理
  Phase 1-ex Interim Lossless再整理

区分4:
  Shared全体

区分5:
  Project Continuity Master 第2周
  Roadmap 第2周
  Overview／Concept／README

区分6:
  LICENSE
  TERMS_OF_USE
  NOTICE
  CITATION
  Corpus全体検証
```

Project Continuity MasterとRoadmapは最初と最後の二周を必須とする。第2周は、途中で作成されたCurrent、Phase Lossless、Shared、PublicおよびLegal状態を反映し、第1周の情報を削らない。

## 30. Phase 1／Phase 1-ex Losslessの現在入口

Phase 1は完了済みのFinal Compilation、Phase 1-exは進行中のInterim Compilationとして分離する。

```text
Phase 1:
  docs/project/phases/phase_1/lossless/
    phase_1_lossless_ja.md
    phase_1_lossless_manifest.json

  Source Count       : 316
  Source Bytes       : 5,206,317
  Verification       : 316 / 316 pass
  Compilation SHA-512:
    f0e5875b28d06425a9a5eb31c2004c976738f0236fc45acfd7712d6673d2d60f449f44bc6193643220590644369762bc2f2c9cf2aabf90bf0577084366793705

Phase 1-ex:
  docs/project/phases/phase_1_ex/lossless/
    phase_1_ex_interim_lossless_ja.md
    phase_1_ex_interim_lossless_manifest.json

  Status             : interim / current-to-date
  Source Count       : 145
  Source Bytes       : 3,926,195
  Verification       : 145 / 145 pass
  Compilation SHA-512:
    1dfc8fc71eea947e61c75502cadc31b5d993f4a9834b23571cacf65aacf99a11913bb3333bdcb26dfb55a72a2f5120f623fb925b282cea2968fe026ab0cfc38c
```

Phase 1-ex完了時は、Interimを上書きしてFinalと偽装せず、Phase途中以後の追加ArtifactをSource Freezeへ含めたFinal CompilationとManifestを新しい作業単位として作る。

## 31. 件数基準の世代分離

本書第10節の320件は、2026-07-26の旧Root Migration時点における非除外Raw Source件数であり、そのMigrationの整合性を説明する歴史的基準である。

2026-07-27の大規模再構築開始時Source Inventoryは、Docs 493件とDemo Image 6件の合計499件である。これはMigration後に追加されたPhase 1-ex History、Current／Shared Stable、Snapshot、EvidenceおよびAssetsを含む。

異なるFreeze時点の件数を直接一致させない。検証時は次を必ず指定する。

- Freeze Timestamp
- Included Root
- Exclusion Pattern
- Entry Count
- Entry-list SHA-512
- Manifest SHA-512

最新Source Inventory：

- `docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_inventory_20260727093727.md`
- `docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_source_inventory_20260727093727.json`

## 32. 現在の公開準備境界

2026-07-27時点で次は完了していない。

- Phase 1-ex完了
- Phase 1-ex Final Lossless Compilation
- Project Continuity／Roadmap第2周
- Public Overview／Conceptの確定
- READMEの現行公開版
- LICENSE／TERMS_OF_USE／NOTICE／CITATIONの現行公開版
- Mac限定簡易Documentation RAG
- Git運用設計の承認
- Git初期化、Commit、Remote、Push
- 匿名Public Demo
- Lightning Traffic-aware Wake-upの実証

したがって、Current／Shared／Phase Losslessが再構築済みであることを、Phase 1-ex完了、公開可能、法的条件確定またはGitHub公開済みと読み替えない。

上記一覧は2026-07-27時点のBaselineである。2026-08-04時点では、Root公開Artifact、低発見性調整、Lightning Traffic-aware Wake-up、Public Demo、Mac／Lightning Documentation RAG、Existing Repository History継承、Source→Target Integration、Publication Sanitation、Draft PR／Merge、追加Docs Commit／Pushおよび単一Git Root移行まで完了している。Phase 1-ex Final Lossless、最終Docs Refresh、全体Review、User Acceptance、Phase Final Backupおよび完了Tag／Release判断は引き続き未完了である。現在値はCurrent Documentation IndexとPhase 1-ex Indexを優先する。

## 33. GitHub Publication Sanitation Timing

GitHub公開時のIdentity、Affiliation、Personal Informationおよび不要Artifactの検査・除外時点は、[GitHub Publication Sanitation Policy](git_publication_sanitation_policy_ja.md)を正本とする。

2026-08-02のユーザー決定により、旧個人Account Handle、作者個人情報その他の識別可能情報、意図しない組織名および`.DS_Store`等を目的とした広範Scan／Cleanupは、通常開発やPhase途中更新のたびには行わず、GitHub Push Preparation Gateでだけ実施する。

GitのHistory特性上、「Push時」は送信Command直前だけではなく、Push対象Commitを作る前からRemote反映後検証までの一つのPublication Unitを意味する。Working Treeだけでなく、初回Root Commit全体または全Outgoing Commit Tree／Metadataを検査する。

本変更は、Secret／CredentialのFail-closed取扱い、BackupのAllowlist、Model／`.venv`／Cache除外、Research Asset Mutation Control、第三者Attribution保持およびユーザーのExternal Action Authorityを弱化しない。

## 34. Task Execution Routing／Cost Control

作業の実行面は、意味判断、Mutation Risk、反復性およびExternal Operationの有無に応じて選ぶ。正本は[Task Execution Routing／Cost Control](task_execution_routing_and_cost_control_ja.md)とする。

```text
設計統括者役:
  方針、Contract、Authority、Handoff、Review、例外判断

Phase別設計者役:
  Assigned Phaseの局所設計、Handoff、Review

Codex実装者役:
  Source／Test／Script／Config実装、複数File変更、Repository整合

通常GPT＋ユーザー手動:
  確定Command、Read-only調査、外部UI、配置／Permission／Hash確認

Script:
  反復する定型作業、Preflight、Lifecycle、Evidence収集
```

通常GPTへ渡せるのは、対象、Action、禁止事項、期待結果、停止条件およびEvidence形式を設計統括者役が固定できる作業である。失敗時の推測修復、追加削除、Permission緩和、Path変更または別Commandへの独断切替を許可しない。

Codex利用可能量、Cloud Credit、ユーザー時間および再説明Costを抑えるため、単純なRead-only確認だけに高文脈の実装Taskを使い続けない。一方、Cost削減をAuthority、Safety、Backup、ReviewまたはResearch Asset Protectionより優先しない。

## 35. Git管理開始後のDocs Lifecycle

Git管理開始後も、Stable／History／Phase Index／Lossless／Backupの文書Lifecycleは変更しない。

```text
Stable更新前Snapshot
  → Stable累積更新
  → Stable更新後Snapshot
  → Phase Event Record
  → Phase Index更新
  → Append-only Documentation Index Snapshot
  → Link／SHA-512／Privacy／Git Diff検証
  → ユーザーがCommit／Pushを別途判断
```

`margpa-runtime-llm`が単一Canonical Git Rootである。旧Git Staging Rootは退役済みであり、Docs更新のたびにSource→Stagingへ同期しない。

Git DiffはReviewとRemote配送のEvidenceであるが、旧Task会話に依存しない完全復旧に必要なCurrent、Shared、Phase History、Lossless Compilation、Recovery ManifestまたはBackupを置換しない。

小規模Docs／Metadata更新でDirect `main`を使う場合も、更新前後SnapshotとAppend-only Indexを省略しない。新機能、大規模再構築、高Risk、Phase統合または複数RoleのReviewが必要な変更はBranch／Draft PRを原則とする。

## 36. Phase 2 Index／Constitution予定構造

Phase 2以降のPhase固有Append-only Documentation Index Snapshotは次へ保存する。

```text
docs/project/phases/<phase>/history/index/
documentation_index_YYYYMMDDHHMMSS.md
```

Phase 2の最初のSnapshotから適用し、`history/`直下へ新規作成しない。Phase 1／Phase 1-exのRaw Indexは遡及移動しない。

Agent／Tool本格実装前に作成するPortableな統合憲法書のCanonical予定配置は次とする。

```text
docs/project/shared/constitution/
docs/project/shared/history/constitution/
```

`constitution/`はStableな統合憲法体系、Manifest、Capability Contract、Provider Adapter、Role別View、SchemaおよびTemplateを持つSelf-contained Package候補である。単一巨大Markdownにはせず、`constitution_index_ja.md`を正本入口として、Scope／優先順位、絶対禁止、Authority、Docs正本、Task Lifecycle、Mutation、Resource、Stop／Recovery／Backup、Evidence、Agent／Tool、Exceptionおよび改憲を章別に分離する。`shared/history/constitution/`は変更前後SnapshotとVersion Migration EvidenceをAppend-onlyで保持する。

各Normative RuleはRule ID、対象、規則、検知、違反時動作、復旧、EvidenceおよびSource Traceを持つ。Agent／Tool／TaskへはCanonical全文の手Copyではなく、同じ正本RevisionとDigestからRole／Phase／Task別`Constitution View`を生成する候補設計とする。

現時点では予定構造だけをAcceptedし、Dummy File、空Directory維持用Artifactまたは未完成の憲法書を作成しない。作成時は[Cross-project Development Governance Constitution Plan](cross_project_development_governance_constitution_plan_ja.md)に従う。

## 37. Project Responsibility Handoff Structure

設計統括者役のStable／Historyを保持したまま、Project全体のPhase Gate、Role編成、Cross-Phase継続性およびRecovery用に次を配置する。

```text
docs/project/shared/
├─ design_governance_handoff/
│  └─ design_governance_handoff_ja.md
├─ project_responsibility_handoff/
│  └─ project_responsibility_handoff_ja.md
└─ history/
   ├─ design_governance_handoff/
   └─ project_responsibility_handoff/
```

プロジェクト責任者役Handoffは設計統括者役Handoffの改名、置換または要約版ではない。前者はProject編成／Phase Gate／複数Role再構成、後者はTechnical Design／Canonical Docs／Phase設計復元を担う。両方のRecovery Manifestを正本とDigestで相互参照する。

各Stableの更新前後は対応Historyへ完全Snapshotを保存する。原則として各Phase完了後かつPhase Backup直前に両Recovery Manifestを更新し、旧Task会話なしで新TaskがProject責任と設計統括の両方を復元できるかを検証する。
