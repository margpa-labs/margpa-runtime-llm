# Pre-pilot Automation Governance Baseline

```yaml
document_id: pre_pilot_automation_governance_baseline
status: historical_baseline_superseded_for_activation
normative: false
language: ja
created_at: 2026-08-09 19:56:20 JST
updated_at: 2026-08-11 12:20:47 JST
owner_role: プロジェクト責任者兼設計統括者役
current_control_state: PAUSED_ROLE_AUTHORITY_DESIGN
pilot_active: false
```

## 1. 目的

本書は、Phase 2-0 Document-driven Orchestration PilotのReview前に確定した人間の指示、既存運用から得た事実、Incident、未決定の将来予約およびPilot開始Gateを、一つの参照入口に再整理する。

本書は新しいAuthority、最上位規則、Exception、Task作成許可、Commit／Push許可またはPilot Start Eventを生成しない。Normative Sourceは各正本とユーザーの明示指示である。

本書は2026-08-09時点のPre-pilot Baseline記録であり、現行PilotのActivation Gateではない。現行のEffective Authorityは[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)、Accepted EnvelopeおよびAutomation Control Profileで解決する。

## 2. Role Baseline

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両Roleを兼務する。

```text
実行主体 : 当面は兼任
責務定義 : 分離
Stable     : 分離
History    : 分離
Recovery   : 分離
参照関係   : 相互参照
```

兼務は、Authorityの合算、User Gateの代理、運用規則からの免除またはRecoveryの圧縮を意味しない。将来Roleを独立Taskへ分離する場合は、現在の責務とRecoveryをLosslessに切り出す。

Pilot Start Event成立前はTask名を変更しない。成立直後にProvider Capabilityが存在する場合だけ、ユーザーが指定した名称へ変更する。

## 3. Human-only Supreme Rule Authority

最上位規則の新規追加、文言変更、削除、並替え、例外化、候補登録およびそれらの指示を行えるのは、ユーザーまたはユーザーが明示指定した人間だけである。

AI、Role、Task、Agent、Tool、Automation、Providerおよび将来の上位Roleは、最上位規則に1mmも自発的に触れない。事実、Incident、Conflictまたは不明点を報告して停止することだけができる。Docs変更は、人間が明示した対象とActionの範囲に限って代行できる。

## 4. Authorized Root Supremacy

明示されたAuthorized Root／Allowed Path外へ無許可で触れない規則は、全Role、全Task、全Agent、全Tool、全Provider、将来の上位Roleおよび全Automation Levelへ適用する。

「触る」には、Read、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL変更、Temporary Artifact、Cache、Log、Intermediate Output、Symlink追跡、External MountおよびToolの暗黙Accessを含む。

Provider／Sandboxが技術的にAccessを許していることは、User Authorizationを生成しない。違反または疑いを検出した場合は、自分が誤生成したArtifactであっても削除・Cleanup・Rollbackせず、即時停止、Exact State報告および人間の明示指示待ちとする。

## 5. Automation LevelとControl Stateの分離

Automation Levelは、どこまで自動連結できるかを示す。

```text
manual
advisory
bounded_unit
workflow
phase
project
```

Control Stateは、そのLevelを現在実行できるかを示す。

```text
OFF
  自動連結なし。個別の人間指示を必要とする。

ARMED
  Design、Role Authority、Envelope、PreflightおよびREADY Evidenceを満たし、Two-key Activation待ち。

ON
  Accepted EnvelopeとEffective Automation Profile内だけで自動連結可能。

PAUSED
  Resource、Review、User Decision、Capability不足または安全な中断により停止。

EMERGENCY_STOP
  Authority逸脱、Root境界違反、重大な未観測MutationまたはEvidence断絶。人間の明示的な再承認なしに再開不可。
```

Control StateとAutomation Levelは独立である。`project + OFF`は自動実行を行わず、`bounded_unit + ON`は一つのAccepted Work Unit内だけを実行できる。現在のStateは`PAUSED／ROLE_AUTHORITY_DESIGN`である。

## 6. Scope Dimensions

Automationは全体一括Switchだけにせず、少なくとも次を独立して制限できる構造とする。

```text
Project
Phase
Subphase
Role
Task
Tool

Task Creation
Delegation
Filesystem Mutation
Git Mutation
External Mutation
Secret Access
Destructive Action
Continuation
Resource Budget
Evidence
Expiration／Revocation
```

上位Scopeは下位禁止を解除せず、Effective Authorityは最も制限の強い契約に従う。

## 7. READY EvidenceとTwo-key Activation

`ARMED`へ移行するには、最低限次をEvidenceで確認する。

```text
Design Review済み
Role Authority Matrix確定
Authorization Envelope確定
Authorized Root／Allowed Path確定
禁止事項確定
Resource／Capability確認
Stop Condition確定
最初の有界Work Unit確定
```

その後、Control Taskが人間と合意したREADY宣言を行い、後続でユーザーが開始を明示した場合にだけ、`ARMED → ON`へ移行する。片方の発言、類似表現、過去の承認または会話の流れで開始を補完しない。

## 8. Human-private Recovery Isolation

Human-private Recovery AssetはAI Control PlaneのInput、Read／List／Stat対象、Evidence、ValidationまたはActivation Gateにしない。AI Sideはその存在、場所、内容または状態を要求せず、Pilot Authorityの判定に使用しない。

## 9. Git CadenceとLightweight Checkpoint

Commit／Pushは原則として、大きな有界Milestone、Subphaseの主要区切りまたはPhase完了単位で検討する。小さなDocs追記やTask往復ごとにCommit／Pushしない。

ただし、Riskの高い変更、大規模Mutation、Automation Work Unit境界またはRecovery Riskの増大時は、Commit／Pushと分離したLightweight Checkpointを将来検討できる。

```text
local commit
patch
archive
working tree snapshot
manifest付きBackup
```

これらは現在の包括許可ではない。それぞれがFile／Git／Backup Mutationであり、Exact Target、実行者、保存先、復元方法およびユーザー承認を必要とする。

## 10. Mechanical Enforcement Research Reservation

将来、文書上の禁止だけでなく「触ろうとしても通らない」境界を実装する候補として次を保持する。

```text
Path Allowlist
外部DirectoryのRead-only化
隔離Workspace／Worktree
実行前後Mutation Inventory
Authorized Root外Diff検知
Tool WrapperによるPath検証
```

どの候補も現時点で未実装・未承認である。導入自体がPermission、Filesystem、Tool、WorktreeまたはProvider設定のMutationになるため、人間の明示承認、RollbackおよびFalse Positive／Lockout検証なしに実施しない。

## 11. Permission Hardening Research Reservation

AI、Agent、ToolまたはAutomationが作成したDirectory／Fileに対し、Artifactの種類、影響、秘密性、実行可否、所有者およびRecovery要件に応じてPermission／ACLを強化する構想を将来検討候補とする。

本件は未決定である。作成主体がAI側であることはPermission変更Authorityを生成しない。Permission／ACL／Owner／Group／Executable Bitの変更は独立Mutationとし、正確なTarget、Before／After、Platform差、親Directory影響、継承、復元および人間の明示承認を必要とする。

## 12. Multi-provider Reservation

CodexとClaude Code等を併用する構成は、開発速度と他Providerでの運用再現性を検証する将来候補である。現時点では未決定・未承認であり、Phase 2-0初回Work Unitに含めない。

特定Provider、Project、Repository、Absolute Path、Phase、Task名、CommandまたはUIをNormative Coreへ固定しない。CoreはCapability、Authority、Evidence、State、Scope、Stop、RecoveryおよびHuman Gateで定義し、Project固有値はManifest、Provider固有操作はAdapter、Work Unit固有値はEnvelopeへ分離する。

## 13. Evidence AccumulationとConstitutionへの関係

Automation専用Folderは、Pilot、通常運用、Incident、Near Miss、Human Intervention、Cost、Context、Provider差およびRecoveryの事実Evidenceを累積する。

Constitution専用Folderは、人間が明示指示した場合にだけ、Source Trace付きの制度候補、Conflict、Chapter MappingおよびNormative Stateを保持する。AI側は最上位規則候補を自発登録しない。

Agent／Tool本格実装前を原則として、Lossless Source Compilationと章立てしたNormative Constitutionを作成する。情報量、ConflictまたはRiskによっては、ユーザー判断で前倒しできる。

## 14. Future Research Reservation

- Phase 10以降に、Thread内のToken、Context、Turn、Decision、Evidence、未解決事項および参照関係をLosslessに保持・参照・再接続する研究を予約する。
- 単純な要約圧縮／復号だけを既定解としない。
- 現在Phase 10に集約した多数の研究群は、依存関係と境界が明確になった後、Phase 11以降へ分解する。

## 15. Current State／Open Decisions

```text
Control State                    : PAUSED／ROLE_AUTHORITY_DESIGN
Automation Level Draft          : bounded_unit
Design Review                    : role authority redesign in progress
Authorization Envelope          : draft_not_authorized
Capability Preflight             : passed／recheck before task creation
Role Authority Matrix            : design review passed／user acceptance pending
READY Evidence                   : incomplete
Two-key Activation               : not completed
Pilot                            : not started
Task Creation                    : not authorized
Task Rename                      : not executed
Permission Hardening             : undecided
Mechanical Enforcement           : research reservation only
Lightweight Checkpoint Mechanism : undecided
Multi-provider                   : undecided
```

## 16. Related Documents

- [Automation Governance Index](automation_governance_index_ja.md)
- [Automation Control Profile](automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)
- [Constitution Research Index](../constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)
- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Git Workflow Policy](../operations/git_workflow_policy_ja.md)
- [Phase Completion Review／Backup Gate](../operations/phase_completion_review_and_backup_gate_ja.md)
- [Project Responsibility Handoff](../project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Design Governance Handoff](../design_governance_handoff/design_governance_handoff_ja.md)
- [Phase 2 Index](../../phases/phase_2/phase_index_ja.md)
- [Phase 2-0 Pilot Execution Plan](../../phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md)
