# Phase 10 READY Portable Autonomous Development Governance Package 二周編纂予約

```yaml
document_id: phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_20260828091200
document_type: append_only_planned_work
document_state: accepted_user_direction_not_started
language: ja
recorded_at: 2026-08-28 09:12:00 JST
decision_authority: user
target_gate: phase_10_ready_before_commit_push
formal_name: Portable Autonomous Development Governance Package
short_name: PADG Package
package_id: portable-autonomous-development-governance-package
japanese_name: 移植可能自律開発統治パッケージ
source_project_mutation_authorized: false
parent_directory_write_authorized: false
implementation_authorized: false
supersedes_naming_only:
  - phase_10_ready_portable_development_governance_package_reservation_20260823154121
retains_schedule_from:
  - phase_7_phase_9_phase_10_closure_ready_sequence_correction_ja_20260823192316
```

## 1. Decision

2026-08-28の対話に基づき、従来の`Portable Package`および`Portable Development Governance Package`という作業名を、正式名称`Portable Autonomous Development Governance Package`へ変更する。短縮名は`PADG Package`、Directory／Package ID候補は`portable-autonomous-development-governance-package`とする。

本Packageは単なる一般的な開発Rule集ではない。Automation、Cross-provider、Manual／Auto Compaction、Recovery、Agent／Task間Role分離、Codexタスク間情報共有・伝達、Long-running Execution、Authority、EvidenceおよびDevelopment Constitutionを、別Projectへ移植可能な体系として扱う。

正式な説明用Subtitleは次を候補として固定する。

```text
Cross-provider Automation, Agent Orchestration,
Compaction Recovery, Role Separation,
Authority, Evidence, and Development Constitution
```

`Autonomous`は常時完全自動または無制限Authorityを意味しない。Manual ApprovalからGate-only Autonomousまで、異なる自律度を安全に統治するPackageであることを意味する。

## 2. Existing Reservationsとの関係

本書は次の既存要件を削除しない。

- Phase 9 ClosureはSpecial／Minimal Closureとし、大規模統合をPhase 10 READYへ送る。
- Phase 10 READYでPhase 3〜9の累積DocsをLosslessに統合する。
- 統合済みSourceから`docs/project/shared/constitution/`を編纂する。
- Project固有成分をSanitize／ParameterizeしたPortable Packageを作成する。
- Portable PackageではPhase 1-exの一般化可能な内容をPhase 1へ統合し、`phases/phase_1/history/index/`を持たせる。
- 新規Projectと既存Projectへの導入、Conflict、Rollback、ValidationおよびSource Coverageを検証する。
- Package候補配置先である親`MARGPA-RUNTIME-LLM/`直下へのWriteは、その時点のUserによるExact Authorityを別途必要とする。

本書が更新するのは、正式名称、Source走査方式、Common／Provider分類、Provider Directoryおよび二周編纂Acceptanceである。既存History Fileは変更しない。

## 3. Three-layer Separation

次の三つを別Artifactとして維持する。

```text
1. <project-root>/constitution/
   製品RuntimeのAgent／ToolへBindingするMachine-readable Constitution。

2. <project-root>/docs/project/shared/constitution/
   開発Automation／Cross-provider運用のRepository内Canonical Source。

3. <parent-root>/portable-autonomous-development-governance-package/
   Project固有成分を除き、他Projectへ移植するPADG Package。
```

`docs/project/shared/constitution/`とPADG Packageは同じ論理分類を共有するが、同一Artifactではない。Source側のCanonical RevisionからPortable派生物を作成し、Portable側からSource側へ暗黙同期しない。製品Runtime用`constitution/`もPADG Packageから自動的にAuthorityまたはTool Bindingを受け取らない。

## 4. Execution Timing

正本の実行順序は次のとおりとする。

```text
Phase 9 Special／Minimal Closure
        ↓
Phase 10 READY
        ↓
Phase 3〜9 Lossless Docs Compilation
        ↓
全Docs第1周走査
        ↓
docs/project/shared/constitution/ 初回編纂
        ↓
PADG Package初版作成
        ↓
全Docs第2周独立走査
        ↓
抜け漏れ／誤分類／Provenance／Coverage再確認
        ↓
必要に応じて第2版編纂
        ↓
Acceptance／Clean／Commit／Push
        ↓
User Backup
```

Phase 8のAgent Research Previewでは、既にAcceptedなBounded Constitution ViewまたはResearch Previewを使用できるが、Phase 3〜9全Sourceの完全二周編纂およびPADG Package完成を主張しない。完全編纂はPhase 10 READYの独立Gateとする。

## 5. Prerequisite — Phase 3〜9 Lossless Compilation

PADG Packageの全Docs走査前に、Phase 3〜9で蓄積したCurrent、Phase、History、Index、Handoff、Acceptance、Incident、Automation、Provider、CompactionおよびUser Manual EvidenceをLosslessにまとめ直す。

この先行統合では次を区別する。

- Current Canonical Rule。
- Historical Rule／旧正本。
- Superseded Scheduling／名称。
- Accepted Practice。
- Experimental Practice。
- Provider固有Observation。
- Incident／Near Miss／Failure Pattern。
- Deferred／Not Implemented／Not Verified。
- Product固有要件。
- 他Projectへ一般化できるGovernance知識。

Phase 3〜9統合前の断片だけからPADG Packageを作り始めない。統合途中のStableを完成版と扱わず、最後に成立したMaterial BoundaryからRecovery可能にする。

## 6. First Full Scan／初版編纂

第1周ではRepository内Docsを全走査し、Source Inventory、ClassificationおよびSource-to-Rule Mappingを作成する。

最低限、次を実行する。

1. 全Docs Path、Document ID、Class、State、Revision、TimestampおよびSHA-512をInventory化する。
2. Stable、History、Current、Evidence、Handoff、Index、Planned WorkおよびPublicを区別する。
3. Phase 3〜9 Lossless CompilationとのCoverageを照合する。
4. Provider-neutral RuleとProvider-specific Capability／Operationを分類する。
5. Rule、Template、Schema、Manifest、Role View、Provider ViewおよびAdoption GuideへSourceをMappingする。
6. Project固有情報のSanitize／Parameterize／Exclude判断と理由を記録する。
7. `docs/project/shared/constitution/`の初回Canonical Candidateを作成する。
8. 同じAccepted SourceからPADG Package初版Candidateを派生生成する。
9. File Count、Digest、Broken Link、Identity、Absolute Path、Secret、PrivacyおよびSource Coverageを検証する。

第1版を単に完成扱いせず、第2周の独立Gap Auditへ必ず送る。

## 7. Second Full Scan／Gap Audit／第2版編纂

第2周は第1周の結果だけを読むReviewではなく、全Docs Sourceを改めて走査する。

確認対象は次のとおりである。

- Inventory漏れ。
- Shared Sourceの見落とし。
- Common／Provider-specific誤分類。
- Normative／Descriptive／Historical誤分類。
- Superseded Ruleの誤昇格。
- Provider固有Failureを共通Ruleへ過剰一般化していないか。
- 共通ContractをProviderの現行Capabilityへ不当に縮退させていないか。
- Source Path、Digest、Rule ID、Migration Mappingおよび除外理由の欠落。
- Compaction／Recovery／Automation／Cross-provider／Role分離の相互依存漏れ。
- 新規Project／既存ProjectへのBootstrap、Conflict、RollbackおよびValidation不足。
- Copilot等の未観測Providerについて推測を事実として書いていないか。

Gapが見つかった場合は、第1版を無かったことにせず、Gap Audit Evidence、Correction Mappingおよび新Revisionを残して第2版を作成する。第1版のInventory、Manifest、DigestおよびFindingはAppend-only Evidenceとして保持する。

第2版Acceptance Candidateでは、少なくとも次を成立させる。

```text
All Docs Inventory Coverage        : VERIFIED
Phase 3〜9 Compilation Coverage    : VERIFIED
Shared重点Coverage                 : VERIFIED
Common／Provider Classification    : VERIFIED
Source-to-Rule Traceability        : VERIFIED
Sanitization／Exclusion Mapping    : VERIFIED
New／Existing Project Dry-run      : VERIFIED
Unknown Provider Fabrication       : 0
```

## 8. `docs/project/shared/`重点走査

`docs/project/shared/`は補助資料ではなく、Project横断の開発統治知識が累積した主要Source Corpusとして扱う。Directory名や現行Categoryだけで対象を限定せず、原則として全Fileを重点走査する。

特に次を完全Inventory対象とする。

- Constitution Research／Source Evidence。
- Docs Structure／Stable／History／Index／Lossless規則。
- Automation／Long-running Execution／Recovery。
- Cross-provider Handoff／Independent Review。
- Manual／Auto CompactionとSelective Rehydration。
- Agent／Task間Role分離、Controller／Executor分離。
- Codexタスク間の直接共有、伝達、再作成およびTask Identity。
- Claude固有Long-run、Auto-compaction、利用制限後Recovery。
- Future Copilot Integration Candidate。
- Authority、Delegation、Scope、Root Boundary、Mutation。
- Stop、Resume、Incident、Near Miss、Zero Claim。
- Evidence、Recording、Hash、Digest、Audit。
- Resource／Quota／Budget／利用制限。
- Git、Commit／Push、Backup、Closure、READY。
- Provider Memory非依存、Repository内Source of Truth。
- Portable Package、Adoption、Migration、Sanitization。

`shared/history/`も旧情報として一括除外せず、現行Ruleの由来、Failure Pattern、訂正、非採用案およびProvider実測Evidenceとして走査する。

## 9. Common／Provider-specific Separation

`docs/project/shared/constitution/`とPADG Packageの両方で、次の論理構造を使用する。

```text
common/
providers/
├── codex/
├── claude/
└── copilot/
```

Filesystem上の名称は英小文字を正本候補とする。表示上は`共通／Codex／Claude／Copilot`としてよい。

### 9.1 Common

Providerに依存しない意味Contractを格納する。

- Human Sovereignty／Amendment Authority。
- Authority、Delegation、Scope、Authorization Envelope。
- Gate、Stop、Resume、Incident、Recovery。
- Agent／Task Role Separation。
- Cross-provider Handoff Contract。
- Automation State Machine。
- Manual／Auto Compaction Recovery Contract。
- Evidence、Audit、Recording、Zero Claim。
- Docs Lifecycle、Stable／History／Index／Handoff。
- Resource／Budget／Quota Signalの抽象Contract。
- Provider Capability Manifest Schema。
- Common Rule、Template、Role ViewおよびValidation。

`common/`を、現在の全Providerが偶然対応できる最小公倍数へ縮退させない。共通の意味Contractを定義し、未対応CapabilityはProvider Manifestで`unsupported`、`unavailable`、`manual_only`等として明示する。

```text
Common Contract
        ↓
Provider Capability Manifest
        ↓
Provider-specific Adapter／Operation
```

### 9.2 Codex

- Codex Task間の直接Message／Return／Handoff。
- Task作成、Rename、Archive、Task Identity。
- 別TaskとSub-agentの区別。
- Controller／Designer-Implementer Task分離。
- 利用制限、5時間制限、週間Quota、Context蓄積の観測。
- 自動再開Capabilityの有無とManual Resume。
- Codex固有Approval、Tool、SandboxおよびUI差。
- Codex固有Incident／Failure Pattern／Recovery Evidence。

### 9.3 Claude

- Claude Code Long-running Automation。
- Auto-compaction、Compaction Recoveryおよび利用制限後の自動再開。
- Claude TaskのRole／Provider Identity。
- Claude固有Harness、Tool、Permission、Provider Memory境界。
- Exact Handoff、Recovery Index、Package単位Resume。
- 指示保持、False Completion、自己Review、Evidence表現の実測特性。

### 9.4 Copilot

Copilot併用を将来候補としてDirectoryとCapability Manifest枠だけ予約する。実際のTask、Agent、Approval、Compaction、Auto-resume、Tool、MCP、QuotaおよびHandoffを観測するまで、Provider固有Ruleを推測で作らない。

Copilot導入はPADG Packageの移植性検証にも使用できるが、Provider追加だけで共通Ruleの正当性またはCopilot適合を自動承認しない。

## 10. Candidate Source Structure

### 10.1 Repository Canonical Source

```text
docs/project/shared/constitution/
├── constitution_index_ja.md
├── common/
│   ├── authority/
│   ├── automation/
│   ├── role_separation/
│   ├── cross_provider_handoff/
│   ├── compaction_recovery/
│   ├── evidence_audit/
│   └── documentation_lifecycle/
├── providers/
│   ├── codex/
│   ├── claude/
│   └── copilot/
├── manifests/
├── schemas/
├── templates/
└── views/
```

Exact分割は全Docs第1周Inventory後にFreezeする。Directory案を理由に既存Docsを先にMoveまたは削除しない。

### 10.2 Portable Package

```text
portable-autonomous-development-governance-package/
├── README_ja.md
├── README_en.md
├── common/
├── providers/
│   ├── codex/
│   ├── claude/
│   └── copilot/
├── manifests/
├── schemas/
├── templates/
├── bootstrap/
├── validation/
├── migration/
├── adoption_guides/
└── source_traceability/
```

既存予約にある`docs/`Directory構造の保持、Phase 1／1-ex統合およびHistory／Index移植要件は維持する。上記はPADGのCanonical Entry構造であり、実行時にはSource Coverageと重複を避ける形で`docs/`派生Corpusを接続する。

## 11. Portability／Adoption Principles

- Codex、Claude、Copilotまたは単一VendorをNormative CoreへHard-codeしない。
- Provider固有Operationを`common/`へ混入させない。
- Provider固有Directoryに共通Authorityを再定義させない。
- Capability不存在をFallbackで隠さず、明示Stateとする。
- Package投入だけでAuthority、Write Root、Tool PermissionまたはHuman Approvalを生成しない。
- 新規Projectと既存ProjectでBootstrap／Inventory／Conflict／Adoption Modeを分ける。
- 既存ProjectのRuleを無条件に上書きしない。
- Project固有情報の除外と、一般化可能な知識のLossless保持を両立する。
- RuleごとにSource Path、Document ID、Revision／Timestamp、Digest、TransformationおよびPortable Pathを追跡する。
- Package Revision、Generated View Digest、Stale DetectionおよびRollbackを持つ。

## 12. External Write／Publication Gate

親`MARGPA-RUNTIME-LLM/`直下へのPADG Package作成は現Project Root外Actionである。本書はそのWriteを許可しない。実行時にUserがExact Parent Root、Exact Destination、Create／Write Authority、Existing Target、Symlink、Permission、Backup、Git Boundary、SanitizationおよびPublication Scopeを明示する。

他Userも利用できるPackageを目標とするが、作成完了、公開、配布、License確定、ReleaseまたはSupport Promiseを本予約から導出しない。

## 13. Non-authorization

本書は計画予約であり、次を開始または許可しない。

- Phase 3〜9 Docs Compilation。
- 全Docs走査。
- `docs/project/shared/constitution/`の再編成または既存Docs Move。
- PADG Package作成。
- Copilot接続、契約、課金またはProvider操作。
- Project Root外Read／Write。
- Parent Directory作成。
- Git Stage／Commit／Push／Tag／Release。
- Backup作成または外部公開。

## 14. Final Reserved State

```text
Formal Name                         : Portable Autonomous Development Governance Package
Short Name                          : PADG Package
Japanese Name                       : 移植可能自律開発統治パッケージ
Phase 3〜9 Compilation              : REQUIRED BEFORE FULL SCAN
Full Docs Scan Pass 1               : REQUIRED
Full Docs Scan Pass 2               : REQUIRED
Shared Full Priority Scan           : REQUIRED
Common／Codex／Claude／Copilot Split : REQUIRED
Copilot-specific Rules              : RESERVED／EVIDENCE REQUIRED
Current Implementation              : NOT STARTED
Current External Write Authority    : NOT GRANTED
```
