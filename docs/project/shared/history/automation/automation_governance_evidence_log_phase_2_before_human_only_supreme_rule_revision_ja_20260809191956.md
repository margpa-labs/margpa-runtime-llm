# Automation／Governance Evidence Log

```yaml
document_id: automation_governance_evidence_log
status: active_cumulative_evidence
normative: false
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-09 18:51:01 JST
owner: プロジェクト責任者兼設計統括者役
technical_owner: プロジェクト責任者兼設計統括者役
constitution_input: true
phase_2_pilot_input: true
rag_default: true
```

## 1. 目的

本書は、人間＋AI Taskによる実際のProject運用から得た成功、Failure、Near Miss、Human Gate、CostおよびAutomation Candidateを、Phase 2 Document-driven Orchestration Pilotと将来の統合憲法書に入力できる形で累積保持するStable Evidence Logである。

本書はNormative Ruleそのものではない。Observationの記載だけで既存Rule、Authority、禁止事項、ExceptionまたはUser Gateを変更しない。Ruleへ昇格する場合は、該当正本のHistory、Source Trace、Reviewおよびユーザー承認を別途必要とする。

## 2. Evidence分類

```text
RULE_EFFECTIVE
RULE_AMBIGUOUS
RULE_MISSING
RULE_OVERRESTRICTIVE
RULE_UNENFORCEABLE
HUMAN_GATE_REQUIRED
AUTOMATION_CANDIDATE
```

一つのObservationは複数分類を持てる。成功だけでなく、人間が気づかなければ進行していた誤り、Ruleが曖昧でも偶然成功した箇所、停止すべきだった地点および未検知領域を保持する。

## 3. Phase 1-ex Final Closure Baseline

```text
Phase                     : phase_1_ex
Closure Commit            : 30d347e0ce05dd208898a4f876e54139cdcacbda
Full Test                  : 430 passed／3 deselected
Link Check                 : 33 files／667 relative links
Lossless                   : 373／373 reconstructed
Backup                     : 1,211 files／132 directories restored
Backup Archive SHA-512     : 23e6c9ff472c93c23b0d5a079fe332969a51c5b83b5cc51695b487d8811e09c0606115b6a5c66aa7587a5755acd1d40c0fc871e20cd3dcb0f52dc62cb02750c9
Git Postflight             : Local／origin tracking／GitHub remote match
Working Tree               : clean
Tag／Release               : none
```

上記はPhase 1-ex Closureの事実Baselineであり、後続Pilotの性能保証ではない。

## 4. Observation Register

### OGE-P1EX-001 — Exact Git Scope Gate

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
before: 16 modified and 51 untracked documentation files
action: staged scope allowlist and out-of-scope path check
after: 67 staged files, all under README.md or docs/
human_intervention: none after scoped authorization
```

Commit前にStaged PathをExact Allowlistと照合し、Source Code、ConfigおよびTest変更が0件であることを機械的に確認できた。「作業内容がDocsだった」という記憶ではなく、IndexとStaged Treeの事実をGateにできる。

将来は`expected_path_set`、`actual_path_set`、`unexpected_paths`および`deletion_count`をEvidence Schema化できる。

### OGE-P1EX-002 — Final Snapshotの相対Link Near Miss

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
  - HUMAN_GATE_REQUIRED
detected: 7 broken relative links in one final index snapshot
cause: history directory depth was counted one level too shallow
result: fixed before commit; final check 33 files and 667 links passed
```

Stableが正しくても、History配置時の相対Path Rebaseは独立に壊れる。Link CheckがCommit前に実際のNear Missを防いだ。ただし自動修復は誤ったTargetへLinkを張るRiskがあるため、Candidate提示とTarget意味Reviewを分ける。

### OGE-P1EX-003 — Structural PassとSemantic Freshnessの分離

```yaml
classification:
  - RULE_MISSING
  - AUTOMATION_CANDIDATE
observation: hash, link and git checks passed while the top current-state block still contained an older phase status
impact: a reader could see Phase 1-ex in progress despite final closure evidence later in the same document
```

SHA-512、Link、Schema、Git CleanおよびTestが合格しても、文書内の現在地が意味的に新しいとは限らない。`active_phase`、Current Position、README、Roadmap、Phase IndexおよびRecoveryのState Tupleを比較する`semantic_state_consistency` Gateが必要である。

機械的に一つの文字列へ統一するのではなく、`phase_1_ex=complete_accepted`、`phase_2=active_pilot_design`等の論理Stateと各文書の表現を照合する。

### OGE-P1EX-004 — Test後のGenerated Artifact再出現

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
observation: full test and static checks regenerated pyc and cache directories after an earlier sanitation
result: exact cache roots and bytecode only were removed before backup and commit
```

SanitationをTestより先に行っても、TestがCacheとBytecodeを再生成する。完了Flowは`Test → final sanitation → staged scope → commit`の順序を保持する必要がある。

### OGE-P1EX-005 — Privacy／Secret／不要物Scanの時点

```yaml
classification:
  - RULE_OVERRESTRICTIVE
  - AUTOMATION_CANDIDATE
decision: broad project scan is performed only for a commit or push work unit
exception: targeted read-only check for an incident, suspected secret, unexpected artifact or explicit user request
```

毎回のDocs作成、Review、Test、HandoffまたはBackupで広範Scanすると、同じ確認の反復にCostを費やす。Git経路成立後はCommit前にCommit Candidate Tree、Push前にOutgoing Historyを確認し、日常的な全Project Scanは行わない。

### OGE-P1EX-006 — Final Lossless Freeze Boundary

```yaml
classification:
  - RULE_EFFECTIVE
  - RULE_AMBIGUOUS
  - AUTOMATION_CANDIDATE
source_set: 373 files
reconstruction: 373 of 373
```

Final Lossless作成後にFinal Review、Recovery、Backup ReceiptおよびIndexを作ると自己参照が発生する。Freeze後Artifactを明示除外し、個別Hash／Linkで検証する方式で有限のSource Setを保持できた。

一方、Freeze後にどのArtifactを追加できるかが曖昧だと、古いSourceの見逃しへつながる。将来は`freeze_manifest`と`post_freeze_artifact_ledger`を分離する。

### OGE-P1EX-007 — Transactional Closure State

```yaml
classification:
  - RULE_EFFECTIVE
  - RULE_AMBIGUOUS
  - AUTOMATION_CANDIDATE
states:
  - prepared
  - backup_verified
  - committed
  - remote_verified
  - complete_accepted
```

CommitされたFinal Recordが、「Backup／Pushが通った場合だけこのStateが成立する」という条件付き自己記述を持つことで、Commit前に完了を偽装せず一連のClosureを実行できた。

ただし文章だけで状態を解決すると誤解しやすい。PilotではState Machineと必須EvidenceをMachine-readableに分離する。

### OGE-P1EX-008 — Detached Backup Receipt Finalization

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
observation: final Git commit SHA does not exist when the pre-commit archive is created
solution: immutable archive plus detached manifest, receipt and checksum sidecar finalized after remote postflight
```

Archive内に自身の将来Commit SHAを埋めると循環依存になる。Archive本体を変更せず、Detached Manifest／Receipt／SHA Sidecarだけに確定CommitとRemote一致を記録する方式が機能した。

### OGE-P1EX-009 — Stable／History SnapshotのByte一致

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
result: 16 of 16 final stable/history snapshots matched byte-for-byte
```

「Snapshotを作った」という報告ではなく、`cmp`とSHA-512でBefore／After原文がStableと一致することを確認できた。これはDocs History更新の決定論的Automation Candidateである。

### OGE-P1EX-010 — Whitespace FindingのScope分類

```yaml
classification:
  - RULE_AMBIGUOUS
  - AUTOMATION_CANDIDATE
observation: git diff --check reported whitespace only in lossless/history source-preservation artifacts
code_or_stable_error: 0
```

`git diff --check`のExit CodeだけでCommitを拒否すると、原文のMarkdown改行や末尾空白を改変する誘因になる。Path ClassをStable、Source、History、Losslessへ分け、Stable／CodeのFindingはBlockし、History／Losslessは原文保持として個判する。

### OGE-P1EX-011 — Recovery Roleの分離

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
roles:
  - プロジェクト責任者役
  - 設計統括者役
```

プロジェクト責任者役を設計統括者役のRenameまたは置換とせず、専用Stable／History／Recoveryを作り、設計Recoveryを参照する上位編成境界とした。これによりProject GateとTechnical Meaning Ownershipを分離できる。

一方、上位Roleを作ってもAuthorityは自動拡張されない。Recovery GraphはRoleの復元を支援するが、User Gateの代理にはならない。

### OGE-P1EX-012 — Scoped Advance Authorization

```yaml
classification:
  - HUMAN_GATE_REQUIRED
  - RULE_EFFECTIVE
observation: user authorized a bounded sequence through docs, checks, backup, commit and phase-ready gate
constraint: the authorization did not extend to Phase 2 task creation or implementation
```

一度の明示許可で連続作業を実行できたが、許可の終了条件で実際に停止できた。自動化Pilotでは、会話上の「あとよろしく」ではなく、列挙されたAction、Target、上限、ExpirationおよびStopを持つAuthorization Envelopeに変換する。

### OGE-P2DESIGN-001 — Project Responsibility／Design Governanceの兼務とRecovery分離

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
current_role: プロジェクト責任者兼設計統括者役
recovery_model: separate_and_cross_referenced
```

伝達段数だけを増やす独立Taskを置かず、当面は一つのTaskがProject ResponsibilityとDesign Governanceを兼務する。ただし両RoleのStable／History／Recoveryは統合・上書きせず、分離したまま相互参照する。兼務はAuthorityの合算、User Gateの代理または運用ルールからの免除を生成しない。

### OGE-P2DESIGN-002 — AutomationはBinaryでなく段階的Profile

```yaml
classification:
  - RULE_MISSING
  - AUTOMATION_CANDIDATE
levels:
  - manual
  - advisory
  - bounded_unit
  - workflow
  - phase
  - project
```

自動化を単純なON／OFFだけで表すと、Task作成、継続、Mutation、Review、GitおよびPhase Gateの許可範囲を区別できない。LevelとCapability Dimensionを分け、常により制限の強い契約へ解決し、Userがいつでも範囲を縮小または停止できるControl Profileが必要である。

### OGE-P2DESIGN-003 — Authorized Rootは自動化より上位

```yaml
classification:
  - HUMAN_GATE_REQUIRED
  - RULE_EFFECTIVE
scope: all_roles_all_automation_levels_all_providers
```

RoleがProject全体を担当していても、Automation Levelが`project`でも、明示されたAuthorized Root／Allowed Path外への接触は許可されない。Read、List、Search、Stat、Temporary Artifact、Symlink先およびToolの暗黙Accessも接触に含む。将来の上位Role、Agent、ToolまたはProvider Adapterも例外ではない。

### OGE-P2DESIGN-004 — Pilot開始のBackup／Dual Consent Gate

```yaml
classification:
  - HUMAN_GATE_REQUIRED
  - RULE_EFFECTIVE
precondition: large_backup_confirmed
controller_phrase: 準備OK。いつでも開始出来ます。
user_phrase: ok。では開始する。
```

設計完了、Task作成Capabilityまたは過去の同意だけではPilotを開始しない。大規模Backup完了後、Control TaskのReady宣言と後続User開始宣言を順序どおり取得し、対象Profile、Root、EnvelopeおよびStateが一致した時点だけをStart Eventとする。

### OGE-P2DESIGN-005 — Automation／ConstitutionのHard-code禁止

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
core: provider_neutral_and_project_neutral
```

Normative Coreへ特定Project名、Absolute Path、Phase番号、Provider、Tool、CommandまたはUIを埋め込むと、別Project／別Providerへ移植できない。CoreはCapability、Authority、Evidence、State、Scope、Stop、RecoveryおよびHuman Gateで記述し、Project固有値はManifest、Provider固有操作はAdapter、Work Unit固有値はEnvelopeへ分離する。

### OGE-P2DESIGN-006 — Multi-provider Orchestrationは未検証候補

```yaml
classification:
  - AUTOMATION_CANDIDATE
  - HUMAN_GATE_REQUIRED
candidate_providers:
  - Codex
  - Claude Code
adoption: undecided
```

複数Providerを併用すれば得意領域ごとのTask分解と開発速度向上の可能性がある。一方、Authority解釈、同時Write、Context、Evidence、CostおよびRecoveryの差が増える。単一Control Taskから別ProviderへHandoffする構成は将来候補として保持するが、現時点で採用済み、設定済みまたは許可済みと扱わない。

### OGE-P2DESIGN-007 — 最上位規則群は閉集合ではない

```yaml
classification:
  - RULE_AMBIGUOUS
  - AUTOMATION_CANDIDATE
decision: current supremacy rules are extensible through formal amendment
```

現在確認済みの最上位規則を「永久に完全な列挙」と扱うと、新しいExecution Domain、IncidentまたはProvider差から得た重大Ruleを正しく昇格できない。一方、Automation主体が自由に追加すると自己権限拡張になる。追加候補を受け入れつつ、Evidence、Conflict Review、検知、違反時動作、RecoveryおよびUser Decisionを必須化する必要がある。

### OGE-P2DESIGN-008 — Automation EvidenceとConstitution Source Registerの責務分離

```yaml
classification:
  - RULE_EFFECTIVE
  - AUTOMATION_CANDIDATE
automation_evidence: factual_observation_source
constitution_register: source_traced_normative_candidate
```

Automation固有Evidenceと憲法候補を同一文書だけで管理すると、事実と規範候補が混同される。Automation専用Folderは事実Evidenceを累積し、Constitution専用FolderはSource Trace、Chapter候補、ConflictおよびNormative Stateを管理する。双方はLinkするが、同じ内容を異なる意味へ要約して二重正本化しない。

### OGE-P2DESIGN-009 — Pilot開始前Git／Backup Checkpoint

```yaml
classification:
  - HUMAN_GATE_REQUIRED
  - RULE_EFFECTIVE
order:
  - design_review_validation
  - user_authorized_commit_push
  - remote_verification
  - user_large_backup
  - final_readiness_preflight
  - dual_consent_start
```

Pilot開始直前の正本状態をGitとユーザーBackupの両方で固定する。Git HistoryはBackupを代替せず、BackupもRemote Historyを代替しない。Ready候補になったことはCommit／PushのStanding Authorizationではなく、Exact Diffと当該External MutationへのUser明示承認を別途必要とする。

### OGE-P2DESIGN-010 — Authorized Root外Temporary Artifact Near Miss

```yaml
classification:
  - NEAR_MISS
  - RULE_UNENFORCEABLE
  - AUTOMATION_CANDIDATE
observed_at: 2026-08-09 18:51:01 JST
external_persistent_artifact: none
recovery: exact_created_artifact_removed_immediately
```

Docs検証時の一覧集計で、Authorized Root内のPipe処理だけで完結できたにもかかわらず、OS Temporary Namespaceへ一時List Artifactを1件生成した。指定Root外のTemporary Artifactも「触る」に含まれるため、これはAuthorized Root境界のNear Missである。生成直後に当該Artifactだけを削除し、外部に永続Artifactは残さなかったが、削除で初回接触事実は取り消せない。

Root Causeは、Provider／Sandbox上利用可能なTemporary Directoryを、ユーザーが指定したAuthorized Rootの例外と誤って扱ったことにある。Provider CapabilityまたはFilesystem PermissionはUser Authorizationを生成しない。今後はTemporary File、Cache、List、Log、Pipeの中間出力およびToolの暗黙ArtifactもAllowed Path検査の対象とし、Root内だけで完結しない場合は推測実行せず停止する。

## 5. Phase 2 Pilotへの直接入力

Phase 2-0の初回有界Work Unitに次を強制する。

1. 初回はRead-onlyのDocs-only Recovery／Authority Acknowledgementとする。
2. Task作成はユーザーが承認したAuthorization Envelope内の1 Taskに限定する。
3. 同一Working TreeへのWriteはSingle Writer Leaseで直列化する。
4. 成果だけでなく、Authority理解、Stop、Cost、Context、Human InterventionおよびNear Missを記録する。
5. File／Git／External／Secret／Destructive Actionは初回Envelopeの対象外とする。
6. `prepared → acknowledged → running → review_pending → accepted／adjust／stopped`のState Machineを使う。
7. 設計書の存在だけでTask作成またはAuthorityを有効化しない。
8. Pilot開始前に大規模Backupと双方の開始宣言を確認する。
9. Initial Automation Levelは一つの有界Work Unitに制限し、Evidenceなしに上位Levelへ昇格しない。
10. Provider／Project固有値をNormative CoreへHard-codeしない。
11. Automationの事実EvidenceとConstitutionの制度候補を分離して相互参照する。
12. Pilot開始前にUser承認済みGit Checkpoint、Remote一致および大規模Backupを完了する。
13. Temporary Artifactを含む全Write TargetをAuthorized Root／Allowed Pathに対してPreflightし、ProviderがWrite可能であることをUser Authorizationと解釈しない。

## 6. 統合憲法書へのChapter Mapping

| Evidence | Constitution Candidate |
|---|---|
| Exact Git Scope Gate | Mutation and Change Control／Evidence Audit |
| Link Near Miss | Document Source of Truth／Evidence Audit |
| Semantic Freshness Gap | Document Source of Truth／Governance Test |
| Post-test Cache | Task Lifecycle／Mutation Control |
| Scan Timing | Resource Budget／Git External Mutation |
| Lossless Freeze | Document Source of Truth／Versioning |
| Transactional Closure | Task Lifecycle／Stop Recovery Backup |
| Detached Receipt | Evidence Audit／Backup |
| Snapshot Match | Document Source of Truth |
| Whitespace Classification | Evidence Audit／Exception Process |
| Recovery Role Separation | Authority Roles and Delegation |
| Scoped Advance Authorization | Authority／Exception／Human Gate |
| Combined Role／Separate Recovery | Authority Roles／Recovery |
| Gradient Automation Profile | Automation Control／Resource Budget |
| Authorized Root Supremacy | Absolute Prohibition／Mutation Control |
| Backup／Dual Consent | Human Gate／Stop Recovery Backup |
| Hard-code Prohibition | Portability／Provider Adapter |
| Multi-provider Candidate | Delegation／Evidence／Conflict Control |
| Supremacy Rule Extensibility | Amendment／Rule Priority |
| Evidence／Constitution Separation | Evidence Audit／Source of Truth |
| Pre-pilot Git／Backup Checkpoint | Stop Recovery Backup／Human Gate |
| External Temporary Artifact Near Miss | Absolute Prohibition／Mutation Control／Provider Boundary |

## 7. 未検証仮説

- 新TaskがDocsだけからProject現在地とAuthorityを一回で正確に復元できるか。
- Task名、Role、Handoff、Write ScopeおよびStopを同一契約として維持できるか。
- Status／Review／Follow-upの往復が再説明Costを実際に減らすか。
- Provider Capabilityが不足する場合に推測実行せず停止できるか。
- 利用可能量／Creditを取得できない場合で、十分であると推測せず小さいWork Unitに留められるか。
- 複数Provider間で同一Rule、Authority、EvidenceおよびStopを維持できるか。
- Automation Levelを下げた際、旧Envelopeの残Actionを確実に失効できるか。

## 8. Update Rule

各Pilot Work UnitのFinal Review時に、Observation ID、Classification、Before／Action／After、Rule、Human Intervention、Stop／Recovery、Cost／Contextおよび次のRule候補を追加する。

本Stableを更新する前後で次へ原文Snapshotを保存する。

```text
docs/project/shared/history/automation/
automation_governance_evidence_log_<phase>_<language>_YYYYMMDDHHMMSS.md
```

## 9. Related Documents

- [Automation Governance Index](automation_governance_index_ja.md)
- [Automation Control Profile](automation_control_profile_ja.md)
- [Constitution Research Index](../constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)
- [Experimental Document-driven Codex Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Git Workflow Policy](../operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../operations/git_publication_sanitation_policy_ja.md)
- [Project Responsibility Handoff](../project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Design Governance Handoff](../design_governance_handoff/design_governance_handoff_ja.md)
