# Design Governance Handoff

```yaml
document_id: design_governance_handoff
status: current
language: ja
created_at: 2026-07-27 07:52:36 JST
updated_at: 2026-08-04 04:34:34 JST
owner: 設計統括者役
active_phase: phase_1_ex
rag_default: true
```

## 1. 文書の目的

本書は、現在の設計統括者役TaskがContext Limit、長期化、障害、手動終了またはTask再作成により継続不能になっても、新しい設計統括者役Taskが旧Taskの会話記憶へ依存せず、Docsだけから同じ責務、判断、運用、Project状態および次の安全な作業を復元するための専用Handoff正本である。

本書は差分通知、短いStatusまたは一回限りの引き継ぎ書ではない。各Phaseを通じて累積更新し、最新版一つから復元を開始できる自己完結のStable入口とする。

ユーザーがこの運用を必要とする理由は明確である。

- Codex TaskがいつContext Limitまたは動作限界へ達するか予測できない。
- 情報ロスにより、ユーザーが過去の要件、判断、例外および運用を再説明する状態を避ける。
- Projectや担当Taskを復元できない状態を避ける。
- 既に得た設計判断、失敗Evidence、将来構想および接続可能性を失う機会損失を避ける。
- 設計統括者役さえ完全復元できれば、Phase別設計者役、実装者役および対外Docs役も正本とHandoffから再作成できる。

## 2. Authority

本Projectの最上位Authorityはユーザーの明示指示である。

```text
User Explicit Instruction
  → Task Role／Write Authority Policy
  → Active Phase Accepted Handoff
  → Documentation Structure／Task Operations
  → Documentation Rules
  → 設計統括者役による解決またはユーザーへのEscalation
```

設計統括者役はProject全体、Cross-Phase設計、Current Canonical、Shared Rules、Role Authority、Phase構成、Final ReviewおよびContinuityを管理する。ただし、ユーザー承認済みのDocs運用、Append-only保持、命名、Git方針、公開境界、削除条件またはRole Authorityを、ユーザーの許可なく変更する権限は持たない。

## 3. Stable／History配置

Stable入口：

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

更新前後Snapshot、Recovery ManifestおよびReconstruction Validation Evidence：

```text
docs/project/shared/history/design_governance_handoff/
```

Stable文書を更新する場合は、次の順序を必須とする。

1. 更新前原文を`design_governance_handoff_<phase>_ja_YYYYMMDDHHMMSS.md`として完全コピーする。
2. Stable原文と更新前SnapshotのSHA-512一致を確認する。
3. 本書、Current、Shared、Active／Completed PhaseおよびRaw Sourceから累積完全版を再構築する。
4. Stable文書を更新する。
5. 更新後原文を別Timestampで完全Snapshotする。
6. Stable原文と更新後SnapshotのSHA-512一致を確認する。
7. Active Phase変更Record、Phase IndexおよびAppend-only Documentation Index Snapshotへ記録する。

既存Historyを編集、削除、圧縮または新しいStable版で置換しない。

## 4. Mandatory Timing

原則として各Phase完了後、Phase Backupを取得する直前に実施する。

```text
Implementation／Review完了
  → User Acceptance／User Test Acceptance
  → 設計統括者役のPhase完了・次Phase移行可能宣言
  → Current／Shared／Project Continuity Refresh
  → Design Governance Handoff Refresh
  → Recovery Manifest
  → Docs-only Reconstruction Validation
  → Phase Backup
```

Reconstruction Validationが`pass`でない場合、Phase Backupへ進まない。

TaskがPhase途中でContext Limit、長期化、障害または継続困難へ近づいた場合は、Phase完了を待たず臨時Refreshする。臨時Refreshでも、更新前後Snapshot、SHA-512、変更RecordおよびIndex更新を省略しない。

## 5. 情報保存原則

本書とRecovery Packageは情報ロスを一切許さない水準で作成する。

- Diff-onlyにしない。
- 最新版一つで現在有効な責務、状態、判断、例外、未決事項および次の作業を解決できるようにする。
- Accepted情報を、簡潔化、重複除去、読みやすさ、File SizeまたはGit差分を理由に削らない。
- 失敗、非採用案、Known Limitation、External Dependency、保留理由および再評価条件も保持する。
- 訂正時は、旧内容をHistoryへ保持し、訂正理由と現在有効な内容を追跡可能にする。
- 後続版はProjectの進展に応じて、原則として粒度と情報量を増やす。
- 別文書へのLinkだけでは復元に必要な前提と結論を落とさない。

本書は`Project Continuity Master`を置き換えない。Project ContinuityはProject全体の生命線、本書は設計統括者役の完全復元入口であり、両方を一組として維持する。

## 6. 必須Reading Order

新しい設計統括者役Taskは、次の順で読む。

1. `docs/project/current/documentation_index_ja.md`
2. `docs/project/current/requirements/requirements_specification_ja.md`
3. `docs/project/current/architecture/system_architecture_ja.md`
4. `docs/project/current/architecture/technology_selection_ja.md`
5. `docs/project/current/architecture/basic_design_ja.md`
6. `docs/project/current/governance/runtime_governance_specification_ja.md`
7. `docs/project/current/project_continuity/project_continuity_master_ja.md`
8. 本書
9. `docs/project/shared/conventions/documentation_rules_ja.md`
10. `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
11. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
12. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
13. Active Phaseの`phase_index_ja.md`
14. Completed PhaseのPhase Index／Lossless Compilation／Final Review
15. 最新の`design_governance_recovery_manifest_YYYYMMDDHHMMSS.md`
16. 最新Accepted Handoff／Status／Review
17. Source確認、矛盾追跡または監査が必要な場合だけRaw History

Historyを最初から全件読む必要はない。ただし、Lossless再整理、矛盾、旧判断、User Instructionまたは正本の根拠を検証する場合は、対象範囲のRaw Historyを必ずSource Inventoryへ含める。

新しい設計統括者役Taskは、最初のMutation可能なTool Callより前に`Research Asset Mutation Control`を読む。未読の場合はRead-onlyを維持する。

## 6.1 Research Asset Protection／Self-governance

設計統括者役は、自身を含む全担当の無許可Mutationを防ぐ責任を持つ。

次をTask固有の判断へ委ねない。

- Project Root外操作の禁止
- Tool PermissionとUser Authorizationの分離
- 元Project／Copyの識別
- Backup完了確認
- Proposed Diffの事前提示
- Mutation Authorization Envelope
- Propose／Commit二段階Protocol
- Pre-tool-call Self Check
- 無許可Mutation後の追加修復禁止

無許可Mutationは、File単位の局所問題ではない。Backup増加、PC容量消費、全Project／Folder差分検証、有料AI利用による現金損失、ユーザーの再説明・監督負担、精神的疲労、研究時間喪失、復元不能および研究・業界上の機会損失へ連鎖する。

設計統括者役が損失規模を把握できない場合、Riskを軽微と推定せず、Default Denyで停止する。

本統制の正本：

```text
docs/project/shared/operations/research_asset_mutation_control_ja.md
```

Schema／Template：

```text
docs/project/shared/schemas/mutation_authorization_manifest_schema_v1.json
docs/project/shared/templates/mutation_authorization_manifest_template_ja.md
```

## 7. Recovery Packageが保持する情報

### 7.1 Project Identity／Purpose

- Project名、表示名、公開名義
- Runtime Governance型AI研究基盤としての目的
- AI研究、AI設計、AI実装から一般対話までを扱う方針
- Model自作ではなく、Hugging Face由来Modelを交換可能なRuntimeへ統合する位置付け
- 疎結合、単一責任、依存性逆転、Adapter、Port、個別ON／OFFを重視する設計思想

### 7.2 Phase State

- 完了済みPhaseとAcceptance
- Active Phase、残作業およびGate
- 次Phaseの目的、開始条件、担当構成
- Phase Backup、Git、公開の状態
- Phase完了宣言とユーザーTest合格の有無

### 7.3 Accepted Design

- Requirements
- Architecture
- ADR
- Governance
- Configuration Layer
- Model／Backend／Deployment Profile
- UI／API／Access Control
- Audit／RAG／Guardrail／Judge／Repair／Agent等の将来Hook
- External R&D Hook
- Docs／Role／History運用

### 7.4 Runtime／Artifact

- Model ID、形式、Quantization、配置規則
- Backend、Python、Dependency Version
- Local／External Profile
- Test結果、Acceptance、Known Limitation
- 主要Source、Config、Script、Docs Path
- 必要なSHA-512、Backup ReceiptおよびManifest

### 7.5 Open State

- Open Finding
- 未決事項
- Deferred Decision
- 非Blocker観察事項
- 再評価条件
- ユーザー担当の外部操作
- 外部Serviceの状態
- 未許可操作
- 次の安全な一手

## 8. Current Project Baseline

本書の現在の入口状態は次である。詳細および後続更新は`Project Continuity Master`とActive Phase Indexを正本とする。

```text
Phase 0        : COMPLETE
Phase 1        : COMPLETE／ACCEPTED
Phase 1 Backup : COMPLETED／VERIFIED
Phase 1-ex     : IN PROGRESS
Git／GitHub    : EXISTING HISTORY PRESERVED／MAIN ALIGNED／SINGLE CANONICAL ROOT
```

Phase 1でmacOS MetalとLightning Linux x86_64 Pure CPUのCLI／Minimal Web Runtimeを成立させた。Phase 1-exでDocs再編、Continuity、Public Demo／Traffic-aware Auto-start、Mac／Lightning Documentation RAG、Existing GitHub Historyを維持した公開統合、Git運用設計および単一Git Root化まで完了した。

Git運用は[Git Workflow Policy](../operations/git_workflow_policy_ja.md)でAcceptedである。`margpa-runtime-llm`が単一Canonical Git Working Rootであり、`main`／`origin/main`／Remote `main`は`9ac8a6ba4a2120d93856356fababd130af3aa352`で一致する。ただし、Commit、Push、Tag、Merge、Release、Branch削除またはRemote変更は各対象のユーザー明示承認なしに行わない。

2026-07-27のDocumentation Reconstructionでは次を完了した。

- 493 Docsと6 Demo Images、合計499 EntriesのSource Inventory固定
- Project Continuity Master第1周
- Roadmap第1周
- Current Canonical 6文書の累積再構築
- Phase 1の316 Source Final Lossless Compilationと全件Hash検証
- Phase 1-exの145 Source Interim Lossless Compilationと全件Hash検証
- Shared Rules／Operations／Role Authority／本Handoffの再構築
- Project Continuity Master／Roadmap第2周
- Public Overview／Concept／Roadmap
- README、LICENSE、TERMS_OF_USE、NOTICE、CITATION
- Canonical／Public／Root Artifactの相対Link、Identity、`.DS_Store`、CITATION、Lossless再抽出、TestおよびStatic Checkを含む最終検証

Documentation Reconstruction初版は`pass`である。これは依頼された初回Documentation Corpusの完成を意味するが、Phase 1-ex全体の完了を意味しない。

次は未完了である。

- Phase 1-ex Final Compilation
- Mac限定簡易Documentation RAG
- Lightning Traffic-aware Wake-upの実証
- 匿名Public Demo
- Git運用設計の承認
- Git初期化またはGitHub公開
- Phase 1-ex完了宣言とBackup

## 9. Role Reconstruction

### 9.1 設計統括者役

Project全体、Cross-Phase、Current、Shared、Phase構成、Final Review、Continuity、Backup／Git／Release設計を担当する。Phase 1-exではPhase別設計実務も兼ねる。

### 9.2 Phase別設計者役

Phase 2以降に必要に応じて配置する。担当PhaseのRequirements、Architecture、ADR、OperationsおよびDesigner Handoffへ書き込む。Current、Shared、他PhaseおよびPublicはRead-onlyとし、Cross-Phase変更を設計統括者役へEscalateする。

### 9.3 実装者役

`src/`、`tests/`、`scripts/`を担当する。Accepted Handoffとユーザー許可がある場合だけ`config/`等を変更する。Canonical Requirements、Architecture、Governance、ADR、Current、SharedおよびPublicはRead-onlyである。

### 9.4 対外Docs役

`README.md`、`LICENSE`、`NOTICE.md`、`CITATION.cff`および`docs/public/`を担当する。Public向けに整理しても、Canonicalの意味、独自性、研究価値および将来構想を失わせない。

新しい設計統括者役は、各担当の開始に必要な正本、Accepted Handoff、Write Boundary、完了条件およびStatus入口を提示できなければならない。

## 10. Recovery Manifest

各Phase完了後、Phase Backup直前に次を作成する。

```text
docs/project/shared/history/design_governance_handoff/
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

Manifestには少なくとも次を記録する。

- 作成日時、対象Phase、Recovery状態
- Source Inventory
- Source Path、Document ID、Version、SHA-512
- 必須Reading Order
- Current／Shared／Public Stable Snapshot対応
- Completed／Active／Next Phase
- 最新Accepted Review／User Acceptance
- Open Finding／Known Limitation／Deferred Decision
- External Service／Deployment／User-owned Operation
- Git／Backup／Release状態
- 各担当Taskの復元入口
- 次の安全な一手
- Reconstruction Validation結果
- Known Link Exception

ManifestはSecret実値、Credential、個人連絡先、Private URL、非公開Modelまたは公開不要なLocal Absolute Pathを含めない。

Phase未完了時の通常更新では、完了を装うRecovery Manifestを作らない。ただし、ユーザーがTask障害に備えた即時完全復旧点を明示要求した場合は、`interim_current_state`または`emergency_recovery_point`として対象時点、未完了範囲およびPhase未完了を明記した臨時Recovery Manifestを作成できる。これはPhase完了版Recovery Manifestを置き換えない。

## 11. Reconstruction Validation

旧設計統括者役Taskの会話を使わず、次を説明・特定できることを`pass`条件とする。

1. 何を、なぜ作っているか。
2. どのPhaseまで完了し、現在どのPhaseか。
3. 現在有効なRequirements、Architecture、Governance、ADRはどれか。
4. どのDocsが正本、Stable、History、Publicか。
5. Accepted Decision、Open Finding、Known Limitation、未決事項は何か。
6. Model、Backend、Runtime、Config、Deploymentの現在状態は何か。
7. どの担当がどこへ書けるか。
8. 何がユーザー専用操作または未許可External Actionか。
9. Phase Backup、Git、GitHub、License、Public Demoの状態は何か。
10. 次に何を安全に行うか。
11. Phase別設計者役、実装者役、対外Docs役をどのDocsから復元するか。
12. Historyを変更せず、Stable変更前後とPhase Development Logを追跡できるか。

一つでも解決不能な場合、完全復元は未達である。Source不足を推測で埋めず、不足箇所をOpen Findingとして記録する。

## 12. Security／Disclosure Boundary

- 公開名義は`Nazuna Research`を使用する。
- Credential、Secret、個人連絡先、Private URLおよび実会話Logを埋め込まない。
- Local Absolute Pathは公開・共通復元に不要なら記録しない。
- External Serviceの手動操作は、担当、状態、再現手順および安全境界を記録するが、Secret実値は記録しない。
- Model本体をDocs／Git／Backupへ含めず、Model ID、取得元、配置規則、SizeおよびHashで再構築可能にする。
- EASA、DLAGSA、OCILNSは名称、研究領域、方向性およびGeneric Hookを保持するが、未公開の核心Algorithmや内部Protocolを推測して追加しない。

## 13. Update Completion Checklist

- [ ] 更新前Stable Snapshotを作成した。
- [ ] 更新前StableとSnapshotのSHA-512が一致した。
- [ ] Current、Shared、Project Continuity、Active Phaseおよび必要なRaw HistoryをSourceにした。
- [ ] Accepted情報を削除していない。
- [ ] 新しい決定、例外、未決事項、失敗Evidenceおよび再評価条件を反映した。
- [ ] Diff-onlyではなく累積・自己完結の最新版にした。
- [ ] Stable文書を更新した。
- [ ] 更新後Stable Snapshotを別Timestampで作成した。
- [ ] 更新後StableとSnapshotのSHA-512が一致した。
- [ ] Local LinkとReading Orderを検証した。
- [ ] Secret、個人情報、Private URLを含めていない。
- [ ] Active Phase変更Recordを追加した。
- [ ] Phase Indexを更新した。
- [ ] Append-only Documentation Index Snapshotを追加した。
- [ ] Phase完了時はRecovery Manifestを作成した。
- [ ] Docs-only Reconstruction Validationを実施した。
- [ ] Validationが`pass`になるまでPhase Backupへ進んでいない。

## 14. 2026-07-27 Reconstruction Recovery Baseline

新しい設計統括者役が現在作業を引き継ぐ場合、次を最初に確認する。

```text
Source Inventory:
  docs/project/phases/phase_1_ex/history/operations/
  documentation_reconstruction_inventory_20260727093727.md

Current Index:
  docs/project/current/documentation_index_ja.md

Phase 1 Final Lossless:
  docs/project/phases/phase_1/lossless/phase_1_lossless_ja.md
  docs/project/phases/phase_1/lossless/phase_1_lossless_manifest.json

Phase 1-ex Interim Lossless:
  docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_ja.md
  docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_manifest.json

Active Phase Index:
  docs/project/phases/phase_1_ex/phase_index_ja.md
```

検証済み値：

```text
Initial Inventory       : 499 / 499 pass
Phase 1 Lossless        : 316 / 316 pass
Phase 1-ex Interim      : 145 / 145 pass
Current Canonical Links : 7 / 7 pass
Git                     : not started
  Public／Legal            : initial corpus complete／validated
```

引継ぎ直後の安全な一手は、公開文書を再作成することではない。2026-07-27の初回Documentation Corpusは完成・検証済みであるため、最新Recovery ManifestとPhase 1-ex Indexを確認し、Mac限定簡易Documentation RAG、Lightning Traffic-aware Wake-up手動検証、Git運用設計、Initial Commit前再照合、Phase 1-ex Final LosslessおよびBackup Gateのうち、ユーザーが次に指定した一項目だけを進める。

## 15. Language Scopeの現在決定

今回の再構築では日本語正本だけを作成する。`docs/project/current/`と`docs/public/`の英語派生版はPhase 1-ex後半でユーザーが改めて判断する。

英語版を作る場合は日本語正本と同じ粒度で一式を作る。概要、抄訳または一部文書だけを正式な英語版として扱わない。作成しない場合も、その判断をInitial Commit前ManifestとPublic Scopeへ明記する。

## 16. 二周方式の完了条件

Project Continuity MasterとRoadmapは、大規模再構築の最初と最後に二周する。

- 第1周：Current、Phase Lossless、Shared、Publicを再構築するための基準。
- 第2周：再構築中に確定したHash、Source Scope、Phase状態、Public／Legal状態およびOpen Workを累積反映する最終照合。

第2周で第1周を短縮、要約または置換しない。更新前後SnapshotとSHA-512を保持し、Phase 1-ex変更RecordとAppend-only Index Snapshotへ記録する。

## 17. 2026-07-27 Post-documentation Recovery Point

2026-07-27 12:13 JST時点で、ユーザーが依頼した初回Documentation Corpusは完成している。

```text
Project Continuity Master   : second pass complete
Public Roadmap              : second pass complete
Current Canonical Set       : complete
Phase 1 Lossless            : final／316 of 316 pass
Phase 1-ex Lossless         : interim／145 of 145 pass
Shared Stable Set           : complete
Public Overview／Concept    : complete
README／Legal／Citation     : complete
Documentation Validation   : pass
Phase 1-ex                 : in progress
Git／GitHub                : not started
```

最終検証Evidence：

```text
docs/project/phases/phase_1_ex/history/operations/
documentation_reconstruction_final_validation_20260727110834.md
```

検証結果：

```text
Selected Stable Files       : 21
Relative Links              : 286／286 pass
Demo Images                 : 6／6 pass
Old Identity／Private Path  : 0
.DS_Store                   : 0
CITATION Parse              : pass
Phase 1 Lossless Extraction : 316／316 pass
Phase 1-ex Extraction       : 145／145 pass
Runtime Test／Static Check  : pass
```

最新READMEには、現在地を`Phase 1-ex / 最終予定 Phase 10`として上部へ明示し、Roadmapを現在位置・実装済み範囲・未実装範囲・将来構想の正本導線とした。

Lightningの過去URLはEvidenceとして保持する。URLが将来変更された場合は、Immutable Historyを改変せず、README、Current Index、Public案内等の現在有効なStable入口だけを新URLへ更新し、変更前後Snapshotと変更Recordを残す。Credential、Managed Secret実値または個人連絡先はDocsへ記録しない。

この時点の臨時Recovery Manifestは、次に置く。

```text
docs/project/shared/history/design_governance_handoff/
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

このManifestのStatusは`interim_current_state`であり、Phase 1-ex完了版ではない。新Taskは、Stable Handoff、最新Recovery Manifest、Current Index、Project Continuity Master、Phase 1-ex IndexおよびRoadmapの順に照合すれば、旧Task会話に依存せず現在状態から再開できる。

現時点の残作業は次である。

1. Mac限定簡易Documentation RAGとExternal Hook
2. Lightning Traffic-aware Wake-upのユーザー手動実証
3. Basic Previewと分離したPublic Demo境界の後続判断
4. Git運用設計
5. Initial Commit前のDocs／Public Allowlist／Secret／Identity／License再照合
6. Phase 1-ex Final Lossless Compilation
7. Phase 1-ex完了版Design Governance Recovery Manifest
8. Final Review、ユーザーAcceptance、Phase Backup
9. ユーザーの明示許可後のGit／GitHub操作

## 18. 2026-08-04 Single Git Root Interim Recovery Point

本節は現在の設計統括者役を新Taskへ直ちに復元するための最新入口である。第14節および第17節は当時のRecovery Pointとして保持し、現在状態は本節を優先する。

### 18.1 Immediate State

```text
Phase 1                         : COMPLETE／ACCEPTED
Phase 1 Backup                  : COMPLETED／VERIFIED
Phase 1-ex                      : IN PROGRESS
Documentation Structure        : MIGRATED／LEGACY ROOT RETIRED
Documentation RAG              : MAC／LIGHTNING BASIC／PUBLIC ACCEPTED
Lightning Auto-start           : ACCEPTED／GO
Anonymous Public Demo          : ACCEPTED
GitHub Existing History        : PRESERVED
PR #1                          : MERGED BY MERGE COMMIT
Canonical Git Root             : margpa-runtime-llm
main／origin/main／remote main : 9ac8a6ba4a2120d93856356fababd130af3aa352
Former Git Staging Root        : RETIRED／DELETED AFTER BACKUP
Cutover Full Test              : 430 PASSED／3 DESELECTED
Tag／Release                   : NONE
```

### 18.2 Required Reading Order

1. 本Stable Handoffの第18節。
2. [Latest Interim Recovery Manifest](../history/design_governance_handoff/design_governance_recovery_manifest_20260804035722.md)。
3. [Current Documentation Index](../../current/documentation_index_ja.md)。
4. [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)の第31節。
5. [Phase 1-ex Index](../../phases/phase_1_ex/phase_index_ja.md)。
6. [Git Workflow Policy](../operations/git_workflow_policy_ja.md)。
7. [Git Source→Target統合／公開反映／単一Git Root移行記録](../../phases/phase_1_ex/history/operations/git_source_target_integration_publication_and_single_root_cutover_20260804035722.md)。
8. [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)。
9. Public Roadmap。

### 18.3 Accepted Git Baseline

```text
Initial Integration Commit : ce4f9ce5537aed2f34ceb0e4316685778fb063cc
Canonical Alignment Commit : 3a645f7317cd5c7f702c6004b8eb0b96d9c261cf
PR #1 Merge Commit          : 9fff303175a3224963254eacddd66f9cf5112a5a
Direct main Docs Commit     : 9ac8a6ba4a2120d93856356fababd130af3aa352
Publication Files           : 1,053／1,053
Source-only／Target-only    : 0／0
Content Mismatch            : 0
```

旧`docs/phases/`と廃止Demo画像8件は削除し、現行Demo画像12件は維持した。作業Branchは`main`への到達をLocal／Remoteで証明後、ユーザー承認で退役した。

### 18.4 Current Git Rule

- 小規模で決定論的なDocs／Metadata変更は、Exact Diff、Test、Sanitation、Rollback可能性およびユーザ明示承認が揃った場合だけDirect `main`候補。
- 新機能、複数Layer、大規模、高RiskまたはPhase統合はWorking Branch／Draft PR／Review／Merge Commitが原則。
- Force Push、History Rewrite、Repository再作成、Root Commit置換、Tag移動および無承認Remote変更は禁止。
- File Write AuthorityはCommit／Push Authorityを生成しない。
- GitはTimestamp History、Lossless Compilation、Recovery ManifestおよびBackupを置換しない。

### 18.5 Remaining Phase 1-ex

1. 本State RefreshとそのBefore／After Snapshot／Index／SHA-512検証。
2. Phase 1-ex Final Lossless CompilationとManifest。
3. Roadmap等の必要Docs Final Refresh。
4. Full Test、Static Check、Link、Privacy、Publication Sanitation、Git Postflightを含むPhase Final Check。
5. Open Finding解決または明示承認済みDeferral。
6. User Acceptance。
7. ユーザーへPhase Backup取得を明示依頼。
8. Phase Final Backup Evidence。
9. Canonical Rootからの正当な次Commit／PushとTag候補の別判断。
10. Phase 2開始Gate。

本Recovery Pointは`interim_current_state`であり、Phase 1-ex完了版ではない。新Taskは上記残作業のうち、ユーザーが明示指定した一つだけを進める。

## 19. Phase 2 Project Responsibility／Pilot First Gate

Phase 2以降、現設計統括者役をProject責任者とする。責任範囲はProject全体、Cross-Phase不変条件、Phase担当Taskの編成、設計／実装Handoff、Review、RecoveryおよびPhase Closure準備である。

User Decision Authority、Backup、Git／公開、External Service、Secret、課金、Destructive ActionおよびPhase移行の最終判断はユーザーに残る。Project責任者というRole名から包括Authorityを推測しない。

Phase 2の最初の作業は、元来のPhase 2機能実装ではなく、Document-driven Orchestration Pilotの設計と最小実行である。

```text
Phase 2-0:
  Pilot Requirements／Capability／Authority／Cost／Stop／Recovery
  → User-approved Authorization Envelope
  → 必要Task作成／命名／Authority設定
  → Handoff／Status／Follow-up／Review
  → single bounded work unit
  → GO／ADJUST／STOP
  → original Phase 2-A～2-F
```

当面は有界な一作業単位ごとに回す。Evidenceが安定した場合だけ複数Unit、Subphase、Phase完了単位へ拡張し、Project完了単位は長期目標とする。Cost、Authority、Recovery、ConflictまたはUser Gateに問題があれば無理に拡張しない。

Phase 2から、Phase固有のAppend-only `documentation_index_YYYYMMDDHHMMSS.md`は`docs/project/phases/phase_2/history/index/`へ保存する。Phase 1／Phase 1-ex Historyを遡及移動しない。

Agent／Tool本格実装前に、運用規則をProvider-neutralな統合憲法書へLossless Compilationする。予定Rootは`docs/project/shared/constitution/`であり、Codex DesktopとClaude Codeの双方へAdapter可能なPortable Packageを目標とする。詳細は[Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)を参照する。

Desktop Application化は後続Phase予約であり、実装Phase／Framework／配布方式は未決定である。
