# Phase 10 PADG Package導入Profile・Phase Lifecycle・既存Docs統合予約

```yaml
document_id: phase_10_padg_deployment_profiles_phase_lifecycle_and_document_integration_reservation_20260910103654
document_type: append_only_planned_work_history
document_state: accepted_user_direction_not_started
language: ja
recorded_at: 2026-09-10 10:36:54 JST
decision_authority: user
target_phase: phase_10
target_package: Portable Autonomous Development Governance Package
target_package_short_name: PADG Package
stable_counterpart: docs/project/shared/planned_work/phase_10_padg_deployment_profiles_phase_lifecycle_and_document_integration_reservation_ja_20260910103654.md
extends:
  - phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_20260828091200
  - phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_20260909075701
implementation_authorized: false
external_write_authorized: false
git_authorized: false
```

## 1. 決定の目的

Phase 10でPADG Packageを作成する際、完全新規Project、既存Project、既存Docsが変更禁止のProject、および特許出願前の非公開運用を、一つの導入方式に強制せず扱えるようにする。

導入方式は単一のDirectory配置にHard-codeせず、ProjectのDocs管理方針、公開状態、変更Authority、既存Docsの正本境界に応じて選べるDeployment Profileとして設計する。

本予約は既存のPADG二周編纂、Provider-neutral Core、Provider Adapter、Sanitization、Source Traceability、Recovery HandoffおよびAuthority境界を変更しない。導入、既存Docs連携、Phase骨格および公開前運用の仕様候補を追加する。

## 2. 標準Phase Lifecycle

PADGを適用するProjectは、原則として`Phase 1`から`Phase 10`までを共通のLifecycle Slotとする。

```text
Phase 1〜10  : 標準Lifecycle骨格
Work Unit数  : Projectの規模とRiskに応じて可変
Evidence強度 : 影響、可逆性、Authorityおよび受入条件に応じて可変
Phase 11以降 : Phase 10までで不足する場合にのみ追加
```

共通化するのはPhaseの存在とLifecycle上の位置であり、各Phaseの文書量、Work Unit数、実装量まで均一にしない。小規模Projectでは短いPhaseや少数のWork Unitを許容し、形式を満たすためだけに過大な儀式を生成しない。大規模Projectでは依存関係とGateを根拠にPhase 11以降を追加する。

### 2.1 新規Project

- PADGが初回RoadmapとPhase 1〜10の骨格を構成する。
- Project規模が小さくてもPhase番号体系を別系統に分岐させない。
- Phase 10以降が必要ない場合も、空の大作業を捏造せず、該当Phaseの目的とDispositionを明示する。

### 2.2 既存Project

- 既存のRoadmap、Current Position、Accepted State、必要なDocsおよび実装状態を有界にDiscoveryする。
- 見つかった情報から現在地を復元し、Phase 1〜10へ再配置したRoadmap候補を作る。
- Existing Project Onboarding、Current State Reconstruction、Docs Authority確定およびRoadmap再構成は、`Phase 1-EX`のような別Phaseを作らず、通常のPhase 1内のWork Unitとして扱う。

### 2.3 `Phase 1-EX`の非移植

現Projectの`Phase 1-EX`は、開発Agent運用を導入した過程で生じたProject固有の履歴である。PADGの標準Phase体系としては移植せず、一般化可能な内容をPhase 1へ統合する。

現ProjectのRaw HistoryとPhase Identityを後から破壊的にRenameまたは削除するという意味ではない。PADG側のPortable Lifecycleに`Phase 1-EX`をCanonical Slotとして導入しない、という境界である。

## 3. Deployment Profile

### 3.1 Private Sidecar

特許出願前の非公開運用における既定Profile候補とする。

```text
<project-root>/
├─ <existing-document-root>/   # 既存ProjectのDocs正本
├─ .padg/                      # PADG作業領域候補、Repositoryから除外
│  ├─ manifest/
│  ├─ phases/
│  ├─ current/
│  ├─ shared/
│  ├─ history/
│  ├─ evidence/
│  ├─ imported_index/
│  └─ publication_staging/
└─ <source and other project assets>
```

- `.padg/`はDirectory名候補であり、Phase 10の導入設計でConflictと既存用途を確認してFreezeする。
- PADG内部状態、Evidence、Recovery、Handoffおよび公開前候補はPrivate Sidecarに保持する。
- 既存Docsを無条件に丸ごと複製しない。原文保存が必要なSourceのみImmutable Snapshot化し、通常はSource Index、DigestおよびMappingで追跡する。
- CommitまたはPush前に、公開可能と確定した成果物だけを`publication_staging/`から既存Docsへ明示的にExportする。
- SyncやExportは自動Authorityにせず、対象、差分、公開境界および承認を持つ。

### 3.2 Embedded Overlay

既存Document Root内にPADG専用名前空間を追加できるProject向けとする。

```text
<existing-document-root>/
├─ <existing-project-structure>/
└─ padg/
   ├─ phases/
   ├─ shared/
   ├─ history/
   └─ evidence/
```

- 既存構造は保持し、PADGは原則として名前空間内だけを管理する。
- 同一文書の常時二重保存は行わず、既存構造に必要な成果物のみExportする。
- 既存ProjectのRuleとPADG側Ruleを暗黙にMergeしない。

### 3.3 Managed Migration

既存Docs管理をPADG構造へ移管してよいProjectだけで使用する。元案の「PADG側で編成後に既存DocsをArchive化し、必要に応じてPADG管理領域を`docs/`等の正式Rootへ切り替える」方式をここに含める。

- 既存DocsのSource InventoryとAuthorityを確定する。
- PADG構造へのTransformation Mappingを作る。
- 既存原文をImmutable Archiveとして保存する。
- Link、Digest、Coverage、Conflict、Rollbackおよび移行先を検証する。
- ユーザーの明示承認後にのみCanonical Rootを切り替える。
- Directory Rename、既存RootのArchive化および正本切替は破壊性が高いため、既定にしない。

### 3.4 Greenfield Native

完全新規Projectで、PADGが初めからDocs正本を管理できる場合に使用する。

- 初回からPADGのDocs、Phase 1〜10、History、Evidence、RecoveryおよびHandoff構造を使用する。
- 既存Docsとの同期を前提にしない。
- 将来のProject固有Docs構造に対するExportは、別のPublication Mappingとして扱う。

## 4. Profile選択条件

Profileは少なくとも次の入力から決定する。

- 完全新規Projectか既存Projectか。
- 既存Document Rootの有無、正本性および変更可否。
- ProjectのDocs Policyが`immutable`、`append_only`または`managed`のどれか。
- PADGをRepository内で公開できるか、非公開・Git除外が必要か。
- 特許出願前か、出願後または公開可能状態か。
- Copy、Move、Rename、Archive、Export、GitおよびProject Root外WriteのAuthorityがあるか。
- Rollback、Source Traceability、Privacy、SecretおよびPublication Sanitationを成立させられるか。

推奨選択は次のとおりとする。

```text
特許出願前・非公開運用                    -> Private Sidecar
新規ProjectかつPADGにDocs管理を委ねる     -> Greenfield Native
既存Docs内へ専用名前空間の追加のみ許可   -> Embedded Overlay
既存Docsの正本移行を明示的に許可         -> Managed Migration
既存Docsが変更禁止                         -> Private Sidecar + Exportなし
```

PADGの存在、Tool Permission、Filesystem Permissionまたは技術的な書込可能性は、Profile選択、Docs変更またはMigration許可を自動生成しない。

## 5. Document Root Discovery

`docs/`という名称をProject-neutral CoreへHard-codeしない。既存Projectでは、例えば次を候補として探索する。

```text
docs/
documentation/
doc/
wiki/
design/
architecture/
README、Project ManifestまたはBuild Configから参照されるDocument Root
```

Discoveryは次の状態を区別する。

```text
not_found
single_candidate
multiple_candidates
conflicting_candidates
immutable_documentation
append_only_documentation
managed_documentation
```

- 複数候補から「それっぽい」ものを勝手に正本化しない。
- History、Archive、BackupおよびGenerated OutputをCurrent Canonicalと混同しない。
- 候補、判定根拠、Conflict、Authorityおよび確定結果をProject Manifestに保存する。
- Document Rootがない新規Projectでは、存在しないDocsを捏造せず`not_found`として扱う。

## 6. Canonical Ownershipと同期の境界

既存Docs、PADG内部状態および公開候補の正本関係を明示する。

```text
Existing Project Docs    : Projectが現在定める正本
PADG Internal State      : PADG領域内のEvidence、Recovery、Handoff、Manifestの正本
Publication Staging      : 公開・同期候補。既存Docsの正本ではない
Exported Artifact        : 承認済みで既存Docs側へ適用した成果物
Immutable Source Snapshot: 必要性とAuthorityが成立した場合のみ作る原文保存
```

同期には少なくとも次を持たせる。

- Source PathとTarget Path。
- Source DigestとExported Digest。
- Source Revisionと最終確認時刻。
- AuthorityとApprover。
- Sanitization、ExcludeおよびTransformation Mapping。
- `not_exported`、`staged`、`approved`、`exported`、`stale`、`conflict`等の同期状態。
- Rollbackまたは復元元。

「どちらが新しいか」だけで正本を決めず、Authority、Document Class、Accepted Correction、Active HandoffおよびProject Policyを維持する。

## 7. Project Manifestの候補Field

Exact SchemaはPhase 10で確定するが、少なくとも次の意味を保持する。

```yaml
document_policy: immutable | append_only | managed
deployment_profile: private_sidecar | embedded_overlay | managed_migration | greenfield_native
padg_visibility: private_ignored | repository_visible
publication_mode: disabled | manual_export | approval_required
existing_document_roots:
  - path: <discovered path>
    authority: project_canonical | reference_only | unknown
    state: current | history | archive | generated | conflicting
source_traceability:
  digest_required: true
  immutable_snapshot: conditional
```

これは説明用の予約形であり、現時点の正式JSON Schema、Default Value、Migration ToolまたはAutomatic Authorityではない。

## 8. 二重管理を抑える原則

- 既存DocsをPADGへ丸ごとCopyし、両方を恒常的な正本として更新する方式を既定にしない。
- 既存Docsが大きい場合も、ストレージ消費とStale Copyの増殖を避ける。
- Symbolic LinkはPlatform、Permission、Archiveおよび配布環境での差異があるため、Project-neutralな唯一の連携方式にしない。
- 必要なSourceを都度Readし、Index、Digest、Mapping、必要なSnapshotおよびExport済みArtifactで関係を維持する。

## 9. 特許出願前後の運用

### 9.1 特許出願前

- Private Sidecarを既定候補とする。
- PADG Packageとその内部設計、Evidenceおよび公開前ArtifactをRepositoryから除外できる構造にする。
- Git Ignore対象とするのは、そのProjectのPolicy、Repository Root、既存Ignore Ruleおよびユーザー承認を確認した後とする。
- CommitまたはPush前のExportは、「PADG全体を移す」のではなく、公開可能でProjectの正本に必要な成果物だけを選ぶ。
- Export対象とPADG内部の非公開設計を混同しない。

### 9.2 特許出願後または公開準備後

- PADGをRepository-visibleにするか、引き続きSidecarとするかをProjectごとに決める。
- Docs管理が許すならEmbedded OverlayまたはGreenfield Nativeを選べる。
- Managed Migrationは、公開済みであることだけで自動許可せず、移行の必要性とDocs変更Authorityを別途確認する。
- 公開状態の変更は、元ProjectのDocs Policyを上書きしない。

## 10. 受入条件候補

PADG導入設計のAcceptanceには、少なくとも次を含める。

1. Phase 1〜10の標準骨格を、小規模から大規模まで可変のWork Unitで運用できる。
2. Phase 11以降の追加を、規模と依存関係に基づき行える。
3. PADGのPortable骨格に`Phase 1-EX`を残さず、一般化可能部分をPhase 1で扱う。
4. Private Sidecar、Embedded Overlay、Managed MigrationおよびGreenfield Nativeの各Profileを選択できる。
5. Docs Rootを名称だけでHard-codeせず、発見結果とConflictを正直に保存できる。
6. Existing Docs、PADG Internal State、Publication StagingおよびExported Artifactの正本境界を混同しない。
7. 変更禁止Projectでは、Existing DocsへのCall、MutationおよびExportが0になる。
8. 非公開運用ではPADGをRepositoryから除外しながら、承認済み成果物のみ既存DocsにExportできる。
9. Copy、Move、Rename、Archive、Sync、ExportおよびGitの各Actionが、別々のAuthority Gateで制御される。
10. 既存Docsの丸ごと二重管理を既定にせず、Source Traceabilityと必要なImmutable Snapshotで復元可能性を維持する。
11. 新規Project、変更可能な既存Project、変更禁止の既存Project、および非公開運用のDry-runを分離して検証できる。

## 11. 非目標と禁止する短絡

- PADGを置いただけで既存Docsの書込Authorityが発生する。
- 既存Docsの変更禁止に対し、利便性を理由にOverlayやMigrationを強行する。
- TimestampだけでConflictを解決する。
- PADG側とExisting Docs側の双方を、同一内容の暗黙な正本にする。
- 公開前PADG全体をCommit対象へ混入させる。
- 既存Docsを無条件に全Copyし、Stale Copyを新しいSource of Truthとして扱う。
- Managed Migrationで原本のBackup、Digest、Mapping、Link検証またはRollbackを省略する。
- 小規模Projectに対し、10 Phase分の過大な作業量を強制する。
- 大規模ProjectをPhase 10で機械的に打ち切る。

## 12. Phase 10で確定する未決定詳細

次は今回の方向決定を変更しない範囲で、実装時に実Projectとツール形状を見て確定する。

- `.padg/`およびEmbedded名前空間のExact Directory Name。
- PADG Package本体とProjectごとのWorking Stateの配置分離。
- Document Root Discoveryの探索上限、Priority、Ignore PatternおよびConflict UI。
- Project Manifestの正式Schema、Required Field、EnumおよびVersioning。
- Git Ignoreの設定方法と、既存Ignore Ruleを壊さない適用方法。
- Export、Sanitization、Diff Review、Approval、ApplyおよびRollbackのExact Workflow。
- Immutable Snapshotを必須にする条件と保持期間。
- Managed MigrationでCanonical Rootを切り替える手順。
- Phase 1〜10の意味Templateと、小規模時のMinimal Gate。
- Phase 11以降を追加する定量・定性判断条件。

## 13. 実行時の推奨順序

```text
PADG二周編纂のSource Inventory確定
  -> Project-neutral CoreとProvider Adapterの確定
  -> Deployment Profile Contractの確定
  -> Document Root DiscoveryとProject Manifest Schemaの確定
  -> Phase 1〜10 Lifecycle Templateの確定
  -> Private Sidecarの導入Dry-run
  -> Embedded Overlayの導入Dry-run
  -> Managed Migrationの非破壊Dry-runとRollback検証
  -> Greenfield Nativeの導入Dry-run
  -> 非公開時のPublication Export検証
  -> 第2周Gap Auditと必要な訂正
```

実行順序はPADG二周編纂の正本順序、Docs統合、Shared Constitution、Bootstrapおよび外部Write Gateと統合して最終Freezeする。

## 14. Non-authorization

本書はユーザーが承認した方向を将来のPhase 10作業に予約する文書である。現時点で次を開始または許可しない。

- PADG Packageの作成。
- `.padg/`、`padg/`または他のDirectoryの作成。
- Existing DocsのCopy、Move、Rename、Archive、Migration、SyncまたはExport。
- `.gitignore`の変更。
- Project Root外へのReadまたはWrite。
- Git Stage、Commit、Push、TagまたはRelease。
- 特許出願、公開、配布またはLicense確定。

## 15. 現在の予約状態

```text
PADG Lifecycle Base                  : Phase 1〜10
PADG Extension                       : Phase 11+を必要時に追加
Portable Phase 1-EX                  : 作らない、一般化可能部分はPhase 1へ統合
Pre-patent Default                   : Private Sidecar
Public/Post-filing Options           : Private Sidecar / Embedded Overlay / Managed Migration / Greenfield Native
Document Root                        : Discovery式、`docs/`固定なし
Existing Docs Full Duplication       : 既定にしない
Commit前Export                        : 公開可能・承認済みArtifactのみ
Automatic Sync                       : 許可しない
Managed Migration                    : 明示承認とRollback成立時のみ
Implementation                       : NOT STARTED
```

## 16. Project固有SharedとProject-neutral Sharedの分離

PADGのDocs構造では、次の二つを別領域として扱う。

```text
docs/current/shared/
  Project固有のEvidence、共有Rule、運用知識、Decision、Failure、
  Recovery、TemplateおよびProject内横断情報を蓄積する。

docs/shared/
  Project固有要素を除去、SanitizeまたはParameterizeした上で、
  他Projectでも再利用可能なEvidence、Rule、Schema、Template、
  Failure Pattern、Recoveryおよび共有知識を蓄積する。
```

現RepositoryのPathとPADG側の最終Pathが異なる可能性はあるため、Exact Directory TreeはPhase 10で確定する。ただし、次の意味境界は維持する。

- `current/shared`側にあるだけでPortable性をClaimしない。
- `shared`側へ移す時は、Project名、絶対Path、個人情報、Credential、固有Model構成、固有Authorityおよび固有Acceptanceを検査する。
- 一般化で情報を落とす場合は、除外理由とSource Traceabilityを残す。
- `docs/shared/`を製品RuntimeのAuthority源、対象Projectの自動許可、または`docs/current/shared/`の置換として扱わない。
- Portable化できないEvidenceは無理に`docs/shared/`へ入れず、Project固有側に保持する。

## 17. Shared RootのREADME

人とAIのどちらでもDirectoryの役割を即座に判定できるよう、少なくとも次のREADMEを置く。Exact Filenameの大小文字はPackage Conventionで確定するが、標準候補は`README.md`とする。

```text
docs/current/shared/README.md
docs/shared/README.md
```

### 17.1 `docs/current/shared/README.md`

少なくとも次を記載する。

- ここがProject固有のShared領域であること。
- 保持対象と対象外。
- Current、History、Evidence、Handoff、RecoveryおよびPlanned Workの違い。
- ここの情報は他Projectでの再利用可能性を自動的に意味しないこと。
- `docs/shared/`へのPromote候補を作る際のSanitization、Parameterization、EvidenceおよびAuthority Gate。
- 主要Indexと読解順序。

### 17.2 `docs/shared/README.md`

少なくとも次を記載する。

- ここがProject-neutralな再利用候補領域であること。
- Project固有要素を除去またはParameterizeしていること。
- 収録物のSource Traceability、Revision、Digest、CoverageおよびKnown Limitationの読み方。
- Portableであること、対象Projectで即時有効またはBinding済みであることは別であること。
- 読んだだけでRole、Authority、Mutation Permission、Runtime BindingまたはProject Adoptionが発生しないこと。
- Projectへ取り込む際のManifest、Conflict、Adoption、ValidationおよびRollback導線。

READMEは単なるDirectory説明にせず、「ここへ入れてよいもの」「入れてはいけないもの」「一般化・採用に必要なGate」を人とAIの両方が解決できる入口とする。

## 18. PADG Package最上位READMEとBootstrap導線

PADG Packageを配置しただけで、AIがPackageを自動発見・自動読込・自動展開することは前提にしない。ProviderやHarnessごとに自動読込Capabilityが異なるため、Provider-neutralな明示入口をPackage最上位に置く。

```text
<padg-package-root>/README.md
```

最上位READMEは、少なくとも次の二つの読者導線を持つ。

### 18.1 AI向け導線

AIが「まず何を読めば運用を展開できるか」を、README単体から解決できるようにする。標準読解順序候補は次とする。

```text
1. PADG Package最上位README
2. Bootstrap Index
3. Project Discovery / Project Manifest手順
4. Deployment Profile選択条件
5. 割り当てられたRoleのBootstrap View
6. Authority / Mutation / Root Boundary
7. Active HandoffまたはCurrent Work Contract
8. Evidence / Return / Recovery Contract
```

- 各段階のRequiredとOptionalを区別する。
- 対象が存在しない場合は`not_found`、複数候補は`conflict`とし、推測で補完しない。
- Bootstrapは実行状態を復元するための導線であり、Role Grant、Project Authority、Write PermissionまたはMigration Permissionではない。
- Codex、Claude、Copilotおよび他Providerに専用の自動読込機構がある場合も、Provider Adapterからこの共通導線へ接続し、Common ContractをProvider固有Fileだけに閉じない。

### 18.2 人向け導線

人がPackage内部の詳細を知らなくても、明示された短い指示でAIにBootstrapを開始させられるようにする。READMEに、Copy可能な標準起動文を掲載する。

日本語の候補は次とする。

```text
PADG PackageのREADME.mdを読み、記載されたBootstrap手順に従って、
このProjectの現在地、Document Root候補、Docs Policy、適用可能なDeployment Profile、
必要なRole、Authority、Conflictおよび次の安全な一手をRead-onlyで確認してください。
対象Projectへの変更、Copy、Move、Migration、Export、Git操作またはAuthority拡張は、
必要な対象と差分を報告し、明示許可を受けるまで行わないでください。
```

英語候補も同等の意味で掲載する。起動文は「即時に全自動導入する」指示ではなく、Read-only Discovery、Conflict保持、Profile提案および明示承認Gateまでを開始する指示とする。

## 19. Bootstrap展開の受入条件追加

1. 人がPADG Packageの最上位READMEを見て、何をAIへ指示すればよいかを解決できる。
2. AIが最上位READMEからBootstrap、Project Discovery、Role、Authority、Handoff、EvidenceおよびRecoveryへ有界に到達できる。
3. Packageの自動読込がないProviderでも、READMEの標準起動文だけからRead-only Preflightを開始できる。
4. `docs/current/shared/`と`docs/shared/`の各READMEから、Project固有とProject-neutralの境界を正しく判定できる。
5. Project固有Evidenceを、SanitizationやAuthority確認なしにProject-neutral Sharedへ昇格させない。
6. READMEの読取やBootstrap完了を、Mutation、Adoption、Role GrantまたはAuthority Recoveryと混同しない。
