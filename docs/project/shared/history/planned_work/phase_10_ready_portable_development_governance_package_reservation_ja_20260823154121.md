# Phase 10 READY時 開発体制移植用Package作成予約

```yaml
document_id: phase_10_ready_portable_development_governance_package_reservation_20260823154121
status: planned_not_started_parent_write_not_authorized
document_type: append_only_planned_work
target_gate: phase_10_ready_before_commit_push
recorded_at: 2026-08-23 15:41:21 JST
decision_authority: user
source_project_mutation_authorized: false
parent_directory_write_authorized: false
```

## 1. Decision

Phase 9 ClosureでPhase 1〜9のDocs群を統合・整理した後、Phase 10 READYかつCommit／Push前に、現Projectで成立したCodex／Claudeを含む開発体制を、新規Project、途中参加する既存Projectおよび他Userへ移植できるPackageへ再編成する。

移植用Packageは`margpa-runtime-llm/`の外側、親の`MARGPA-RUNTIME-LLM/`直下へ新規Folderとして作成する候補である。Exact Folder名、Absolute Path、作成権限およびMutation範囲は実行前にUserが明示する。

本書は、現在許可されたProject Rootの外へ書き込む権限を与えない。

## 2. Three-layer Separation

次の三つを別物として扱い、名前、責務、RevisionおよびBindingを混同しない。

```text
1. <project-root>/constitution/
   Phase 8でAgent／Toolへ適用するRuntime MARGPA Constitution Package。

2. <project-root>/docs/project/shared/constitution/
   Codex／Claude等の開発運用に用いる憲法・制度・運用ルールのRepository内Lossless正本。

3. <parent-root>/<portable-package>/
   Project固有成分を除き、別Projectへ開発体制を導入する移植用Package。
```

Runtimeの`constitution/`を、そのままCross-provider開発運用Packageと見なさない。移植用Packageも、Runtime Agent／Toolへ自動Bindingしない。

## 3. Repository内の先行統合

Phase 9 Closureでは、Phase 1〜9で蓄積した次の内容を、既存HistoryとProvenanceを失わずに`docs/project/shared/constitution/`へ統合する。

- 最上位規則群とHuman-only Amendment Authority。
- Authority、Role、Delegation、Scope、Filesystem Boundary。
- Docs正本、Append-only History、Index、Handoff、From／To。
- Mutation、Backup、Recovery、Stop、Resume、Review、Closure。
- Automation、Cross-provider、Compaction、Long-run、Provider Limit Recovery。
- Evidence Class、Zero Claim、Near Miss、Incident、Deferred Evidence。
- Human Escalation Eligibility、Controller Responsibility、Decision Burden最小化。
- Codex／Claude／将来ProviderのAdapter差分とProvider-neutral Core。
- Constitution Mode、Automation Level、OFF／OBSERVE／ENFORCE等のMode契約。

巨大な単一Markdownへ押し込まず、Canonical Index、章別文書、Rule ID、Schema、ManifestおよびRole／Provider Viewへ分割された一つの統合体系とする。

## 4. Portable Package Source and Sanitization

移植用Packageは、Phase 9 Closure後の`docs/`構造をBaseとしてDirectory構造を可能な限り保持しつつ、Project固有成分を削除、抽象化またはTemplate Parameterへ変換する。

削除／抽象化対象候補：

- Project名、Organization名、個人名、User名、Machine名。
- Absolute Path、Local Account、Repository URL、Thread ID、Task固有ID。
- MARGPA Runtime LLM固有のProduct要件、Model名、Phase成果物、UI／API実装詳細。
- Secret、Credential、Email、Private URL、Local Environment情報。
- 既に完了したProject固有Incidentの内容。ただし一般化可能なFailure PatternとRuleは残す。

保持対象候補：

- Governance Core、Role、Authority、Docs、Evidence、Recovery、AutomationおよびCross-provider Contract。
- 新規／既存Projectへ導入するBootstrap、Inventory、Migration、ValidationおよびRollback手順。
- Provider-neutral Template、Schema、Manifest、Rule ID、Role ViewおよびAdapter Interface。
- Project固有値を注入するための明示的Parameter／Placeholder。

「Project固有成分を除く」ことと「一般化可能な運用知見をLosslessに保持する」ことを両立させる。削除したSourceがどの一般Rule、Templateまたは除外理由へ写像されたかをManifestで追跡可能にする。

## 5. Portable Phase 1／Phase 1-ex Integration

移植用Packageでは、`Phase 1-ex`を独立Phaseとして残さない。一般化可能なPhase 1-exの内容は、Portable Phase 1へLosslessに統合する。

```text
Current Source Repository:
  phases/phase_1/
  phases/phase_1_ex/

Portable Package:
  phases/phase_1/
  phases/phase_1_ex/  -> not created
```

Portable Phase 1には、現在欠けている次のDirectoryを新設する。

```text
phases/phase_1/history/index/
```

統合時は次を必須とする。

1. Phase 1-ex由来の一般化可能な文書、決定、EvidenceおよびHistoryをInventory化する。
2. Stable、History、Index、Handoff、Lossless、Operations等の移植先を明示する。
3. `source_path`、旧Phase、旧Document ID、Revision、Digest、変換種別およびPortable PathをMigration Manifestへ記録する。
4. Phase 1-ex由来であることを消去せず、Provenanceとして保持する。
5. Phase 1／Phase 1-ex間の重複、ConflictおよびCurrent／Historical状態を分類する。
6. 内部Link、Index、From／To、HandoffおよびPhase参照をPortable Phase 1へ再接続する。
7. Project固有情報として除外した内容も、除外理由とSource CoverageをManifestへ残す。
8. Source Repositoryの`phase_1/`および`phase_1_ex/`は、この作業のために削除、Moveまたは統合しない。

ここでいうLosslessは、Project固有Dataを無条件に複製することではない。移植可能な制度・運用上の意味、決定、Failure Pattern、Rule、Evidence Classおよび由来を欠落させないことを指す。

## 6. Candidate Package Structure

Exact構造はPhase 9 Closure後にFreezeするが、最低限次を候補とする。

```text
<portable-package>/
├── README_ja.md
├── README_en.md                         # optional／availability dependent
├── docs/
│   ├── project/
│   │   ├── current/
│   │   ├── phases/
│   │   │   └── phase_1/
│   │   │       └── history/
│   │   │           └── index/
│   │   └── shared/
│   │       └── constitution/
│   └── templates/
├── schemas/
├── manifests/
├── bootstrap/
├── validation/
└── migration/
```

元の`docs/`構造をBaseとして保持する方針は、空DirectoryやProject固有Phaseを機械的に全て残すことを意味しない。DirectoryごとにPortable責務、Source Coverageおよび除外理由を定義する。

## 7. Portability and Provider-neutral Requirements

- Codex、Claude Codeまたは単一Vendorだけを前提にしない。
- 新規Projectと途中の既存Projectで、Inventory／Conflict／Adoption Modeを分ける。
- Existing Rulesを上書きせず、Diff、Conflict、Adopt／Adapt／Reject判断を経る。
- Absolute Path、Project Phase番号、Tool名、UI名またはProvider MemoryをNormative CoreへHard-codeしない。
- Humanだけが最上位規則群の追加、削除、編集または正式Exceptionを承認できる。
- Package投入だけでAuthorityを自動生成しない。Project OwnerによるScope、Role、Write RootおよびException Gateを必須とする。
- Full PackageとRole／Phase／Task別Viewを同じAccepted Revisionから生成可能にする。
- Package Revision、Source Digest、Generated View DigestおよびStale Detectionを持たせる。
- Provider Memoryではなく、Package内Docs／Manifest／Evidenceを正本とする。

## 8. Build and Acceptance Flow

1. Phase 9 ClosureでRoadmap、Index、Current、SharedおよびPhase Docsを統合する。
2. `docs/project/shared/constitution/`のCanonical CorpusとRevisionをFreezeする。
3. 全Source InventoryとSource→Portable Mappingを作成する。
4. Project固有情報をSanitize／Parameterizeし、除外理由を記録する。
5. Portable Phase 1へPhase 1-exを統合し、`history/index/`を構築する。
6. Bootstrap、Adoption、Conflict Resolution、RollbackおよびValidation手順を作成する。
7. Privacy／Secret／Absolute Path／Identity／Broken LinkをScanする。
8. File Count、Size、SHA-512、ManifestおよびSource Coverageを確定する。
9. 空の新規Projectと、既存規則を持つFixture Projectの両方でDry-runする。
10. Human Review後、Phase 10 READYかつCommit／Push前の成果物として受理する。

## 9. External Write Gate

候補配置先の`MARGPA-RUNTIME-LLM/`直下は、現時点で許可されたProject Rootの外側である。実作成前に少なくとも次を明示確認する。

```text
Exact Parent Root
Exact Portable Package Folder Name
Create／Write Authority
Read Scope
Existing Target Existence
Symlink／Permission／Ownership
Backup／Rollback
Git Repository Boundary
Sanitation and Publication Scope
```

Folder名を会話の流れまたは「良かれ」で決めず、UserのExact指定または承認を受ける。

## 10. Non-authorization

本書は予約であり、次を許可しない。

- Parent `MARGPA-RUNTIME-LLM/`へのRead／Write／Directory作成。
- 現RepositoryのPhase 1／Phase 1-exのMove、削除、統合または直編集。
- `docs/project/shared/constitution/`またはRuntime `constitution/`の即時作成。
- Project固有情報の機械的削除、外部公開またはPackage配布。
- Git Stage、Commit、Push、TagまたはRelease。

実行はPhase 9 Closure、UserのExact要件、外部Write GateおよびPhase 10 READY Gateが成立した後に別途開始する。

