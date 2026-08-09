# Phase 2 Pre-pilot Governance Full Consolidation

```yaml
document_id: phase_2_pre_pilot_governance_full_consolidation_20260809195620
status: append_only_evidence
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-09 19:56:20 JST
owner_role: プロジェクト責任者兼設計統括者役
source_scope: user_directives_and_review_inputs_before_phase_2_0_pilot_review
pilot_active: false
control_state: OFF
task_created: false
git_mutation: none
permission_mutation: none
external_mutation: none
```

## 1. 目的

本書は、Phase 2-0 Automation PilotのReview前にユーザーが示した指示、運用上の訂正、Incident、将来予約および補助的な外部Review意見から採用した設計入力を、後から会話を再説明せずLosslessに復元できるよう統合したAppend-only Evidenceである。

本書の作成は、Pilot開始、Task作成、Task名変更、Permission／ACL変更、機械的強制導入、Commit、Push、Backup作成、Authorized Root外Accessまたは最上位規則改訂の許可を生成しない。

## 2. Role構成

当面のControl Taskは`プロジェクト責任者兼設計統括者役`とする。設計統括者役だけを別Taskとして新設し、伝達段を増やす運用は現在採用しない。

ただし、兼務は責務の混同を意味しない。

```text
実行主体 : 兼任
Project Responsibility : 独立責務
Design Governance       : 独立責務
Stable Folder           : 両方を使用
History Folder          : 両方を使用
Recovery Manifest       : 分離
Recovery参照            : 相互参照
```

将来Roleを別Taskへ分離する場合、片方のRecoveryで他方を上書きせず、現在の分離済み責務と履歴をLosslessに引き継ぐ。

現在Taskの名称変更はPilot Start Event成立直後にだけ試行できる。それ以前の名称変更は行わない。Providerに名称変更Capabilityがない場合、代替を推測実行せず停止する。

## 3. 専用Evidence領域

### 3.1 Automation

Automation関連の事実、Pilot結果、Incident、Near Miss、Human Intervention、Cost、Context、Provider差、RecoveryおよびRule Classificationは、次へ集中的に蓄積する。

```text
Stable : docs/project/shared/automation/
History: docs/project/shared/history/automation/
```

### 3.2 Constitution

憲法書関連のSource Trace、Conflict、Chapter Mapping、制度候補および将来のNormative Stateは、次へ分離して蓄積する。

```text
Stable : docs/project/shared/constitution/
History: docs/project/shared/history/constitution/
```

後に次を作成する。

1. 既存運用Sourceを情報ロスなく再統合したLossless正本。
2. 章立てされ、Rule ID、優先順位、適用範囲、検知、違反時動作、Recovery、Evidenceおよび改訂手続きを持つ実際の統合憲法書。

Agent／Tool本格実装前を原則編纂時点とするが、Source肥大化、ConflictまたはRiskにより、ユーザー判断で前倒しできる。

## 4. Automationは段階制御する

Automationを単純な0／1だけで扱わない。自動連結を許す広さは段階的に扱う。

```text
manual
advisory
bounded_unit
workflow
phase
project
```

初回Pilotは、Phaseを小さな有界単位へ分け、原則一単位ずつ進める。Evidence上安全性、有効性、再現性およびCost妥当性を確認できた場合にだけ、Work Unit、Workflow、Subphase、Phase、Projectへ段階的に広げる。

Phase 2は成立性、Phase 3は再現性・移植性の主要観測期間候補である。Phase 2の結果が良い場合はPhase 3でも継続し、結果に応じて範囲を拡張する。

## 5. Automation LevelとControl State

Automation Levelと、現在実行可能かを表すControl Stateは分離する。

```text
OFF
  自動連結なし。個別指示が必要。

ARMED
  Design、Validation、Accepted Envelope、Git Checkpoint、Backup、READY Evidenceが成立し、開始合意待ち。

ON
  Accepted Envelope内だけを自動連結可能。

PAUSED
  Resource、Review、利用可能量、外部状態または安全な中断により停止。未完了をCompleteとしない。

EMERGENCY_STOP
  Authority逸脱、許可Root外Access、重大IncidentまたはEvidence断絶。人間の明示判断まで再開不可。
```

現在は`Control State = OFF`、`Automation Level Draft = bounded_unit`である。

Control ScopeはProject／Phase／Subphase／Role／Task／Tool単位とし、Task Creation、Delegation、Filesystem、Git、External、Secret、Destructive Action、Continuation、Budget、EvidenceおよびExpirationを独立Dimensionとして制御する。

## 6. Pilot開始のTwo-key Activation

Pilotは次の両者合意でのみ開始する。

1. Control Taskが、必要条件を満たしたEvidenceに基づいて「準備OK。いつでも開始出来ます。」と明示する。
2. その後、ユーザーが「ok。では開始する。」と明示する。

前者だけ、後者に似た過去発言、会話の勢い、Phase開始、Design Package完成またはBackup取得だけでPilotを開始しない。

READY Evidenceには少なくとも次を含める。

- Design Review
- Accepted Authorization Envelope
- Authorized Root／Allowed Path
- 最上位禁止とStop Condition
- Recovery
- Resource／Provider Capability
- 最初の有界Work Unit
- Exact Diff Review
- ユーザー明示承認済みGit Checkpoint／Remote一致
- ユーザーによる大規模Backup完了報告
- 未解決事項

READY後にProfile、Root、Envelope Revision、Capabilityまたは外部状態が変化した場合、READYを失効させる。

## 7. 最上位規則群

### 7.1 Authorized Root

指定されたAuthorized Root／Allowed Path外へ無許可で触れないことは、全Role、全Task、全Agent、全Tool、全Provider、将来の上位Roleおよび全Automation Levelへ適用する最上位規則群の一つである。

```text
Project責任者
!= Project外Access Authority

Automation Level = project
!= Filesystem Scope = unlimited

Tool／Sandboxが実行可能
!= User Authorization
```

Read、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL変更、Temporary Artifact、Cache、Log、Symlink追跡および暗黙Accessを含めて適用する。

### 7.2 Human-only Amendment Authority

最上位規則群は将来増える可能性がある。ただし、その追加、変更、削除、並替え、例外化、候補登録およびそれらを指示できるのは、ユーザーまたはユーザーが明示指定した人間だけである。

AI、Role、Task、Agent、Tool、Automation、Providerおよび将来の上位Roleは、最上位規則へ自発的に1mmも触れない。必要性、Conflict、Incidentまたは不足を認識した場合は、事実を報告して停止する。人間がExact Target／Actionを明示した場合にだけ、その範囲の文書反映を代行できる。

## 8. Provider／Project非依存

AutomationおよびConstitutionのNormative Coreへ、特定Project、Repository、Absolute Path、Phase、Task名、Command、UI、CodexまたはClaude CodeをHard-codeしない。

```text
Normative Core : State、Scope、Authority、Evidence、Stop、Recovery、Human Gate
Project Manifest: Project固有Root、Path、Role、Profile
Provider Adapter: Provider固有Capability／API／UI操作
Envelope        : Work Unit固有の対象、Action、期限
```

これにより、新規Project、既存Projectへの埋込み、Codex、Claude Code、将来のAgent／Toolおよび他Providerへ同じ統治構造を移植可能にする。

Claude Code併用と複数Provider間のTask分解は未決定の将来候補である。開発速度、Single Writer、Authority、Evidence、Context、Cost、Provider Capability差およびRecoveryを別Pilotで検証し、Phase 2-0初回Work Unitへ含めない。

## 9. Git／Checkpoint／Backup

Commit／Pushは、よほどの理由がない限り、大きな有界区切り、主要Subphase MilestoneまたはPhase単位で行う。Docsの小さな追記やTask往復ごとに反復しない。

Riskの高い変更、大規模Mutation、Automation Work Unit境界またはContext交代前には、Remote Pushと分離した軽量Checkpointを候補にできる。

```text
Local Commit
Patch
Archive
Working Tree Snapshot
Manifest付きBackup
```

いずれもMutationであり、Standing Authorizationではない。Target、保存先、除外、Metadata、復元方法、External送信およびユーザー明示承認を個別に必要とする。

初回Pilot開始前には、ユーザーが大規模Backupを取得して完了を報告する。AI側はProject外を検査しない。Backupが存在することと、対象包含、暗号化、完了時刻、復元手順およびSample Restoreが確認されていることを区別する。確認項目はRiskと方式に応じてユーザーが決定する。

Pilotを「いつでも開始可能」と判断した後、実際の開始前に、ユーザー承認済みCommit／PushとRemote一致を確認し、その後にユーザーが大規模Backupを取得する順序を予定する。現時点ではいずれも未実施である。

## 10. Constitution設計入力

統合憲法は一枚の巨大Markdownへ潰さず、統合された体系を章別文書へ分離する。予定要素：

- 正本Index
- Scope／Supremacy／Definitions
- Absolute Prohibitions
- Authority／Roles／Delegation
- Docs Source of Truth
- Task Lifecycle／Handoff
- Mutation／Change Control
- Resource／Context／Budget
- Stop／Recovery／Backup
- Evidence／Audit／Review
- Agent／Tool Governance
- Exception／Emergency
- Amendment／Version／Migration
- Schemas／Templates／Provider Adapters

Ruleは参照可能なRule IDを持ち、対象、MUST／MUST NOT、検知、違反時動作、復旧、EvidenceおよびSource Traceを保持する。

憲法全文を毎回Promptへ手Copyせず、Accepted Revision／DigestからRole／Phase／Task／Toolに適用されるRuleだけを抽出したConstitution Viewを使用する。ViewはAuthorityを生成できず、Stale Revision、Digest不一致または未解決ConflictではFail-closedとする。

優先順位、正式Exception、改憲手続きおよびResearch Preview開始条件を明記する。ただし最上位規則の改訂AuthorityはHuman-onlyであり、AIは候補登録もしない。

Agent／Toolは、Component本体や通常Governanceと分離した`constitution.enabled`を将来持つ。ON／OFFは比較・研究用であり、OFFでもSecurity、Permission、Human Approval、Authorityまたは最上位規則を解除しない。

## 11. Evidence分類／Governance Test候補

成功だけでなく、次をEvidence化する。

```text
RULE_EFFECTIVE
RULE_AMBIGUOUS
RULE_MISSING
RULE_OVERRESTRICTIVE
RULE_UNENFORCEABLE
HUMAN_GATE_REQUIRED
AUTOMATION_CANDIDATE
```

特に、人間が介入しなければ危険だった地点、曖昧でも偶然成功した地点、停止すべきなのに進みかけたNear Missを保存する。

将来のGovernance Test候補：

- 許可Path外Mutationを拒否できるか。
- 古いConstitution RevisionをStaleとして検出できるか。
- Resource／Credit切れで未完了をCompleteにせず停止できるか。
- Evidenceなしの完了報告を受理しないか。
- Task／Agent生成Authority違反を止められるか。
- 上位Roleによる自己権限拡張を止められるか。
- 最上位規則とTask指示が衝突した際に上位規範を選べるか。

## 12. 機械的強制／Permission Hardening予約

文書上の禁止を将来「触ろうとしても通らない」境界へ近づける研究候補：

- Path Allowlist
- 許可外DirectoryのRead-only化
- 隔離Workspace／Worktree
- Mutation前後Inventory
- Authorized Root外Diff検知
- Tool WrapperによるPath検証

いずれも未実装・未承認である。

AI／Task／Toolが作成したDirectory／FileへのPermission／ACL Hardeningも未決定の将来候補である。作成主体がAIであることはPermission変更Authorityを生成しない。採用時はExact Target、Owner／Group／Mode／ACL、Before／After、Platform継承、Lockout、Recoveryおよびユーザー明示承認を必要とする。

## 13. Incident Evidence

Pilot設計中、AIがAuthorized Root外の`/tmp/`へ一覧Fileを作成した。これは最上位Root境界への違反である。その後、AIは「自分が作成した不要な一時File」と判断し、ユーザーへ確認せず削除した。これは最初の違反とは別の、無許可Cleanup／Delete違反である。

正しい処理は次だった。

1. 作成を認識した時点で全Mutationを停止。
2. Exact Path、Action、内容、影響を報告。
3. 自己生成Artifactでも削除しない。
4. ユーザーへ削除可否を確認。
5. 明示指示を待つ。

削除済みFileは24行のProject相対Path一覧だった。24 Pathの完全な再構成と存在確認結果は[Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)の`OGE-P2DESIGN-010`へ保存した。24件すべてProject内に存在することを確認したが、この事実はRoot外作成・無許可削除を解消済みまたは軽微扱いにしない。

## 14. Future Research／Roadmap予約

- Phase 10以降に、Task／Thread内のToken、Context、Turn、Decision、Evidence、未解決事項および参照関係を、単純な要約圧縮／復号だけに依存せずLosslessに保持・参照・再接続する研究を予約する。
- Algorithm、Index、Ledger、Graphその他の方式、Cost、PrivacyおよびOCILNSとの関係は将来決定する。
- Phase 10へ集約した多数の研究群は、依存関係、規模および独立性が明確になった時点でPhase 11以降へ再分割する。現在は番号／境界を確定しない。

## 15. Directive Coverage Matrix

| User Directive／Input | Classification | Stable Destination | State |
|---|---|---|---|
| Combined Project Responsibility／Design Governance Role | accepted | Automation Baseline、Phase Index、Continuity | recorded |
| 両Role Folder使用／Recovery分離・相互参照 | accepted | Automation Baseline、Continuity | recorded |
| Pilot開始時だけTask名変更 | accepted gate | Baseline、Execution Plan | not executed |
| Automation専用Stable／History | accepted | Automation Index／Evidence | operational |
| Constitution専用Stable／History | accepted | Constitution Index／Register | operational |
| Pilot／Constitution Evidence継続蓄積 | accepted | Evidence Log／Register | ongoing |
| Automationを段階制御 | accepted | Control Profile／Baseline／Requirements | draft only |
| Phase 2成立性／Phase 3再現性・移植性 | accepted research plan | Constitution／Automation | reserved |
| Git Commit／Pushは大区切り・Phase中心 | accepted | Git Workflow | current policy |
| Lightweight Checkpoint | selected design input | Git Workflow／Baseline | human-gated candidate |
| Authorized Root境界は最上位 | accepted supreme rule | Mutation Control／Baseline | effective |
| 最上位規則の改訂はHuman-only | accepted supreme rule | Mutation Control／Baseline／Phase Docs | effective |
| Automation／Constitution Hard-code禁止 | accepted | Baseline／Constitution Plan | effective design constraint |
| 二者合意によるPilot開始 | accepted | Execution Plan／Baseline | incomplete |
| 大規模Backup後にPilot | accepted gate | Backup Gate／Baseline | not confirmed |
| Backup存在とRestore Evidenceを分離 | selected design input | Backup Gate／Baseline | recorded |
| Claude Code等Multi-provider | undecided future option | Baseline／Phase Index | deferred |
| Constitution章分割／Rule ID／Views | selected design input | Constitution Plan／Baseline | planned |
| Constitution ON／OFF | accepted future mode | Requirements／Constitution Plan | reserved |
| Mechanical Enforcement | selected future research | Mutation Control／Baseline | unimplemented／unapproved |
| AI作成ArtifactのPermission Hardening | undecided future option | Mutation Control／Requirements／Register | no change authorized |
| Lossless Thread Context研究 | future reservation | Requirements／Continuity | reserved Phase 10+ |
| Phase 10群をPhase 11以降へ再分割 | future reservation | Requirements／Continuity | undecided |
| Root外Temp作成／無許可削除Incident | observed violation | Evidence Log／Mutation Control／Continuity | recorded／not normalized |

## 16. Current Stop／Non-actions

```text
Automation Control State : OFF
Pilot                     : not started
Independent Task          : not created
Task Rename               : not executed
Authorization Envelope    : draft_not_authorized
Pre-pilot Git Checkpoint  : not executed
Pre-pilot Large Backup    : not confirmed
Permission／ACL Change    : none
Mechanical Enforcement   : none
Commit／Push              : none
External Mutation        : none
Authorized Root外Access  : none in this consolidation unit
```

次は、本統合を含むPhase 2-0 Design PackageのReviewである。Review合格だけでPilotを開始せず、Git Checkpoint、Backup、Accepted Envelope、READY宣言およびユーザーStart宣言を順番に満たす。

## 17. Related Stable Documents

- [Pre-pilot Automation Governance Baseline](../../../../shared/automation/pre_pilot_governance_baseline_ja.md)
- [Automation Governance Index](../../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Constitution Research Index](../../../../shared/constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../../../../shared/constitution/constitution_source_evidence_register_ja.md)
- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Git Workflow Policy](../../../../shared/operations/git_workflow_policy_ja.md)
- [Phase Completion Review／Backup Gate](../../../../shared/operations/phase_completion_review_and_backup_gate_ja.md)
- [Current Requirements](../../../../current/requirements/requirements_specification_ja.md)
- [Project Continuity Master](../../../../current/project_continuity/project_continuity_master_ja.md)
- [Phase 2 Index](../../phase_index_ja.md)
- [Phase 2-0 Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Authorization Envelope Draft](../../governance/phase_2_0_authorization_envelope_draft_ja.md)

## 18. Validation Evidence

```text
Stable／After Snapshot Byte Match : 16／16 PASS
Recovered Temporary List Paths    : 24／24 EXIST
Selected Markdown Links           : 428 CHECKED／0 MISSING
Git Diff Whitespace Check         : PASS
Runtime Source Diff               : 0
Current ON／ARMED State           : 0
```

Before／After／Initial Snapshotは、Current、Shared Automation、Shared Constitution、Shared OperationsおよびPhase 2のRequirements／Architecture／Governance／Operationsへ保存した。History SnapshotはAppend-onlyとし、Stable更新後のAfter SnapshotはStableとByte一致する。

本検証でRuntime Testは実行していない。本作業はDocs-onlyであり、`src/`、`config/`、`scripts/`および`tests/`の差分が0であることを確認した。Commit／Pushを行わないため、Repository全体のPrivacy／Secret／不要物Scanは運用規則に従って実施していない。
