# Cross-project Development Governance Constitution Plan

```yaml
document_id: cross_project_development_governance_constitution_plan
status: planned_preimplementation_gate
normative: false
language: ja
created_at: 2026-08-04 04:34:34 JST
updated_at: 2026-08-09 18:11:00 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
target_gate: before_agent_and_tool_implementation
rag_default: true
```

## 1. 位置付け

本書は、Project内に蓄積している絶対禁止事項、Documentation規則、Role／Authority、Mutation Control、Handoff、Review、Recovery、Backup、Git、Costおよび停止条件を、将来一つの整合した体系として章別文書へLosslessに再編するための計画書である。

現時点では憲法書そのものではなく、作成時期、入力、構造、Portable Package要件およびAcceptanceを固定する予約である。本書だけを根拠に既存規則を置換、要約、廃止または移動しない。

## 2. 作成時期

統合憲法書は、RuntimeのAgent／Toolを本格実装する前の独立Gateで作成する。

それまでは、Phase 2 Document-driven Orchestration Pilotを含む実運用から次を継続収集する。

- Authority逸脱と未遂
- 誤解、暗黙推測およびScope拡張
- Task作成、命名、Handoff、Follow-upおよびReview
- 同一Working Treeでの競合
- Docs-only RecoveryとTask再作成
- Resource／Credit Limitによる安全なPause
- Backup、Git、External MutationおよびUser Gate
- Provider／Tool Capability差
- Ruleの重複、矛盾、欠落、例外および実効性

作成を早める場合も、入力Inventory、Source Hash、Conflict ListおよびUser Approvalを省略しない。

## 3. Canonical予定Path

```text
docs/project/shared/constitution/
├─ constitution_index_ja.md
├─ 01_scope_supremacy_and_definitions_ja.md
├─ 02_absolute_prohibitions_ja.md
├─ 03_authority_roles_and_delegation_ja.md
├─ 04_document_source_of_truth_ja.md
├─ 05_task_lifecycle_and_handoff_ja.md
├─ 06_mutation_and_change_control_ja.md
├─ 07_resource_budget_and_context_ja.md
├─ 08_stop_recovery_and_backup_ja.md
├─ 09_evidence_audit_and_review_ja.md
├─ 10_agent_and_tool_governance_ja.md
├─ 11_exception_and_emergency_process_ja.md
├─ 12_amendment_versioning_and_migration_ja.md
├─ constitution_manifest.yaml
├─ capability_contract_ja.md
├─ provider_adapters/
│  ├─ codex_ja.md
│  └─ claude_code_ja.md
├─ views/
│  ├─ view_manifest_schema_ja.md
│  └─ generated_role_views/
├─ schemas/
│  ├─ rule_schema.json
│  ├─ authority_envelope_schema.json
│  ├─ evidence_schema.json
│  └─ exception_schema.json
└─ templates/
   ├─ authority_envelope_ja.md
   ├─ handoff_ja.md
   ├─ status_ja.md
   ├─ review_ja.md
   └─ recovery_ja.md

docs/project/shared/history/constitution/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

File構成は作成時のInventoryとReviewで調整できる。ただし、統合された体系を一枚の巨大なMarkdownへ押し込まない。`constitution_index_ja.md`を全章、適用範囲、優先順位、現行RevisionおよびDigestの正本入口とし、章別Normative Core、Package Manifest、Capability Contract、Provider Adapter、Role View、Schemaおよび運用Templateを分離する原則を維持する。

単一巨大文書は、Context超過、一部規則の見落とし、重複規則の衝突、章ごとの更新ずれおよびAgentごとの解釈差を生むRiskがある。分割は規則体系の分裂を意味せず、Index、Rule ID、DigestおよびTraceabilityによって一つの憲法正本として束ねる。

## 4. Portable Package目標

`docs/project/shared/constitution/`を新規または他Projectへ配置し、Project固有のManifestとAuthorityを設定するだけで、同じ開発統治体制を即時展開できる状態を目標とする。

Portable PackageはMARGPA固有のAbsolute Path、Repository、Model、Phase番号、個人情報、Credentialまたは特定Task IDを前提にしない。Project固有値は別ManifestまたはAdapterへ分離する。

### 4.1 Normative CoreのHard-code絶対禁止

Automation／ConstitutionのNormative Coreへ、特定Project、Provider、Repository、Absolute Path、Phase番号、Task名、Command、UI、Cloud、個人情報または一つのAgent Frameworkだけに通用する値をHard-codeしてはならない。

```text
Normative Core      : Capability／Authority／Evidence／State／Scope／Stop／Recovery／Human Gate
Project Manifest    : Project固有Root／Role Mapping／Docs Source／Git／Backup
Provider Adapter    : Provider固有Tool／Command／Session Lifecycle
Authorization View : Phase／Task／Work Unit固有Scopeと期限
```

この分離は推奨ではなくPortable Constitutionの成立条件である。新Project、既存Project、異なるProviderまたは将来のAgent／Toolへ適用する際、Normative Coreの書換えを要求する設計は不合格とする。

## 5. Provider-neutral要件

Normative CoreはCodex固有Tool名やClaude Code固有Commandを規則本文へ直結させない。共通Capabilityとして次を定義する。

```text
Task／Session Creation
Task Naming
Instruction／Handoff Delivery
Follow-up Messaging
Status Observation
Wait／Pause／Resume
Filesystem Read／Write
Shell／Test
Git／External Mutation
Human Approval
Recovery／Archive
```

Codex Desktop、Claude Codeその他の実行環境はProvider AdapterでCapabilityへ対応付ける。利用できないCapabilityは推測実行せず、`unsupported`、`manual_required`または`blocked`として扱う。

Provider互換性は「同じCommandが動くこと」ではなく、同じAuthority、Evidence、Stop、RecoveryおよびHuman Gateの意味が保持されることをAcceptance基準とする。

CodexとClaude Code等の複数Providerを一つのOrchestrationで併用し、Control Taskが別ProviderへHandoffする構成は将来の検証候補とする。現時点では未決定・未承認であり、導入済みまたはPhase 2 Pilotの必須構成として扱わない。採用判断では開発速度だけでなく、Cross-provider Authority、Single Writer、Evidence、Context、Cost、停止およびRecoveryを検証する。

## 5.1 Project責任者の規範従属

Project責任者、設計統括者役、Phase担当設計者役、実装者役、対外Docs役、AgentおよびToolの全てを統合憲法書の適用対象とする。Project全体を統括する責任、Taskを編成するCapabilityまたは長期運用上の信頼は、絶対禁止事項、Docs規則、Authority規則その他の運用ルールからの免除を生成しない。

```text
Project Responsibility
  ≠ Constitution Exemption
  ≠ Self-authorized Exception
  ≠ Unbounded Authority
  ≠ Compliance Guarantee
```

承認、確認、Manual TestまたはUser Decisionを待つために停止することはRule違反ではない。規則に従って停止・確認する責任と、規則を免除されることを混同しない。

## 6. 統合対象

少なくとも次を章立てして取り込む。

1. User Authority／Project Decision Authority
2. 絶対禁止事項
3. Workspace／Project Root境界
4. Role／Task／Agent／Tool Authority
5. Mutation Authorization Envelope
6. Documentation Stable／History／Lossless／Index規則
7. Handoff／Acknowledgement／Status／Review
8. Concurrent Work／Write Collision Control
9. Git／Remote／External Service／Secret／Cost境界
10. Backup／Restore／Recovery／Task再作成
11. Resource Limit／Safe Pause／Resume
12. Incident／Deviation／Evidence Retention
13. Provider Capability Adapter
14. Cross-project Bootstrap／Validation
15. Constitution Change／Version／Migration

## 6.1 Rule ID／参照可能性

各Normative Ruleへ一意なRule IDを付与する。最低限、分類、対象、規則、検知、違反時動作、復旧、EvidenceおよびSource Traceを保持する。

```text
CONST-ABS-001
分類      : MUST NOT
対象      : 全Role／全Task／全Agent／全Tool
規則      : 明示的Authorityなしに外部公開を行ってはならない
検知      : External Send／Git Push／Release／Visibility Mutation
違反時    : 即時停止
復旧      : Human Review必須
Evidence  : Actor／Command／Target／Diff／Status／Timestamp
Source    : Existing Rule ID／Source Path／Digest
```

Rule ID Namespace、廃止規則、置換規則およびConflict関係はManifestで管理する。自然言語だけを手掛かりに「たぶん同じ規則」と判断しない。

## 6.2 規範の優先順位

Task指示、Role Authorityおよび上位規範が衝突した場合の優先順位を憲法自身へ記載する。計画上の基本順序は次とする。

```text
絶対禁止／不可侵条件
  > 正式な例外／緊急承認
  > Phase Authorization Envelope
  > Role Authority
  > Phase Contract
  > Task Handoff
  > 通常の会話指示
  > 推測／慣例／善意
```

通常会話、Role名、Tool Permissionまたは作業効率だけで絶対禁止を上書きしない。例外を許容するRuleについて上書きが必要な場合は、例外理由、対象範囲、有効期限、承認者、復旧条件およびEvidenceを持つ正式なExceptionとして扱う。例外不許可のAbsolute Ruleは、通常のException手続でも変更しない。

## 7. Lossless Compilation

統合憲法書は、既存規則の短い要約集として作らない。

```text
Source Inventory／Hash Freeze
  → Rule Classification
  → Duplicate／Conflict／Exception Matrix
  → Chapter Mapping
  → Lossless Draft
  → Source Traceability検証
  → Provider-neutral Core分離
  → Adapter／Template作成
  → Reconstruction Test
  → User Review／Acceptance
```

意味が重複する規則を統合する場合も、Source、原文、例外、適用範囲および変更理由をManifestから追跡可能にする。読みやすさを理由に禁止事項、失敗事例またはAuthority境界を弱めない。

## 8. Agent／Toolへの適用

統合憲法書は、開発担当Taskだけでなく、後続のAgent／Tool設計で使用するGovernance Source候補とする。

ただし、文書を配置しただけでRuntime権限、Tool Permissionまたは実行許可を生成しない。Agent／Toolへ適用する場合は、Machine-readable Policy、Deterministic Enforcement、Human Approval、EvidenceおよびFail-closed境界を別途設計する。

```text
Constitution Exists
  ≠ Loaded
  ≠ Active
  ≠ Authorized
  ≠ Enforced
  ≠ User Approved
```

### 8.1 Constitution View／Compiler候補

Canonical Constitution全文を毎回すべてのTask、AgentまたはToolへ投入しない。正本は全文を保持しつつ、Role、Phase、Task、ProviderおよびAuthorization Envelopeに応じて、適用条文だけを抽出した`Constitution View`を生成する構造を候補とする。

各Viewは最低限、次を含む。

- Constitution Revision／Source Digest
- Role／Phase／Task Identity
- Read Scope／Write Scope
- 適用Rule ID
- 絶対禁止事項
- Stop／Escalation Condition
- Evidence義務
- View生成条件と有効期限

Viewは正本の代替ではなく派生Artifactであり、独自の規則追加、Rule弱体化またはAuthority拡張を行わない。Stale Revision、Digest不一致、未解決Rule Conflictまたは生成条件不足ではFail-closedとする。将来の`Constitution Compiler`は、この抽出、検証およびProvider Adapter向け変換を担う候補である。

### 8.2 Agent／Tool Constitution Enabled Mode

将来のAgentおよびToolには、機能本体のON／OFFと分離して、憲法適用の`ON／OFF`を持たせる。

```text
component.enabled
constitution.enabled
governance.mode = off／observe／enforce
```

- `constitution.enabled = ON`では、Accepted Constitution Revisionと対象Role／Phase／Task／Component用Viewを解決し、Digest、適用Rule、Authority、StopおよびEvidence Contractを検証してからAgent／Tool Actionへ進む。
- `constitution.enabled = OFF`では、Constitution ViewのLoad、憲法固有Evaluationおよび憲法固有Evidence生成を行わない。Governance有無の比較、Ablationおよび研究Baselineとして利用できる。
- `OFF`は`allow all`ではない。Platform Security、Sandbox、File／Tool Permission、Access Control、Human Approval、既存Authority、利用規約、法令およびProject開発中の絶対禁止／Docs／Authority規則を無効化しない。
- Agent本体または対象Tool本体が`OFF`の場合、当該ComponentのConstitution `ON`を実行済みと表示しない。Invalid Combinationとして拒否するか`not_applicable`にする。
- Agentと各Toolは独立したConstitution状態を持てる。Agent側`ON`だけを理由に、呼び出し先ToolのConstitution状態、Tool PermissionまたはHuman Approvalを省略しない。
- Constitution `ON`で必要なRevision、View、DigestまたはEnforcement Capabilityを解決できない場合は、黙って`OFF`へFallbackせずFail-closedとする。
- UIでToggleを表示する場合はResearch／Developer Mode配下を基本候補とし、一般公開または運用ProfileではPolicyにより`ON`固定またはToggle非表示にできる。Default値と公開範囲は後続設計で決定する。

憲法Toggleは実験可能性を提供するが、Authority昇格手段、Security Boundary回避またはProject運用ルールの停止手段ではない。

## 9. Phase 2 Pilotからの入力

Phase 2 Pilotでは、当初はSubphaseまたは一つの有界なWork UnitごとにOrchestrationする。結果が安定した場合だけ、複数Work Unit、Phase完了単位、最終的にはProject完了単位へ対象粒度を拡大する。

Phase 2をOrchestrationの成立性検証、Phase 3を異なるPhase要件、担当Task、ContextおよびEvidence Domainでも同じ骨格が機能するかを確認する再現性・移植性検証と位置付ける。Phase 2の結果が`GO`または条件付き`ADJUST`としてUser Acceptanceされた場合、Phase 3でもPilotを継続し、Evidenceに基づいて粒度と適用範囲を再決定する。Phase 2の成功をPhase 3への無条件自動展開と解釈しない。

粒度拡大はTask数または自律性の無条件拡大ではない。各段階でAuthority遵守、Cost、Recovery、Review品質、Conflict、User Gateおよび停止可能性を評価し、`GO／ADJUST／STOP`を決定する。

PilotのIncident、成功、停止、再開およびProvider Capability差は、憲法書作成時のEmpirical Inputとして保持する。成功結果だけでなく、人間が介入しなければ危険だった地点、規則が曖昧でも偶然成功した地点、停止すべきなのに進行しかけた地点をNear Missとして保存する。

### 9.1 Operational Evidence分類

Phase 2・3の観測結果を少なくとも次へ分類する。

```text
RULE_EFFECTIVE
  既存Ruleが事故、逸脱または情報ロスを実際に防いだ

RULE_AMBIGUOUS
  解釈が分かれ、追加説明または優先順位が必要だった

RULE_MISSING
  想定外事象へ適用できるRuleが存在しなかった

RULE_OVERRESTRICTIVE
  安全性に対して作業能力を不必要に制限した

RULE_UNENFORCEABLE
  文書化済みだが検知または強制ができなかった

HUMAN_GATE_REQUIRED
  自動化せず人間判断へ返すべきだった

AUTOMATION_CANDIDATE
  反復可能で機械化候補になった
```

各EvidenceにはPhase、Work Unit、関係Rule ID、Actor／Role、Before／Action／After、Human Intervention、検知方法、停止・復旧結果、Cost／Contextおよび次のRule変更候補を関連付ける。

### 9.2 Governance Test候補

将来の自動化Testでは、実装機能だけでなく統治規則を検証する。

- 許可Path外Mutationの拒否と停止
- 古いConstitution Revision／ViewのStale検知
- Resource／Credit切れ時のSafe Pauseと未完了表記
- Evidenceなしの完了報告のReject
- Spawn AuthorityなしのTask生成のReject
- Project責任者による自己Authority拡張の検知
- Absolute RuleとTask指示の衝突時に上位規範を選べること
- 停止後にEvidenceから安全にRecoveryできること

Testが通ったことだけでRuleの十分性を証明せず、検知不能領域とHuman Gateを明示する。

## 10. Constitution Research Preview開始条件

永久に「完全」を待ってAgent／Tool Pilotを開始不能にしないため、完成ではなく`Constitution Research Preview v0.x`の開始条件を定義する。

- 優先順位に未解決の重大Conflictがない。
- 全RoleのAuthority範囲が定義済みである。
- 全Absolute Ruleに違反時動作がある。
- Stop、RecoveryおよびBackupが定義済みである。
- Evidence最低要件が定義済みである。
- Resource Limit時の処理が定義済みである。
- Task／Agent／Tool生成Authorityが定義済みである。
- 改憲、Version、MigrationおよびRollbackが定義済みである。
- Currentな人間＋AI Task運用で一度以上試験済みである。

開始後は曖昧条文、Rule Conflict、検知不能、過剰制限、Authority不足、Evidence CostおよびRecovery Failureを記録し、正式手続で改訂する。

## 11. Acceptance Criteria

- 既存の全対象規則がSource／Hash付きで追跡できる。
- 絶対禁止、Authority、Docs、Mutation、RecoveryおよびUser Gateに情報ロスがない。
- MARGPA固有値を別Manifestへ分離できる。
- CodexとClaude Codeの双方についてCapability Mappingと不足時Fallbackを説明できる。
- Folder単体を他ProjectへCopyし、Bootstrap Checklistから同じRole／Docs／Handoff／Review体制を構築できる。
- Provider差がAuthorityの拡大または禁止事項の弱体化を生まない。
- Agent／Toolが文書の存在だけから権限を獲得しない。
- Agentと各ToolでConstitution ON／OFFを独立比較でき、OFFが`allow all`または既存Securityの解除にならない。
- Constitution ONで必要なView／Digestを解決できない場合にFail-closedとなる。
- Constitution自体の変更、History、Version、ReviewおよびRollbackが定義される。
- 新しいTaskが旧会話へ依存せず、Packageから運用を再構築できる。
- ユーザーが内容と適用範囲を明示承認する。
- Project責任者を含む全主体が適用対象となり、自己免除できない。
- Chapter分割後もIndex、Rule ID、RevisionおよびDigestから一つの正本体系として解決できる。
- Role別Constitution ViewをCanonical Sourceから再生成でき、View単独でAuthorityを追加できない。
- Phase 2の成立性EvidenceとPhase 3の再現性・移植性Evidenceを区別して追跡できる。
- 成功だけでなくIncident、Near Miss、Human Interventionおよび停止判断を保持する。
- Research Preview開始条件と改憲手続きが定義される。

## 12. 現在のDecision

```text
Constitution Folder       : reserved／not created yet
Constitution Compilation  : not started
Operational Rule Collection: active
Phase 1-ex Closure Evidence: initial empirical input recorded
Phase 2 Pilot Evidence    : design started／execution pending
Phase 3 Pilot Evidence    : conditional continuation after Phase 2 acceptance
Agent／Tool Application   : future／separate design required
Constitution View／Compiler: planned candidate／not implemented
Codex Portability         : required
Claude Code Portability   : required
User Acceptance           : required
```

## 13. Related Documents

- [Experimental Document-driven Codex Task Orchestration](experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Documentation Rules](../conventions/documentation_rules_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](research_asset_mutation_control_ja.md)
- [Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)

## 14. Phase 1-ex Closureから得た初期Empirical Input

Phase 1-ex Final Closureは、将来の憲法編纂に対する最初の体系的な実証入力を提供した。詳細なEvidenceと分類は[Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)を正本とし、本書では憲法設計への影響だけを示す。

- File／Link／Testが構造上合格しても、Current Stateの意味的鮮度は別Gateとして検証する必要がある。
- Test実行後にCacheや`.pyc`が再生成されるため、SanitationをTest前の一度だけで済ませてはならない。
- Phase Closureは、Docs Freeze、Test、Backup、Commit、Push、Remote一致、完了宣言を明示状態として扱う必要がある。
- Exact Staged Scope、Unexpected Path、Deletion、Whitespace例外をCommit直前に固定すると、意図しない公開面変更を抑止できる。
- Project責任者役と設計統括者役は、相互参照しつつRecoveryとAuthorityを分離する必要がある。
- Backup ReceiptやRemote Commit等、実行後にしか確定しない証跡は、自己参照を避けたPost-freeze Artifactとして扱う必要がある。
- StableとHistory SnapshotのByte一致は、書換え前原文をLosslessに保持したことを機械的に検証できる。
- Scoped Authorizationは、対象、期間、Git／External境界、停止条件および完了点を明示し、次工程へ継承しない。

これらをPhase 2-0 PilotのRecovery、Acknowledgement、State Machine、Evidence Schema、Stop ConditionおよびReview Gateへ反映する。
