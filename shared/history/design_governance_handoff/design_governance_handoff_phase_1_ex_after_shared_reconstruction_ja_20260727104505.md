# Design Governance Handoff

```yaml
document_id: design_governance_handoff
status: current
language: ja
created_at: 2026-07-27 07:52:36 JST
updated_at: 2026-07-27 10:39:39 JST
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
11. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
12. Active Phaseの`phase_index_ja.md`
13. Completed PhaseのPhase Index／Lossless Compilation／Final Review
14. 最新の`design_governance_recovery_manifest_YYYYMMDDHHMMSS.md`
15. 最新Accepted Handoff／Status／Review
16. Source確認、矛盾追跡または監査が必要な場合だけRaw History

Historyを最初から全件読む必要はない。ただし、Lossless再整理、矛盾、旧判断、User Instructionまたは正本の根拠を検証する場合は、対象範囲のRaw Historyを必ずSource Inventoryへ含める。

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
Git／GitHub    : NOT STARTED
```

Phase 1でmacOS MetalとLightning Linux x86_64 Pure CPUのCLI／Minimal Web Runtimeを成立させた。Phase 1-exではDocs再編、Continuity、公開準備、Public Demo／Auto-start、Mac簡易Documentation RAG、Git運用設計およびInitial Commit前整備を扱う。

Git運用は未決定である。ユーザーの明示承認前にGit初期化、Commit、Tag、Remote、Push、公開Repository投入または履歴加工を行わない。

2026-07-27のDocumentation Reconstructionでは次を完了した。

- 493 Docsと6 Demo Images、合計499 EntriesのSource Inventory固定
- Project Continuity Master第1周
- Roadmap第1周
- Current Canonical 6文書の累積再構築
- Phase 1の316 Source Final Lossless Compilationと全件Hash検証
- Phase 1-exの145 Source Interim Lossless Compilationと全件Hash検証
- Shared Rules／Operations／Role Authority／本Handoffの再構築

次はProject Continuity Master／Roadmapの第2周、Public Overview／Concept、README、LICENSE、TERMS_OF_USE、NOTICE、CITATIONおよびCorpus全体検証である。

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

Phase未完了時の通常更新では、完了を装うRecovery Manifestを作らない。必要な場合は臨時Continuity Refreshであることを明示した別Eventを作る。

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
Public／Legal            : reconstruction pending
```

引継ぎ直後の安全な一手は、Public文書を先に想像で作ることではない。Shared再構築RecordとIndexが作成済みか確認し、Project Continuity Master／Roadmap第2周のSourceとしてCurrent、Phase Lossless、Sharedおよび最新Phase 1-ex Historyを取り込む。

## 15. Language Scopeの現在決定

今回の再構築では日本語正本だけを作成する。`docs/project/current/`と`docs/public/`の英語派生版はPhase 1-ex後半でユーザーが改めて判断する。

英語版を作る場合は日本語正本と同じ粒度で一式を作る。概要、抄訳または一部文書だけを正式な英語版として扱わない。作成しない場合も、その判断をInitial Commit前ManifestとPublic Scopeへ明記する。

## 16. 二周方式の完了条件

Project Continuity MasterとRoadmapは、大規模再構築の最初と最後に二周する。

- 第1周：Current、Phase Lossless、Shared、Publicを再構築するための基準。
- 第2周：再構築中に確定したHash、Source Scope、Phase状態、Public／Legal状態およびOpen Workを累積反映する最終照合。

第2周で第1周を短縮、要約または置換しない。更新前後SnapshotとSHA-512を保持し、Phase 1-ex変更RecordとAppend-only Index Snapshotへ記録する。
