# Phase 9 要件 — Experiment and Multi-Governance Research Platform

```yaml
document_id: phase_9_requirements
document_state: accepted_frozen_ready_not_started
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
authority_owner: Nazuna Research
implementation_scope: poc_mvp_three_program_sequence
program_order:
  - phase_9_1_governance_semantic_debt
  - phase_9_2_experiment_multi_governance
  - phase_9_3_context_compaction_recovery_core
```

## 1. 目的

Phase 9は、Phase 6で成立したProvider Registry、Role Lifecycle、Budget、Deadline、Cancel、Recording、Failure Presentation、Rule／Pattern Base Guardrail、Built-in Judge PortおよびGD Compiler入口を再利用し、次の三つを順番に進める。

1. **Phase 9-1**：Phase 6で未成立だったGovernance Semantic中心Debtを有界に決着させる。
2. **Phase 9-2**：Model／Judge／Guard／GD／RAG／Repair／Modeの構成差を比較できるExperiment／Multi-Governance Research Platformを成立させる。
3. **Phase 9-3**：Context Compaction／Recoveryの非Visualな技術Coreを、9-2成立後かつ利用可能量が許す範囲で実装する。

User Decisionにより、まずPhase 9-1を独立Checkpointとして速やかに完了候補へ到達させる。Phase 9-2／9-3を9-1へ混入させてはならない。

## 2. Source Priority／Supersession

2026-08-29時点のHistoryには、Phase 6中心Debtを新Phase 10へ送るSnapshotが存在する。その後の2026-08-30 User Decisionにより、次の境界へ再編された。

```text
Phase 9 : Phase 6中心Debtの有界Rework、Experiment／Multi-Governance、Context技術Core
Phase 10: 全Docs二周、Shared Constitution二周、PADG、Full Runtime Constitution、後半UI再編
Phase 11+: General Web Search、正式Agent Level、Cloud／External R&D／Hardening
```

本書はPhase 9のCurrent設計正本として、上記より古い移管先記述をCurrent計画として採用しない。Historyは改変せず、Phase 8 Closure時にCurrent Roadmap／未解決Registryの残存矛盾をCorrectionする。

## 3. Cross-program Requirements

| ID | 要件 |
|---|---|
| P9-REQ-001 | Phase 6〜8の成立済みSource、Contract、Persistence、User DataおよびCitationを再実装・Rollbackしない。 |
| P9-REQ-002 | Provider、Role、Task、Authority、Configured、Active、ExecutedおよびEvidence Identityを分離する。 |
| P9-REQ-003 | OFF／Unavailable／Unsupported／Deferred／Unknown／FailedをPASSまたは実行済みと表示しない。 |
| P9-REQ-004 | Provider名、Model Path、User固有Path、GD名または固定Hardware値をCoreへHard-codeしない。 |
| P9-REQ-005 | Phase目的の中心経路、Data Integrity、Truthful Failure、次Programへの土台およびUser実画面Candidateで止め、Enterprise Product級HardeningをClosure Blockerへ昇格しない。 |
| P9-REQ-006 | Critical／Major／MVP BlockerだけをCurrent Rework対象とし、Minor／Polish／将来研究はStable未解決Registryへ送る。 |
| P9-REQ-007 | Phase 9-1、9-2、9-3を別Checkpointとして扱い、後段を理由に前段の完了候補Returnを遅らせない。 |

## 4. Phase 9-1 — Governance Semantic Debt Fast Closure

### 4.1 Dedicated Judge／Guard

| ID | 要件 |
|---|---|
| P9-REQ-101 | Selene Dedicated Judgeを実Artifact、明示Manifest、実PromptおよびStrict Output Contractへ接続する。 |
| P9-REQ-102 | Qwen3Guard Dedicated Guardを実Artifact、Target別Category、Line ProtocolおよびStrict Output Contractへ接続する。 |
| P9-REQ-103 | Artifact Path、Revision、Digest、Quantization、Runtime BackendおよびHardware ProfileをEvidence化する。 |
| P9-REQ-104 | Startup Defaultは全Governance Mode OFFを維持し、OFF中にDedicated Role Modelを常時Loadしない。 |
| P9-REQ-105 | OBSERVE／ENFORCE遷移時だけPreflight後にLoadし、OFF／ShutdownでLease終了後に安全に解放する。 |
| P9-REQ-106 | Load、Inference、Deadline、Cancel、UnloadおよびLate ResultをRole Lifecycle／Tracked Worker契約へ従わせる。 |
| P9-REQ-107 | Real Model Call 0／1以上、実行Provider、Stage、Latency、BudgetおよびFailure Reasonを観測可能にする。 |
| P9-REQ-108 | Current HardwareでDedicated Artifactが成立しない場合、失敗StageとResource理由をTyped Evidenceにし、Built-in／Rule-based／Noneの正直なBaselineを維持する。 |

### 4.2 Semantic Criterion／Built-in Evaluator

| ID | 要件 |
|---|---|
| P9-REQ-109 | ARGD／DAGDその他GDのSemantic RuleをNormalized IRからLive Criterionへ変換する。 |
| P9-REQ-110 | Semantic 109件を一律Deferredへ落とさず、対象、非対象、未対応、Unknown、Deferredおよび実評価をRule単位で区別する。 |
| P9-REQ-111 | Built-in Evaluatorが評価可能なCriterionだけを評価し、意味評価不能なCriterionをPASSへ捏造しない。 |
| P9-REQ-112 | Criterion ID、Definition／Rule Revision、Point、Input、Outcome、ReasonおよびEvidence Pointerを保持する。 |
| P9-REQ-113 | Main pre／post、Guard、JudgeおよびRepairで同じCriterion Identityを追跡できる。 |
| P9-REQ-114 | Evaluation Countをselected／evaluated／passed／deviated／unknown／not_applicable／deferredの合計と整合させる。 |

### 4.3 Judge／Repair／Rejudge／Semantic ENFORCE

| ID | 要件 |
|---|---|
| P9-REQ-115 | Independent JudgeがMain Candidateを評価し、Self JudgeとEvidence上で区別される。 |
| P9-REQ-116 | Judge OutputはStrict Decodeされ、Malformed／Timeout／Unavailable／Unsupportedを型付きFailureへ収束する。 |
| P9-REQ-117 | Material DeviationからRepair Candidateを生成し、同一Request ChainでRejudgeできる。 |
| P9-REQ-118 | Repair採用、原Candidate採用、Safe Fallback、Failureの各Presentationを根拠付きで区別する。 |
| P9-REQ-119 | Main Semantic ENFORCEは対応済みActionだけを実行し、Authorityを追加しない。 |
| P9-REQ-120 | Conflict、Priority、Budget、Max Repair、Deadline、CancelおよびLate Result拒否を有界化する。 |
| P9-REQ-121 | Request IDを起点にConfigured／Active／Executed Provider、Frozen Mode、Criterion、Judge、Repair、Rejudge、RecordingおよびFinalを相関する。 |
| P9-REQ-122 | Current ResultとHistorical Resultを分離し、OFF Turnへ過去の実行状態をCurrentとして投影しない。 |

### 4.4 Phase 9-1 MVP停止線

Phase 9-1は次を満たした時点で`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`へ進める。

```text
Dedicated Judge／Guard:
  Local ArtifactとAuthorityが成立する場合は、実Load／Inference／Stop／UnloadをUser Macで確認する。
  Hardware／Artifact／Authorityが成立しない場合は、原因をStage別Typed Evidenceで固定し、
  Dedicated PASSを主張せず、UserがResource-gated Dispositionを判断できる。

Semantic:
  109件一律Deferredを解消し、少なくとも対応Criterionの実評価Golden Pathを成立させる。

Judge／Repair:
  Judge -> Repair -> Rejudge -> Adopt／Fallbackの決定論的Golden Pathを成立させる。

ENFORCE:
  対応済みSemantic ActionだけがBudget／Authority内で動き、虚偽成功表示がない。

Integrity:
  Conversation、RAG、Citation、Recording、Cancel、RestartへMaterial Regressionがない。
```

Dedicated Artifactが物理的に成立しない場合の`RESOURCE_GATED`は技術PASSではない。ただし、Phase 9-1全体を無期限に止めず、Built-in／Rule-based Baseline成立とUser Dispositionを条件に次Checkpointへ進める。

## 5. Phase 9-2 — Experiment／Multi-Governance／Semantic Research

Phase 9-2は9-1のController ReviewおよびUser Checkpoint後に詳細Freezeする。現時点では次を必須境界として予約する。

| ID | 要件 |
|---|---|
| P9-REQ-201 | `experiment_id／run_id／request_id`、Effective Config Snapshot、Model／Artifact／Definition／Plan Digestを持つ。 |
| P9-REQ-202 | Main／Judge／Guard／GD／RAG／Repair／Modeの構成差を同一Caseで比較する。 |
| P9-REQ-203 | Self JudgeとIndependent Judge、定量と定性、Human ReviewとLLM Reviewを混同しない。 |
| P9-REQ-204 | Multiple Definition、Conflict、Suppression、Repair Propagation、Manual／Static／Dynamic Routingを比較する。 |
| P9-REQ-205 | 削除・更新済みSource FactとHistorical Conversation ContextのFreshness Governanceを実験対象にする。 |
| P9-REQ-206 | 無関係Project DocsのFalse-positive Retrieval／GroundingとStrict NO_HITを比較する。 |
| P9-REQ-207 | Source Authority／ProvenanceとCorrection Acceptance／Belief Revision SuccessをVersion付きCaseとして評価する。 |
| P9-REQ-208 | Strict BufferとProgressive Presentationを分離し、既表示Chunkは回収できないことを正直に扱う。 |
| P9-REQ-209 | Manual URL Fail-closed時のMain Model Call 0を含むTurn Execution Traceを観測可能にする。 |

## 6. Phase 9-3 — Context Compaction／Recovery Technical Core

Phase 9-3は9-2成立後、利用可能量、As-builtおよびUser優先順位を再評価して詳細Freezeする。実装しない場合も予約は失われない。

| ID | 要件 |
|---|---|
| P9-REQ-301 | Context Capacity、Usage、Effective Budget、Working Reserve、Safety MarginおよびPressure Stateを分離する。 |
| P9-REQ-302 | 自動CompactionのDefaultをOFFとし、OBSERVEはContextを変更しない。 |
| P9-REQ-303 | ENFORCE／Manualは実行前Snapshotを作成し、Atomic切替失敗時に旧ContextへRollbackできる。 |
| P9-REQ-304 | Original Chat、Structured Context、Recovery IndexおよびSelective Rehydrationを分離する。 |
| P9-REQ-305 | Original Chatを自動削除せず、失われた文章を生成的に復号したと主張しない。 |
| P9-REQ-306 | Handoff生成、Manual Compaction、RecoveryおよびGovernance TraceのAPI／Event／Identity ContractをUI非依存にFreezeする。 |
| P9-REQ-307 | Visibility、Persistence、RedactionおよびRetentionを別契約として扱う。 |
| P9-REQ-308 | Runtimeが観測できないHidden Reasoningを捏造しない。 |

## 7. Scope外

- Project全Docs統合／Full Closure、全Stable Docs妥当性再確認。
- `docs/project/shared/constitution/`完全版。
- PADG／Portable Autonomous Development Governance Package。
- Full Runtime Constitution。
- Settings／Sidebar／Right-side Observatoryを含む大規模Visual UI再編。
- Citation／Sourceを右Panelへ全面移送する最終UI。
- General Web Search／Automatic Search／Hostile-site Sandbox。
- 正式なMARGPA Development Agent Level 1〜3、Generic MCP、Dynamic Sub-Agent。
- Cloud／Home Server／Enterprise Hardening／External R&D。
- 未解決0件または製品品質をPhase 9 Closure条件にすること。

## 8. Phase全体停止線

Phase 9全体のMilestoneは`Composable Multi-Governance Research Platform`である。9-1、9-2、9-3の各Checkpointを独立評価し、9-3がResource上見送られた場合は未実装範囲を明示したうえでPhase 9 Closure DispositionをUserが決める。
