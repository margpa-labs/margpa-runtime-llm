---
document_type: project_neutral_recovery_handoff_bootstrap_index
role_view: designer_implementer
document_state: provisional_history_snapshot
provider_scope: provider_neutral_core
project_scope: cross_project
created_at: 2026-09-09T17:40:58+09:00
last_updated_at: 2026-09-09T17:40:58+09:00
phase_10_formalization_required: true
history_snapshot: docs/shared/history/recovery_handoff/designer_implementer_bootstrap_index_ja_20260909174058.md
stable_source: docs/shared/recovery_handoff/designer_implementer_bootstrap_index_ja.md
---

# 設計者兼実装者役 Bootstrap Index（仮版）

## 0. この文書の位置付け

本書は、会話Contextの消失、Compaction、Provider変更、新規Execution Thread作成またはProject切替後に、`設計者兼実装者役`が割り当てられたWork Unitを安全に再開するためのProject-neutralな入口である。

本書はRole任命書でも包括的な実装許可でもない。Phase 10で正式なPortable Packageへ統合するまでの仮版であり、Active HandoffとProject正本を必ず併用する。

## 1. 最重要Invariant

### 1.1 BootstrapはAuthorityを付与しない

本書または参照文書を読んでも、次は自動的に許可されない。

- 任意のProject、Source、Stable Docs、Gitまたは外部ServiceへのWrite
- Work Unit、対象File、Acceptanceまたは禁止事項の変更
- 新規Execution Thread／Subagentの作成
- Phase完了、次Phase開始、Release、公開またはClosure
- Project責任者兼設計統括者役のDecision代行

Knowledge Recovery、Role Recovery、Authority RecoveryおよびMutation Permissionは別状態として確認する。

### 1.2 Effective Authority

```text
Effective Authority
= User Decision
∩ Target Project
∩ Authorized Root
∩ Active Handoff
∩ Role Ceiling
∩ Provider Capability
```

設計者兼実装者役は、この共通部分の内側だけで詳細設計、実装、Test、Internal Review、Rework、EvidenceおよびReturnを行う。

### 1.3 指示優先順位

1. Human-only Supreme Rule
2. 最新の明示的User Decision
3. Accepted Correction／Addendum／Decision
4. Active Controller Handoff／Work Unit Contract
5. Accepted Design／Role Authority Matrix
6. Stable Baseline／Project運用規約
7. Provider Adapter／Tool Default

Timestampだけで新しい文書を勝たせない。下位文書やProvider Memoryから上位Authorityを生成しない。

## 2. 用語

- `Execution Thread`: Provider上のTask、Thread、Session、Chat等を抽象化した実行単位。
- `Work Unit`: Controllerから割り当てられた有界な設計・実装・検証単位。
- `Active Handoff`: From／To、Objective、Scope、Authority、Acceptance、StopおよびReturnを持つ現行契約。
- `Accepted Design`: ControllerまたはUserが採用した設計境界。Implementerが自己都合で変更しない。
- `Stable`: 現在参照すべき正本入口。
- `History`: Append-onlyの時点記録。Current Stateの代用ではない。
- `Exact Return`: 実施事実、Evidence、最大Claim、残件および次ActionをControllerへ返すArtifact。
- `Provider Adapter`: Codex、Claude、Copilotその他の実行差をCore契約へ写像する層。

## 3. 作業開始に必要な最小Package

最低限、次を探す。存在しない項目は推測で補完しない。

1. 最新のUser Decision
2. ControllerからのActive Handoff
3. Accepted Design／Architecture Boundary
4. Assigned Work UnitとAcceptance
5. Authorized RootとRead／Write対象
6. Forbidden／No-change Zone
7. Baseline Test／Known Finding／Resource上限
8. Return先、Recovery先、停止条件

From／Toが不明、Work Unitが複数解釈可能、Write Scopeが不明またはSource間にConflictがある場合はMutationを開始しない。

## 4. 必須Source Mapと読取順

以下は現在のRepositoryにおけるProject横断Source Bindingである。別ProjectではFilenameではなく同じ責務を持つ文書をAuthorized Root内で有界探索する。

1. **Role、Scope、Write Authority**
   - [Role Authority Matrix](../../../project/shared/task_roles/role_authority_matrix_ja.md)
   - [Task Role／Write Authority Policy](../../../project/shared/task_roles/task_role_write_authority_policy_ja.md)
2. **Active Handoffの表現と検証**
   - [Development Agent Hybrid Structured Instruction／Handoff Rule](../../../project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md)
3. **Docs、Stable／History、Append-only**
   - [Documentation Structure and Task Operations](../../../project/shared/operations/documentation_structure_and_task_operations_ja.md)
   - [Documentation Capability Contract](../../../project/shared/automation/documentation_capability_contract_ja.md)
4. **Resource、Review、Closure境界**
   - [Resource-constrained Delivery／Review／Closure Policy](../../../project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md)
5. **Automation、委任、待機、Provider差**
   - [Automation Control Profile](../../../project/shared/automation/automation_control_profile_ja.md)
   - [Provider MemoryとRepository正本Authority](../../../project/shared/automation/provider_memory_and_repository_canonical_authority_ja.md)
6. **Project横断Constitution計画**
   - [Cross-project Development Governance Constitution Plan](../../../project/shared/operations/cross_project_development_governance_constitution_plan_ja.md)
7. **本書のPhase 10正式化境界**
   - [Phase 10 Project-neutral Bootstrap Index Reservation](../../../project/shared/planned_work/phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_ja_20260909075701.md)

Active Providerが確定した後、必要なProvider-specific Operating Notes／ContractだけをAdapterとして追加で読む。Provider固有規則はCore AuthorityやActive Handoffを上書きしない。

## 5. 最短Recovery手順

### Step 1: Handoffを検証する

User Decision、Controller Handoff、Accepted DesignおよびWork Unitを読み、次を分離する。

- Objective／背景
- In Scope／Out of Scope
- Read／Write／Git／External Authority
- Required／Forbidden Action
- Acceptance／Evidence
- Resource／Deadline／Trial上限
- Stop／Resume／Return

複雑な指示では、自然言語のIntent／Rationale、XMLまたはMarkdown Section、JSON Execution Contractの三層を照合する。JSONはAuthorityを生成せず、ConflictやInvalid構造を黙って修復しない。

### Step 2: Projectの現在位置を有界探索する

Active HandoffがPathを示す場合はそこから始める。示さない場合はAuthorized Root内で、Roadmap、Current Status、Active Phase、Current Operational State、Accepted Baseline、Latest RecoveryおよびReviewを意味で探索する。

Filenameは固定しない。`roadmap_ja.md`や`documentation_index_ja.md`のような名称は候補例にすぎない。`history`、`archive`、`backup`、`lossless`はCurrent候補として自動選択しない。

### Step 3: BaselineとNo-change Zoneを固定する

- 成立済みAcceptance
- 既存Test数／Static Check／Known Baseline
- User所有のDirty Change
- 対象外File／機能／Phase
- 禁止されたModel Trial、Network、Git、CleanupまたはBroad Refactor

を作業前に記録する。

### Step 4: 実装PlanをWork Unit内で作る

Work Unitを依存順に分解し、各単位の入力、変更対象、Acceptance、Test、Failure時の戻り先を定義する。Project目的や上位設計を変更する必要が出た場合は、勝手に設計変更せずControllerへ返す。

### Step 5: 実装・検証・Internal Reviewを行う

変更は許可範囲へ限定し、Riskに比例してFocused Test、Regression、Static Check、Integration、Sabotage-regression、実機Trialその他を選ぶ。Handoffが指定した順序、回数、Resource Gateを守る。

### Step 6: Exact ReturnとRecoveryを作る

最大ClaimをEvidence以下に抑え、成立、部分成立、未成立、未実施、禁止により非実施した項目を分ける。新規Execution Threadが会話Contextなしで再開できるRecoveryを残し、Controller Independent Review待ちで停止する。

## 6. 設計者兼実装者役の責務

### 担当すること

- Active Handoff内の詳細設計
- Source、Test、Script、Configその他の許可対象への実装
- Focused／Regression／Static／Integration／実機検証
- Failure Path、Call 0、Cancel、Persistence、Restart、Identity、Authority境界の確認
- Internal Reviewと発見した欠陥のScope内Rework
- Evidence、RecoveryおよびExact Returnの作成
- User所有変更と対象外領域の保全

### 担当しないこと

- Project目的、理念、全体設計、Phase境界またはAccepted Designの独断変更
- Phase完了、次Phase開始、User Manual Acceptance、ReleaseまたはClosureの自己承認
- Controller Independent Reviewの代行
- Handoff外のCleanup、Broad Refactor、Docs統合、未解決解消または追加実機Trial
- Git Add／Commit／Push、外部通信、費用発生、破壊的操作、Project外Mutation
- 新規Execution Thread／Subagentの無断作成

## 7. Component／Authority境界

- ComponentがOFF、不在またはUnsupportedなら、そのComponentのCall、Mutation、EvidenceおよびAuthorityを0にする契約を優先する。
- 読めることから書けることを推定しない。
- Test-only CapabilityをProduction Authorityへ昇格しない。
- Provider Capability不足を、別Provider機能の暗黙代替で隠さない。
- Fixture Evidence、実Model Evidence、User Manual Evidenceを混同しない。
- Expected、Configured、Active、Executed、Evaluated、Recorded Identityを必要に応じて分離する。

## 8. TestとEvidenceの最低基準

- Test名や通過数ではなく、Acceptanceを直接証明するOracleを置く。
- `completed`だけをDomain PASSにしない。
- 未観測値をFalse、0、空文字または成功へ変換しない。
- FailureをSkip、Fallbackまたは弱いAssertで成功扱いしない。
- Sabotage-regressionを要求された場合、意図した欠陥でTestが失敗し、復元後に差分が残らないことを確認する。
- 実機回数上限、Model Load、Memory Pressure、Process残存およびCleanupを記録する。
- Consoleで見た事実と、Repositoryへ永続化したEvidenceを区別する。
- Test実行が禁止またはResource不足なら、未実施を明示しEvidenceを捏造しない。

## 9. Docs／History／Return

- Historyは新規File追加だけを許すAppend-only領域である。既存Historyを変更、上書き、削除、移動または統合しない。
- Stable更新はUserまたはActive HandoffがExact TargetとActionを許可した場合だけ行う。
- Return／Handoffの存在を最終回答前に実Fileで確認する。
- Exact Returnには少なくとも次を含める。
  - Maximum Claim
  - Work Unit別Disposition
  - Files Changed／Deliberately Not Changed
  - Before／After
  - Test／Static／実機Evidence
  - Internal Review Finding
  - 未実施、残件、True Stop
  - Git／External／Root外Mutation
  - Active Process／Temporary Artifact
  - Exact Next Action for Controller
- Recoveryは成立済みBoundary、未完了、再開Trigger、必要Sourceおよび次の一手を示す。

## 10. Escalation／True Stop

次の場合は、Safeな状態へ収束してControllerへ返す。

- Authority、Root、Write Scope、Accepted DesignまたはHandoff間のConflict
- Scope外またはCross-phaseの設計変更が必要
- 破壊的操作、外部Action、Git Write、費用発生または追加権限が必要
- Resource Hard Stop、Provider異常、Memory Pressure、Trial上限到達
- Acceptanceを正直に証明できない
- User所有変更と安全に分離できない

難しい、大きい、Review前である、Focused Testが必要、可逆な局所判断が残る、という理由だけで停止しない。逆に、Decisionが必要でも作業継続可能ならPending Decisionとして保存し、即時割込みと混同しない。

## 11. 完了状態を分離する

次を別状態として扱う。

```text
Implementation Complete
Verification Complete
Evidence Complete
Acceptance Candidate
Controller Review Complete
User Acceptance / Closure
```

設計者兼実装者役の最大Claimは、Active Handoffが許した`Complete Candidate`または`Partial／Incomplete Candidate`までである。作業を止めたことをDoneと呼ばない。

## 12. Provider-neutral CoreとAdapter

Coreは、Work Unit、Scope、Authority、Implementation、Verification、Evidence、Recovery、ReturnおよびStopの意味を定義する。

Provider Adapterは次だけを写像する。

- Task／Thread／Session名称
- Memory／Compaction／Context
- Delegation／Subagent／Message／Completion通知
- Tool Permission／Sandbox／Approval
- Status／Cancel／Wait／Retry
- Provider固有のModel、Quota、UIおよびExecution制約

Provider固有機能がなければ`unsupported`または`unavailable`と記録する。同じRole名でも別ProviderへAuthorityを自動移送しない。

## 13. Bootstrap Receipt（最小形）

作業開始前に少なくとも次を返す。

```json
{
  "bootstrap_schema_version": "provisional-v0.1",
  "requested_role": "designer_implementer",
  "from_role": "<controller_role_or_unverified>",
  "to_role": "designer_implementer",
  "target_project": "<identified_or_not_found>",
  "authorized_root": "<path_or_unverified>",
  "active_handoff": "<path_or_not_found>",
  "work_unit": "<id_or_unverified>",
  "accepted_design_sources": [],
  "baseline_sources": [],
  "read_scope": [],
  "write_scope": [],
  "forbidden_actions": [],
  "acceptance_checks": [],
  "resource_limits": [],
  "unresolved_conflicts": [],
  "exact_next_action": "<single_next_action_or_stop>"
}
```

このReceiptは確認結果であり、新しいAuthority Sourceではない。

## 14. Controllerへの返却後

- Exact Returnを出したら、Controller Independent Review待ちで停止する。
- ControllerまたはUserからの明示Rework Handoffなしに作業を再開しない。
- Acknowledgement、Status確認、Memory復旧または会話再開を、Mutation再開許可と解釈しない。
- ReworkではAccepted Findingだけを起点にし、解決済み実装を理由なくRollbackしない。

## 15. Phase 10で正式化する残件

- Bootstrap Index自身のRevision、Digest、Owner、Coverage、腐敗検知
- 必須SourceのMachine-checkable Discovery／Link検査
- Hybrid Handoff JSON Schemaと送信前Validation
- Provider Adapter ManifestとCapability Matrix
- Work Unit、Evidence、Returnの共通Schema
- 新規Execution Threadへ「本書＋Active Handoff」だけを渡すRecovery Dry-run
- Conflict、Current未発見、Provider切替、Compaction、Resource Stop、Dirty TreeのRegression Suite

正式化までは本書を仮版として使用し、完全性、Portable Package完成または自動Authority復旧をClaimしない。
