# Phase 2-B～2-D Automation Campaign Plan

```yaml
document_id: phase_2_b_to_d_automation_campaign_plan
status: phase_2_b_to_d_technical_complete_terminal_checkpoint
phase: phase_2
campaign_scope:
  - phase_2_b
  - phase_2_c
  - phase_2_d
created_at: 2026-08-14 00:57:11 JST
from_role: User／プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役／Phase 2実装者役
decision_authority: user
automation_level_ceiling: bounded_unit_chained_to_phase_2_d
git_terminal_checkpoint: user_directed
docs_refresh_before_git: required_for_complete_and_incomplete_terminal_states
campaign_started: true
campaign_technical_scope_completed: true
```

## 1. Decision

Phase 2-B、2-Cおよび2-Dを一つのAutomation Campaignとして扱い、内部では依存順に直列実行する。

```text
Phase 2-B Persistence／Lifecycle
  → Internal GO／ADJUST／STOP
Phase 2-C Persistent API／Conversation UX
  → Internal GO／ADJUST／STOP
Phase 2-D Configuration Control Surface
  → B～D Integration Review
  → Terminal Git Checkpoint Commit／Push
  → User Backup Gate
```

B、CおよびDを一つの巨大Mutationまたは並行Writeとして実施しない。各Subphaseを復元可能なMaterial Boundaryとして閉じ、前段Contractへ依存する後段だけを次に開始する。

## 2. Current State／Activation Boundary

本計画のAcceptedは、Campaign開始そのものではない。開始前に次を成立させる。

1. Phase 2-A Final Acceptance。
2. Phase 2-A区切りBackup完了のユーザー報告。
3. Phase 2-B～D Exact Authorization Envelope／Role View／Allowed Path／禁止事項のFreeze。
4. Phase 2設計担当者役とPhase 2実装者役の独立Task準備。
5. Single Writer LeaseとResult／Review Routeの確定。
6. ControllerのREADY／ARMED宣言。
7. その後のユーザー開始宣言。

開始前はSource実装、Task作成、Branch作成、Commit、Push、Data Directory作成またはRuntime Bindingを行わない。

## 3. Role／Task Chain

```text
プロジェクト責任者兼設計統括者役
  → Phase目標、Cross-Phase不変条件、Authority、到達線
Phase 2設計担当者役
  → Subphase Requirements／Architecture／ADR／Exact Handoff
Phase 2実装者役
  → Source／Test実装、Validation、Status
Phase 2設計担当者役
  → 設計適合Review、Finding、再作業、局所Acceptance
プロジェクト責任者兼設計統括者役
  → Scope／Compatibility／Evidence／Closure Review
```

ControllerがRoutine実装を抱えない。各Roleは委譲範囲内を自律判断し、Routine Actionごとに上位RoleまたはUserへ確認しない。例外、Scope外、Conflict、重大Risk、Resource／Provider異常またはHuman-only Gateだけを段階的にEscalateする。

## 4. Phase 2-B Workstream

対象：

- Runtime Data Root Binding。
- Conversation Persistence Adapter。
- Serialization／Storage Envelope。
- Atomic CAS／Operation Idempotency。
- Pending／Terminal Commit。
- Crash Recovery／Interrupted確定。
- Persistent Application Orchestrator。
- Domain-to-Generation Mapper。
- Schema Preflight／Migration／Checkpoint／Rollback。
- Recording Port／Default OFF Hook。

入力：

- `phase_2_a_conversation_domain_requirements_ja.md`
- `phase_2_a_conversation_domain_architecture_ja.md`
- `phase_2_a_conversation_domain_adr_ja.md`
- `phase_2_runtime_data_root_and_recording_architecture_ja.md`
- `phase_2_b_entry_handoff_ja.md`

Phase 2-B Closureでは、Concrete Store、Application Lifecycle、Failure、Migration、Zero-write CompatibilityおよびData Root境界をTest可能な状態へ閉じる。

## 5. Phase 2-C Workstream

Phase 2-BのAccepted Contractへ依存して次を実装する。

- Separate Versioned Persistent API。
- Chat List／History／New Chat／Resume。
- Retry／Regenerate／Branch UX。
- Streaming／Stop／Error／ReconnectとPersistent Stateの整合。
- Browser／Server Source of Truth Cutover。
- Multi-browser Conflictの安全表示。
- Public／Basic Preview／Local ProfileのPersistence Binding分離。

Phase 2-Bが`GO`でない状態でPhase 2-Cへ進まない。既存`/api/v1/chat/*`を暗黙Migrationまたは互換性破壊で置換しない。

## 6. Phase 2-D Workstream

Phase 2-B／CのRuntime／API／UI境界を入力として次を実装する。

- 一般利用者向け設定と研究／開発者向け設定の分離。
- Research／Developer Mode表示切替。
- Config Schema Validation。
- Effective Config／Source／Digest／Diff／Apply Result。
- Runtime変更可能設定とRestart必須設定の分離。
- Feature ModeとRecording ModeのControl Surface Hook。
- SecretをUI、Tracked Config、LogまたはAudit Detailへ書かない境界。

Research／Developer ModeをAuthority昇格、Policy解除、Tool Permission拡張またはProtected Research Captureの有効化として扱わない。

## 7. Internal Material Gates

各Subphase終了時に次をControllerが統合判定する。

```text
Technical Result          : PASS／FAIL
Design Conformance        : PASS／FAIL
Compatibility             : PASS／FAIL
Scope／Authority           : PASS／FAIL
Target／Regression Test   : PASS／FAIL
Static／Link／Schema       : PASS／FAIL
Restart Point             : exact path／state
Recommendation            : GO／ADJUST／STOP
```

RoutineなTask／Reviewごとの全文Snapshotは作らない。B、C、DのClosure、重大な設計Freeze、不可逆Mutation前または復元Riskが生じた地点をMaterial Boundaryとし、途中はCompact Status／Receipt／Deltaへ集約する。

## 8. Resource／Context Safe Pause

利用可能量、Credit、Context、Providerまたは実行時間の限界で継続が危険な場合、未完了をCompleteと表記しない。可能な限り現在のWork Unitを次の一貫したCheckpointへ閉じる。

- Last Accepted Subphase／Work Unit。
- Current Source／Test State。
- 未完了Path／Finding。
- 最後に合格したValidation。
- 次のExact Action。
- Restart Reading Order。
- Automation／Task／Writer Lease State。

安全なCheckpointへ閉じられない場合は追加Mutationを止め、Unsafe／Unknown Stateとして報告する。

## 9. Terminal State

CampaignのTerminal Stateを次に分ける。

```text
COMPLETED_D:
  Phase 2-Dまでの設計、実装、Review、Validation完了

SAFE_PAUSE:
  後続再開可能な一貫した状態で一時停止

SAFE_STOP:
  GO不能だが、既知の状態とRollback／再設計入口を確定

UNSAFE_STOP:
  Authority、Secret、Integrity、RepositoryまたはData Safetyが未解決
```

`COMPLETED_D`、`SAFE_PAUSE`または`SAFE_STOP`では、状態を正確にDocsへ反映してTerminal Git Checkpointへ進む。`UNSAFE_STOP`では、外部送信となるPushを機械的に強行せず、追加Mutationを停止してUserへ報告する。

## 10. Terminal Git Checkpoint／User Direction

ユーザーは、Phase 2-Dまで完了した場合だけでなく、Campaignが途中で安全停止した場合も、最後にCommit／PushしてRemoteへ復元点を残す方針を指示した。

Commit／Push前に次を完了する。

1. 完了／未完了を偽装しないPhase Index、Roadmap、StatusおよびRestart Point。
2. 当該時点で完了したScopeのTarget／Regression／Static／Link／Schema Test。
3. Commit Candidate TreeとOutgoing Historyに対するPrivacy／Secret／不要物Scan。
4. Runtime Data、Model、`.venv`、Cache、Secretおよび許可外ArtifactがStagedされていないことの確認。
5. Expected Path Set、Unexpected Path、Deletion、PermissionおよびSymlinkの確認。
6. Repository-local公開Identity、Remote、BranchおよびUpstreamの確認。
7. Staged Diff Reviewと`git diff --cached --check`。

### 10.1 Mandatory Docs Refresh before Commit／Push

`COMPLETED_D`、`SAFE_PAUSE`または`SAFE_STOP`のいずれでも、Commit／Push前に必ず現在地をDocsへ反映する。

- `docs/public/roadmap_ja.md`の現在進捗、完了済み、未完了、次ActionおよびKnown Limitation。
- `docs/project/phases/phase_2/phase_index_ja.md`のActive Subphase、Terminal State、Validation、Restart PointおよびUser Gate。
- 当該CampaignでMeaningまたは運用状態が変わったRequirements、Architecture、ADR、Handoff、OperationsおよびAutomation Evidence。
- Phase 2-B、C、Dそれぞれの完了／未完了／延期／再設計待ちの区別。
- Commit後に別Taskが旧会話なしで再開するためのReading OrderとExact Next Action。

Stable文書は通常の変更前後History Snapshot規則に従い、既存Historyを上書きしない。RoutineなTask単位ではなく、Campaign Terminal StateというMaterial Boundaryで集約する。無関係なCurrent／Shared／Public文書を機械的に全更新せず、今回の状態変化に必要な文書だけを更新する。

Docs Refresh後に、相対Link、状態表現、Snapshot一致およびGit Candidate Treeを再検証する。RoadmapまたはPhase Indexが旧状態のままの場合、Source Testが合格していてもTerminal Git Checkpointへ進まない。

Commit MessageはTerminal Stateを正確に表す。

```text
COMPLETED_D candidate:
  feat(phase-2): complete persistence ux and configuration control

SAFE_PAUSE／SAFE_STOP candidate:
  chore(phase-2): checkpoint b-d campaign at <restart-point>
```

Incomplete Checkpointへ`complete`、`final`またはPhase Closureを示す表現を使わない。Tag／Releaseは本計画に含めない。

## 11. Git Target／Branch Boundary

Phase 2-B～Dは複数Layerを変更する大規模Campaignであるため、Accepted Git Policy上はWorking Branchが原則である。Exact Branch／Target RefはCampaign開始前EnvelopeでFreezeする。現在の`main`、過去のDirect Pushまたは本計画の存在だけからTargetを推測しない。

Terminal Git処理は次を満たす。

```text
Local Commit created
  → Push succeeds
  → Local HEAD == upstream branch HEAD
  → Remote branch SHA verified
  → Working Tree state reported
  → User Backup Gate
```

Push失敗またはGitHub Authentication待ちの場合、Local CommitをRemote反映済みと表記しない。Remote一致後にだけTerminal Git Checkpoint完了とする。

本計画に対するユーザー指示は、B～D Campaign終端のCommit／Pushを実行線へ含める事前方針である。実行時のExact Repository、Branch、Staged Path、Commit内容およびRemoteが開始前Envelopeと一致しない場合は、Standing Authorizationとして拡張解釈しない。

## 12. Backup Handoff

Terminal Git CheckpointのRemote一致確認後、Controllerは次をユーザーへ報告する。

- Terminal State。
- 完了Subphase／未完了Subphase。
- Commit SHA／Remote SHA一致。
- Test／Static／Sanitation結果。
- Runtime Dataの有無と除外状態。
- Exact Restart Pointまたは次Subphase入口。
- Backup対象の推奨範囲。

その後、ユーザーがBackupを取得する。Controllerまたは他TaskがBackup Locationを探索、読取、作成、削除または検証するAuthorityを本計画から取得しない。ユーザーのBackup完了報告前に、そのBackupを存在済み、復元可能またはAutomation Evidenceとして扱わない。

## 13. Stop Conditions

- Authorized Root／Allowed Path外接触の必要。
- Authority、Scopeまたは目的の拡張。
- Secret／Credential／Private Data混入の疑い。
- 未承認External Service／Cloud／課金。
- Destructive Migration／Data Loss／不可逆Action。
- Working TreeまたはGit History Integrity不明。
- Concurrent Writer／Task Identity混線。
- 安全な一意解がなく、要求または重大Risk受容を人間が決める必要がある。
- Terminal Checkpointへ閉じられないUnsafe State。

Scope内の通常設計、実装、Test修正、Review、再作業およびDocs整合をUser Blockerへ付け替えない。

## 14. Current Authorization State

```text
Plan                         : ACCEPTED
Campaign                     : PHASE 2-B～2-D TECHNICAL COMPLETE／TERMINAL CHECKPOINT
Phase 2-A Final Acceptance   : ACCEPTED BY PHASE 2-B START DIRECTION
Pre-campaign Backup          : USER REPORTED COMPLETE／2026-08-14
Exact Envelope／Role View    : FROZEN PER SUBPHASE／CONSUMED
Phase Designer Task          : PHASE 2-B／2-C／2-D COMPLETE
Implementer Task             : PHASE 2-B／2-C／2-D COMPLETE
Source Mutation              : PHASE 2-B／2-C／2-D ACCEPTED
Git Mutation Now             : TERMINAL CHECKPOINT AUTHORIZED／CANDIDATE READY
Terminal Commit／Push        : INCLUDED IN CURRENT TERMINAL COMPLETION LINE
Post-push User Backup        : REQUIRED HUMAN GATE
Phase 2-B Result             : PASS／GO／528 passed・3 deselected
Phase 2-C Result             : TECHNICAL PASS／GO／567 passed・3 deselected
Phase 2-D Result             : TECHNICAL PASS／GO／613 passed・3 deselected
Integrated Validation       : 272 targeted passed／Ruff・Mypy・Node PASS
Manual Browser Matrix       : USER ACCEPTANCE GATE／NOT TECHNICAL BLOCKER
Phase 2-E                   : NOT STARTED
Current Restart Point        : TERMINAL GIT CHECKPOINT／POST-PUSH USER BACKUP
```

本書はB～Dを一括委任可能なCampaignとして予約するが、Human-defined Supreme Rules、Authorized Root、Role／Docs Authority、Secret、External、Destructive、GitおよびBackupの境界を無効化しない。
