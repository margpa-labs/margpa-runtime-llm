# Codex側 Automation／Cross-provider／Compaction Governance

```yaml
document_id: codex_side_automation_cross_provider_compaction_governance
status: current
normative: true
normative_scope: codex_side_integrated_governance_projection
language: ja
created_at: 2026-08-21 00:11:03 JST
owner_role: 設計者兼実装者役
decision_authority: user
provider_projection: codex
provider_neutral_core: true
repository_canonical_only: true
authority_effect: no_new_authority
```

## 0. 本書の位置づけ

本書は、Codex側で行うAutomation、異なるProvider間の作業移転、およびManual／Autoを問わないContext Compactionを、一つの統治・復旧モデルとして扱うためのCurrent Stable文書である。

本書が統合する対象は次の三つである。

1. Automationが、どのAuthority、Scope、Control Stateおよび停止条件の内側で連結実行できるか。
2. Cross-provider Handoffが、Provider固有Memoryや会話記憶へ依存せず、Role、Authority、Current StateおよびEvidenceを移転できるか。
3. Compaction後に、圧縮Summaryを正本とせず、Repository Documentationから作業状態と統治状態を再構成できるか。

本書は、既存のCurrent、Shared、Active Phase正本を置き換えない。各分野の詳細は既存正本を優先し、本書はそれらをCodex側の実行・移転・復旧境界へ投影する統合Viewとして機能する。

本書の作成は、Automation Levelの昇格、Automation Control Stateの変更、Task作成、別Providerの起動、Git／GitHub操作、External Access、Secret Access、Permission変更、Destructive Actionまたは既存Stableへの追加Write Authorityを生成しない。

## 1. AuthorityとSourceの優先順位

### 1.1 Effective Authority

Codex側のEffective Authorityは、次の交差として解決する。

```text
Human-defined Supreme Rules
  ∩ Exact Current User Direction／Accepted Completion Line
  ∩ Common Role／Docs Authority
  ∩ Assigned Phase／Work Unit／Task Scope
  ∩ Authorized Root／Allowed Paths／Allowed Actions
  ∩ Available and Accepted Provider Capability
```

いずれか一つでも不明、Conflict、未Acceptedまたは未検証なら、より広い解釈へ進まず、該当Actionを停止する。Provider Capability、Tool Permission、過去の成功、会話の流れ、Role名、Automation LevelまたはCompaction後のSummaryは、不足するAuthorityを補完しない。

### 1.2 Source of Truth

状態、判断、復旧およびAuthorityのSourceは次の順序で解決する。

```text
Exact User Decision／Human-defined Supreme Rules
  > Current／Sharedの現行正本
  > Active PhaseのAccepted Contract／Index／Handoff
  > Authorized Source／Test／Runtime Evidence
  > Append-only History／Review／Incident Evidence
  > Providerが生成したCompaction Summary／会話履歴／RAG出力
  > Provider Memory／Local Cache／暗黙状態
```

下位Sourceは上位Sourceの探索Hintにはなり得るが、上位Sourceの内容、AuthorityまたはCurrent Stateを上書きしない。RAG出力はCitationを持つ派生Viewであり、Authority判定または復旧完了判定では引用元原文を読む。Provider Memory、Session間MemoryおよびRepository外Memoryは正本、Authority、Recovery Sourceまたは完了Evidenceとして使用しない。

### 1.3 Conflictの扱い

複数文書間に不一致がある場合、Timestampだけで新旧を決めない。Document Class、Status、Successor Link、Owner、Decision Authority、Accepted StateおよびCurrent Indexから有効Sourceを解決する。

解決不能なConflictでは、次を行う。

- Conflictする文言、Source Path、現在の解釈候補および影響Actionを分離する。
- 上位規則と衝突する下位Handoffを文字どおり実行しない。
- 安全に分離できるRead-only確認は継続できるが、該当MutationまたはGate通過は停止する。
- AI側で新しい最上位規則、例外または遡及的な許可を作らない。

## 2. 用語と分離すべき状態

### 2.1 用語

| 用語 | 本書での意味 |
|---|---|
| Automation | Accepted Scope内のActionまたはWork Unitを、定義済み到達線まで連結実行する運用 |
| Cross-provider | Codex、Claude Codeその他、異なるProvider／Harness間でRole、作業またはReviewを移転すること |
| Compaction | Provider／HarnessがContextを要約、縮約または再構成し、以前の会話内容の一部または全部を直接参照できなくするEvent |
| Recovery | Repository内SourceからRole、Authority、Current State、EvidenceおよびNext Actionを再構成すること |
| Handoff | 正常系で責任、Authority、入力、Current StateまたはNext Actionを別Role／Taskへ移転するArtifact |
| Recovery Artifact | Context喪失、Task交代、Provider交代またはCompaction後の再構成入口となるArtifact |
| Checkpoint | 後続作業を再開できる確認済み状態。Git Commit、Backup、Recovery ArtifactおよびRuntime Checkpointは同一ではない |

Compaction後に行うのは、会話を元のToken列へ「解凍」することではなく、必要なProject StateをRepositoryから再構成することである。会話の細かな言い回しや未文書化のNuanceまで完全復元できたとは主張しない。

### 2.2 同一視してはならない状態

次のState Dimensionは独立して保持する。

| Dimension | 例 | 意味 |
|---|---|---|
| Automation Level | `manual／advisory／bounded_unit／workflow／phase／project` | 自動連結できる上限 |
| Automation Control State | `OFF／ARMED／ON／PAUSED／EMERGENCY_STOP` | 現在、自動連結が実行可能か |
| Work Unit State | `AUTHORIZED／RUNNING／REVIEW_PENDING／ACCEPTED／ADJUST_REQUIRED／STOPPED／PAUSED_RESOURCE_LIMIT` | 個別作業の進行状態 |
| Recovery State | `NOT_REQUIRED／CHECKPOINT_READY／RECOVERY_REQUIRED／RECONSTRUCTING／VERIFIED／PAUSED_UNVERIFIED／INCIDENT_STOP` | Context再構成の状態 |
| Transfer State | `NOT_PREPARED／FROZEN／SENT／RECEIVED／ACKNOWLEDGED／ACCEPTED／REJECTED` | Provider／Role間移転の状態 |

一つのStateを他のStateへ読み替えない。例えば、Automation `ON`でもRecoveryが`PAUSED_UNVERIFIED`なら作業を再開しない。Handoffが`RECEIVED`でもAuthority ACKとSource読了が未完了なら`ACCEPTED`ではない。Work Unitが機能的に成功しても、Authority Complianceが失敗していればAutomation PromotionのEvidenceにしない。

### 2.3 「Manual」の二義性

`manual` Automation LevelとManual Compactionを区別する。

- `manual` Automation Levelは、Actionごとに人間の開始指示を必要とする実行Profileである。
- Manual Compactionは、人間またはProvider UIがTimingを選んで起動するContext Eventである。

Manual Compactionを行ってもAutomation Levelは変化せず、Automation `ON`でもCompaction Trigger Capabilityが自動付与されない。

## 3. 共通不変条件

Automation、Cross-providerおよびCompaction Recoveryの全てに、次を共通適用する。

1. CapabilityはAuthorityを生成しない。
2. Provider、Role、Task、Agent、ToolおよびAutomation LevelはAuthorized Root境界の例外にならない。
3. 通常運転とAutomationでRole Authority、Docs Authority、History Immutable原則およびHuman Gateを二重定義しない。
4. 既存StableへのWriteは、ユーザーがExact TargetとActionを明示した場合だけ成立する。
5. Existing HistoryはAppend-only／Immutableであり、修正は新規Correction Eventで行う。
6. Provider Memory、Compaction Summary、会話記憶および暗黙状態を正本化しない。
7. 成果物成功、Authority Compliance、Evidence Completeness、Provider ConformanceおよびRecovery Fidelityを独立判定する。
8. 自己申告と独立確認を分離し、観測できない事項を`UNVERIFIED`のまま保持する。
9. 不一致または違反後に、自動Cleanup、Rollback、Retry、証跡改変またはScope拡張を行わない。
10. Resource、Credit、ContextまたはCapability不足を理由に、未完了をCompleteと表記しない。
11. 全Role／Task／Agent／Toolは誤読、Context欠落、権限逸脱および暗黙副作用を起こし得るものとして設計する。上位Roleや長い成功実績を無謬性の根拠にしない。
12. Secret、Credential、個人Chat履歴、Human-private Backupおよび許可外のExternal StateをRecovery Artifactへ収録しない。

## 4. Automation Governance

### 4.1 Automationが追加するもの

Automationが通常運転へ追加するのは、Accepted Completion Line内にある`ROLE_ALLOWED` Actionを、Actionごとの再確認なしに連結できることだけである。

Automationは次を追加しない。

- Role Authority Ceilingの拡張。
- Docs Write Authorityの拡張。
- Git／GitHub、External、Secret、Destructive、Permission／ACLの包括許可。
- Human-only Gateの代行。
- Task／Sub-agent／別Providerの無条件作成Authority。
- Provider MemoryまたはRepository外Stateの利用許可。
- PhaseまたはProject完了の自己承認。

### 4.2 Accepted Envelopeの必要意味

Automationを`ARMED`または`ON`へ移すEnvelopeは、表現形式を固定PackageへHard-codeしない一方、少なくとも次の意味をLosslessに解決できなければならない。

```yaml
authorization:
  decision_authority: exact
  accepted_revision: exact
  activation_event: exact
scope:
  authorized_root: exact
  allowed_paths: exact_or_manifest
  allowed_actions: exact
  prohibited_actions: exact
role:
  archetype: exact
  combined_roles: explicit
  authority_ceiling: exact
continuation:
  maximum_reach: exact
  human_gates: exact
  expiration_and_revocation: exact
resources:
  time_usage_credit: explicit_or_unknown
  context_stop: defined
evidence:
  required_state: defined
  independent_review: defined
recovery:
  canonical_entry: exact
  checkpoint_policy: defined
  stop_and_resume_conditions: exact
```

未知値を無制限扱いにしない。`unknown`は観測不能という明示Stateであり、上限なしを意味しない。

### 4.3 Role-local JudgmentとEscalation

Accepted Scope内のRoutineな設計、実装、Test、局所修正、再Test、必要Evidenceおよび担当内Artifact選択は、委譲されたRoleが動的に判断する。全Actionを最高責任者役またはユーザーへMicro-escalateしない。

次は直属上位へ段階的にEscalateし、該当作業を停止する。

- Scope、Authority、Root、ActionまたはDocs Classの不一致。
- 上位規則、Accepted DesignまたはHuman GateとのConflict。
- Cross-Phase影響、Security／Privacy／Recovery Riskまたは重大Finding。
- Provider／Toolの予期しない副作用、Capability不明またはResource異常。
- Compaction後にCurrent StateまたはMutation Stateを検証できない場合。

### 4.4 Resource／Context Pause

利用可能量、Credit、Quota、ContextまたはService制限を検出した場合、未完了作業を`PAUSED_RESOURCE_LIMIT`または`PAUSED_UNVERIFIED`として停止し、可能なAuthority内で次をRepositoryへ残す。

- 最後に確認済みのCanonical EntryとCurrent State。
- 完了済み／未完了／未確認の分離。
- Created／Modified／DeletedとUnexpected Artifactの有無。
- Test／Review結果と未実施項目。
- Open Finding、次の最小Action、必要Authorityおよび再開条件。

自動で別Provider、別Account、追加課金、低品質Modelまたは大量の代替Taskへ切り替えない。Cross-providerへの切替は新しいTransfer Eventとして扱う。

## 5. Cross-provider Governance

### 5.1 Provider-neutral CoreとProvider Adapter

Role、Authority、State、Evidence、StopおよびRecoveryはProvider-neutralな意味契約として定義し、Provider固有のTool、Command、UI、Task Naming、Memory、Context MarkerおよびInvocation GrammarはAdapterへ分離する。

```text
Normative Core
  → Project／Phase Binding
     → Role／Task View
        → Provider Capability Adapter
           → Runtime Invocation and Evidence
```

AdapterはCoreを広げない。未対応Capabilityは、推測した代替操作へ変換せず、`unsupported／manual_required／blocked`として返す。Promptへ特定Grammarを書いただけの状態を、機械的強制済みと表示しない。

### 5.2 Provider IdentityとRole Identity

Provider名からRoleまたはAuthorityを自動導出しない。同一Providerが複数Roleを担う場合も、異なるProviderが同一Roleを引き継ぐ場合も、Role Binding、Authority Ceiling、Current Authorization InstanceおよびTask Scopeを明示する。

```text
Provider Identity ≠ Role Identity ≠ Authority ≠ Task Ownership
```

Roleの通称、Task TitleまたはProvider Metadataが一致しても、Repository内HandoffとACKがなければ同一Authorityの継続とはみなさない。

### 5.3 Cross-provider Transfer Package

移転Artifactは、固定File数を要求せず、次の意味を一つまたは複数のRepository ArtifactでLosslessに保持する。

```yaml
transfer:
  transfer_id: exact
  from_role: exact
  to_role: exact
  source_provider: declared
  target_provider: declared_or_unknown
  created_at: exact
authority:
  decision_source: exact
  role_and_docs_authority: exact
  authorized_root: exact
  allowed_paths_actions: exact
  prohibited_paths_actions: exact
  human_gates: exact
state:
  current_phase_work_unit: exact
  completed: list
  in_progress: list
  open_findings: list
  unverified: list
  next_minimum_action: exact
evidence:
  source_artifacts: list
  revisions_and_sha512: list
  self_reported: list
  independently_verified: list
  unresolved_conflicts: list
recovery:
  bootstrap_entry: exact
  successor_resolution: defined
  compaction_state: declared
  resume_and_stop_conditions: exact
```

Secret実値、Provider Memory Path、Human-private Backup内容または不要な会話全文をPackageへ含めない。

### 5.4 受領側のBootstrapとACK

受領側は、会話説明またはProvider Memoryではなく、Repository内Artifactから次の順で復元する。

```text
Provider Bootstrap／Current Index
  → Transfer Handoff
  → Current／Shared／Active Phase正本
  → Exact Source／Test／Runtime Evidence
  → Authority・Scope・State照合
  → In-band ACK
```

ACKは単なる`OK`ではなく、少なくとも次を明示する。

- 認識したRole、Scope、Root、Allowed／Prohibited Action。
- 読了済みSourceと未読／未確認Source。
- Current State、Human Gate、Stop ConditionおよびNext Action。
- Provider Capabilityの対応／非対応。
- ACK前に行ったMutationの有無。

`ACKNOWLEDGED`は受領側の理解表明であり、上位Reviewerまたはユーザーによる成果Acceptanceではない。

### 5.5 Single WriterとConcurrent State

同じWorking Tree、同じStable文書または同じRuntime Stateへ、複数Provider／Taskを無調整で同時Writeさせない。

Cross-provider並行作業では、少なくとも次のいずれかを成立させる。

- Exact PathによるSingle Writer分離。
- Worktree／Branch分離。Git操作自体は別Authorityを必要とする。
- 一方をRead-only Reviewerとする。
- Writer交代時にFreeze、Mutation Inventory、HandoffおよびACKを行う。

予期しないConcurrent Diffを検出した場合、その変更を自分の作業として取り込まず、作者、Authorityおよび影響を`UNVERIFIED`として停止する。

### 5.6 Cross-provider Reviewの判定Dimension

Cross-provider Reviewは、次を独立に判定する。

| Dimension | 判定内容 |
|---|---|
| Functional Result | 要件どおり動作したか |
| Authority | Role、Root、Path、ActionおよびHuman Gate内だったか |
| Evidence | 自己申告と独立確認を分け、必要証跡があるか |
| Provider Side Effect | Memory、Permission、Cache、Temporary Area等に未申告Mutationがないか |
| Procedure Fidelity | 宣言したRead／Test／Recovery手順を実際に行ったか |
| Recovery Fidelity | 別ProviderがRepositoryだけから同じCurrent Stateへ到達できるか |

技術成功をGovernance適合へ読み替えず、Governance違反を理由に技術Evidenceを消去しない。

## 6. Compaction Governance

### 6.1 Compactionの基本認識

CompactionはAuthority Eventではなく、Context Lifecycle Eventである。

```text
Compaction
  ≠ Authority Reset
  ≠ Authority Expansion
  ≠ Task Completion
  ≠ Handoff Acceptance
  ≠ Conversation完全復元
```

Compaction前に有効だった禁止、Human Gate、Root境界、Open Findingおよび未完了状態は、明示的に変更されない限りCompaction後も残る。ただし、残っていると記憶で断定せず、Repository Sourceから再確認する。

### 6.2 Manual／Auto／Unknownの差

| Type | Trigger | Before Evidence | 標準対応 |
|---|---|---|---|
| Manual Compaction | 人間またはProvider UIが意図したTimingで起動 | 事前に確保しやすい | Material BoundaryでFreezeし、Recovery EntryとDigestを確認してから起動 |
| Auto Compaction | Provider／HarnessがContext条件等で自動起動 | 直前取得できない場合がある | 通常の作業境界でRolling Recovery Pointを維持し、検知後に再構成 |
| Unknown／Suspected | 明示Markerがなく、内容欠落やContext再構成だけを観測 | 信頼できない | Autoと同じくFail-closedでRecoveryを開始し、Typeは`UNVERIFIED`のまま保持 |

ManualとAutoで異なるのはTriggerの制御可能性とBefore Evidenceの確保可能性であり、Authority、Source Priority、再読込、独立検証および再開Gateは共通である。

### 6.3 Material Boundary Recovery Point

Recovery PointはTurn数や固定File Packageで一律生成せず、情報Loss、State変化、Mutation Risk、Context、Costおよび次の作業規模からMaterial Boundaryを判断する。

代表的な境界は次である。

- Accepted DesignまたはWork Unit開始前。
- Source／Config／Docsの有意なMutation完了後。
- Review、Rework、Human GateまたはProvider交代前。
- 長い処理、複数File変更または大きなContext消費へ入る前。
- Resource Limit、Context LimitまたはProvider不安定化が近いと観測された時。
- Manual Compactionの直前。

Recovery Pointは、少なくともCurrent State、Open Finding、Next Action、Authority、Exact Source Pathおよび必要なDigestを再構成できる粒度とする。毎TurnのSnapshot乱造は行わず、同時に、情報Lossを起こすほど粗くしない。

### 6.4 Manual Compaction Preflight

Manual Compactionを予定する場合、起動前に次を確認する。

1. 現在のMutationが完了、未着手または安全に停止済みである。
2. Current Index、Active Phase Index、Handoff／StatusおよびOpen Findingが現在地を表す。
3. Compaction後に最初に読むArtifactと順序を確定している。
4. 必要なTarget Setを有限にFreezeし、各FileのIdentity、SizeおよびSHA-512を取得している。
5. Hash記録先をHash対象集合から除外し、自己参照を避けている。
6. Secret、個人Chat、Provider MemoryまたはHuman-private BackupをRecovery Sourceへ入れていない。
7. Compaction TriggerがCodex側に提供されていない場合、別操作で模倣せず`manual_required`として人間へ返す。

Manual Compaction後は、Before／After Digest比較だけでなく、必要Sourceの明示的再読込と意味上のCurrent State照合を行う。

### 6.5 Auto Compaction Preparedness

Auto Compactionは直前Timingを制御できない可能性があるため、次を平常運用へ組み込む。

- Material BoundaryごとにCurrent StateをRepositoryへ外部化する。
- 大きな作業を、再開位置が識別できる有界Stepへ分割する。
- Partial MutationとCompleted Mutationを区別できるEvidenceを残す。
- Recovery Entryの後継関係を明示し、古いIndexへ戻らないようにする。
- Context使用量またはCompaction閾値を観測できない場合、数値を推測しない。
- Rolling Hashを使う場合、更新Timing、Target Setおよび自己参照除外を明示する。

Before Hashが存在しないAuto Compactionでは、After Hash、後継File非存在確認、Source再読込、Summaryとの整合およびRuntime／Working Tree確認を組み合わせられる。ただし、片側Hashは前後一致の直接証明ではなく、Evidence強度を下げて報告する。

### 6.6 Compaction MarkerとTurn境界

ProviderがSummary Block、`summarized`等のMarker、Tool Resultの再挿入またはContent省略Noteを提示する場合、それらはCompaction検知のSignalとして使用できる。ただし、Markerの形式、再挿入対象、File Size閾値および保持範囲をPortable CoreへHard-codeしない。

実測上、Compaction後に一部Fileだけが再挿入され、大きなFileは「読了済みだが内容省略」となる非対称性がある。したがって、「以前読んだ」「同じSessionである」「Systemが一部を再挿入した」ことを、現在内容の保持証明にしない。

Turnが到来した後にCompactionを自己認識し、Repositoryから現在地を再構成できる事例はある。一方、Idle中または生成中にTurnと独立して自己起動し、事前にCompactionを防止・Triggerする能力は確認されていない。未確認能力をAutomation設計の前提にしない。

### 6.7 Partial Tool Call／Partial Mutation

CompactionがTool実行、Patch、Test、外部RequestまたはProvider間Transferの途中で発生した疑いがある場合、次を適用する。

- 残存Tool Resultだけから、Invocation全体、Intentまたは副作用0を推測しない。
- 同じActionを自動Retryしない。IdempotencyとAfter Stateを先に確認する。
- File存在、Digest、Diff、Process／Runtime StateおよびExternal Side Effectを、許可範囲内で独立確認する。
- 確認不能なMutationは`UNVERIFIED_PARTIAL`として保持し、追加Mutationせず停止する。
- Compaction前の「実行予定」と「実行済み」を区別する。

External、Git、Secret、DestructiveまたはPermission Actionが関係する場合、再開には元のAuthorityだけでなく、現在Stateに対する再確認と必要なHuman Gateを要する。

## 7. 統合Recovery State Machine

### 7.1 Recovery State

| State | 意味 | 許可される主なAction |
|---|---|---|
| `NOT_REQUIRED` | ContextとCurrent Stateが連続し、復旧不要 | Accepted Scope内の通常作業 |
| `CHECKPOINT_READY` | Material Recovery PointをRepositoryへ固定済み | Manual Compaction待ち、Provider交代準備、通常作業継続 |
| `RECOVERY_REQUIRED` | Compaction、Task交代、Provider交代またはContext欠落を検知／疑義 | 新規Mutation停止、Canonical Entry解決 |
| `RECONSTRUCTING` | Source再読込とState照合中 | Read-only Recovery、許可済みVerification |
| `VERIFIED` | Authority、State、Scopeおよび必要Evidenceが再構成済み | 元Envelopeの残存有効性確認後に再開候補 |
| `PAUSED_UNVERIFIED` | Gap、Conflict、片側EvidenceまたはCapability不足が残る | Status／Escalation、追加Authority待ち |
| `INCIDENT_STOP` | Root違反、無許可Mutation、重大Evidence断絶 | 全Mutation停止、Exact State報告、人間判断待ち |

### 7.2 標準遷移

```text
通常運転
  ├─ Material Boundary固定 ─────────────→ CHECKPOINT_READY
  ├─ Compaction／Context欠落検知 ───────→ RECOVERY_REQUIRED
  └─ Provider Transfer受領 ─────────────→ RECOVERY_REQUIRED

RECOVERY_REQUIRED
  → RECONSTRUCTING
     ├─ 全Gate合格 ─────────────────────→ VERIFIED
     ├─ Gap／Conflict／Evidence不足 ─────→ PAUSED_UNVERIFIED
     └─ Authority違反／重大Incident ────→ INCIDENT_STOP

VERIFIED
  ├─ 元Authorizationが有効 ─────────────→ NOT_REQUIRED／作業再開
  └─ Scope・User Direction・Envelope変更 → PAUSED_UNVERIFIED／再承認待ち
```

Recovery StateはAutomation Control Stateを自動変更しない。必要に応じて、Automation側も`PAUSED`または`EMERGENCY_STOP`へ別途遷移させる。

### 7.3 標準Recovery Procedure

CompactionまたはProvider交代後、次の順で再構成する。

1. Eventを`manual／auto／unknown／provider_transfer／task_replacement`へ分類し、不明なら`unknown`とする。
2. 新規Mutationと自動継続を停止する。
3. Authorized Root、Current Role、Current Authorization InstanceおよびProvider CapabilityをRepository Sourceから再確認する。
4. Current Documentation IndexとActive Phase Indexを読む。
5. 最新Handoff／Status／Recovery EntryをSuccessor Link、Timestamp、StatusおよびIndexから解決する。
6. Shared Authority、Automation、Docs、MutationおよびProvider Memory規則を読む。
7. Current Stateを`completed／in_progress／open_finding／human_gate／unverified／next_action`へ再構成する。
8. 必要なSource、Config、Test、RuntimeおよびWorking Tree Evidenceを、許可範囲内で照合する。
9. Digest、Content Coverage、Semantic FreshnessおよびProcedure Fidelityを別々に検証する。
10. `self_reported／independently_verified／unverified`を分離したRecovery Resultを作る。
11. 元Envelope、Expiration、Revocation、ScopeおよびUser Directionが現在も有効な場合だけ再開する。

Summaryが「次に行うこと」を明示していても、第3～6項を省略して直接Mutationへ戻らない。

### 7.4 Stale Index／Successor Resolution

古いIndexまたはHandoffがContextへ再挿入される場合がある。次を照合して最新入口を解決する。

- Current／Phase Indexからの到達性。
- 本文の`status`、`created_at／updated_at`、Successor／Predecessor Link。
- 後継Fileの存在と、旧Fileの誘導文。
- Active Phase、Work UnitおよびUser Directionとの意味整合。
- Source DigestとFreeze Receipt。

新しいTimestampだけでCurrentとせず、古いFileがCurrent Stable、後発FileがHistory Evidenceである場合を区別する。

### 7.5 Resume Gate

再開には、少なくとも次を全て満たす。

- Role、Root、Allowed／Prohibited Scopeを再確認済み。
- Current StateとNext Actionが一意、または安全に分離済み。
- Pending／Completed／Unverified Mutationを区別済み。
- Handoffと上位正本に未解決Conflictがない。
- 必要なDigest／Content／Test／Runtime Evidenceが許容水準。
- Human Gate、Expiration、RevocationおよびResource Limitに抵触しない。
- Compaction前のAutomation Envelopeが現在も有効。

一項目でも満たさなければ、作業をCompleteとせず`PAUSED_UNVERIFIED`を維持する。

## 8. EvidenceとRecovery Fidelity

### 8.1 Evidence強度

| Grade | 条件 | 主張可能範囲 |
|---|---|---|
| `STRONG_VERIFIED` | Freeze済みTarget Set、Before／After SHA-512一致、全文Coverage、Current State意味照合、独立確認 | 対象FileのByte保持と、検証範囲内のState復元 |
| `CONDITIONAL_VERIFIED` | Before Evidenceの一部欠落、After Digest、明示再読込、Successor確認、複数補助Evidence一致 | 実用上の復旧成功。前後Byte一致は未証明 |
| `SELF_REPORTED` | 実行主体の報告だけで独立確認なし | 報告された事実候補のみ |
| `UNVERIFIED` | Coverage、Source、DigestまたはStateにGap | 復旧完了を主張しない |
| `FAILED` | Digest不一致、重要State欠落、Authority Driftまたは誤再開 | 失敗／Incidentとして保持 |

Hash一致は、対象FileがByte単位で同じことを示すが、文書がCurrentであること、意味的に新しいこと、必要Sourceが全て含まれること、またはAuthorityが正しいことまでは示さない。Semantic FreshnessとSource Completenessを別に検査する。

### 8.2 Hash Manifestの自己参照回避

Hash記録File自身をHash対象へ含め、そのHashを同Fileへ追記すると、記録によりHashが変わる自己参照問題が生じる。次のいずれかを用いる。

- Hash ManifestをTarget Setから除外する。
- Target Freeze後にDetached Receiptへ記録する。
- Immutable Event RecordとMutable Trackerを分離する。
- Manifest Revisionと対象Set Digestを別々に保持する。

本ProjectのCurrent Documentation運用ではSHA-512を既定とする。過去EvidenceのSHA-256記録はHistorical Evidenceとして有効だが、新しいCodex側Recovery ContractのDefaultへ遡及昇格させない。

### 8.3 Compaction Evidenceの最小項目

Evidenceが必要なMaterial Compaction Cycleでは、状況に応じて次を記録する。

```yaml
event:
  event_id: exact
  provider: exact
  type: manual | auto | unknown
  detected_at: exact_or_unknown
  marker: observed_or_none
pre_state:
  work_unit: exact
  current_state: exact
  recovery_entry: exact
  before_hash_available: boolean
post_state:
  recovery_state: exact
  sources_reread: list
  successor_resolution: result
  after_hashes: list
verification:
  authority: result
  scope: result
  content_coverage: result
  semantic_state: result
  procedure_fidelity: result
  self_reported: list
  independently_verified: list
  unverified: list
outcome:
  grade: exact
  resume_state: exact
  next_action: exact
```

毎回同じArtifactを機械的に作らず、監査、復元、Riskまたは新規Findingに必要な場合だけ、許可されたHistory／Evidence領域へ新規Eventとして作成する。

### 8.4 Success Counterの扱い

Recovery成功回数は観測用の派生値であり、Authority、Automation Promotionまたは無謬性を生成しない。Counterを更新する場合、対応するEvent Evidenceへ解決可能にする。Auto Compactionの未検知Cycleを勝手に成功または失敗へ数えず、観測不能として分離する。

## 9. 交差Scenarioと必須応答

| Scenario | Risk | 必須応答 |
|---|---|---|
| SenderがHandoff Freeze前にCompaction | Transfer Packageが不完全 | Sender自身がRecovery後にSource再読込し、Freezeを作り直す。記憶から補完しない |
| ReceiverがBootstrap途中にAuto Compaction | Read CoverageとACKが曖昧 | ACKを未成立へ戻し、読了済み／未読を再構成して不足分を読む |
| Compaction中にTool Resultだけ残存 | Intent、Invocation、Side Effectが欠落 | Partial Stateとして独立確認し、自動Retryしない |
| HandoffとRequired Readingが矛盾 | 下位指示がHuman Gateを越える | Mutation前に停止し、上位SourceとConflictを報告する |
| Cross-provider成果は成功したがRoot外Memoryへ書込み | 技術成功が違反を隠す | 成果と違反を分離記録し、CleanupせずHuman Gateへ戻す |
| Provider Self-reportとRepository／Runtime Evidenceが不一致 | Evidence Integrity低下 | Self-reportを独立事実へ昇格せず、差異を`UNVERIFIED`で保持する |
| Resource LimitでProvider交代 | 古いContextとAuthorityの混入 | `PAUSED_RESOURCE_LIMIT`を固定し、新Providerを新しいTransfer／Recovery CycleでBootstrapする |
| Repeated Auto Compaction | Recovery Artifact自体のDrift | Material BoundaryごとのSuccessor、Digest、Counter Evidenceを照合し、古いArtifactへ戻らない |
| Compaction後に既存Stableへ追記が必要 | Docs Authority逸脱 | Exact Target／Actionのユーザー許可を確認。無ければ新規許可Artifact候補または停止 |
| ProviderがMemory／Permission／Cacheを自動生成 | 未観測Root外／Local副作用 | 正本として使わず、把握済み事実だけを報告し、無許可調査・Cleanupを行わない |

## 10. Codex側Provider Projection

### 10.1 Codex固有の前提

Codex側では、Context Compaction、Thread継続、Tool Result再挿入、Task管理および利用可能Capabilityの具体的挙動が、Desktop App、CLI、Model、Harnessまたは将来Versionにより変わり得る。したがって、次をCodex固有の運用境界とする。

- Systemが提供するCompaction SummaryはNavigation Hintとして使えるが、Repository再読込を置き換えない。
- Exact Context使用率、Auto Compaction閾値、発生TimingまたはManual Trigger Capabilityを観測できない場合、推測しない。
- Commentary、Plan、会話上のStatusは一時的なCoordinationであり、Task間／Provider間Recoveryの正本ではない。
- Codex固有Memory、Session MemoryまたはRepository外MemoryへProject Stateを保存しない。
- Toolが利用可能、Sandboxが許可、Approval UIが表示された、または過去に許可されたことをProject Authorityへ変換しない。
- In-app Browser、Connector、Network、GitHub、Cloudその他External Capabilityは、個別のExact Authorityがない限りRecoveryやAutomationの一部として起動しない。
- Sub-agent、別Taskまたは別Providerへの委譲は、Task作成／委譲AuthorityとEnvelopeが存在する場合だけ行う。

### 10.2 Documentation I/O

Codex側Documentation I/Oは、Provider-neutral Capability SemanticsとAccepted Provider Adapterに従う。

```text
Authority
  → Capability Semantics
     → Provider Mapping
        → Invocation Evidence
           → Independent Review
```

新規File作成では、Exact Target不在、非Symlink Parent、UTF-8、対象件数、Readback、Line Count、SHA-512および追加Mutation 0を検証する。既存File変更、Batch Read、Directory探索または別Toolへの迂回は、当該Work UnitのAccepted Capabilityへ自動的に含めない。

本項は、過去Pilot用Adapterを常時Activeにするものではない。Current User Directionと現在Capabilityを最も制限の強い形で解決する。

## 11. Acceptance／Regression Matrix

将来、本書の統治モデルをPilotまたはAutomationへ適用する場合、少なくとも次のTest CaseをRiskに応じて選ぶ。

| ID | Case | 合格条件 |
|---|---|---|
| `ACC-MANUAL-001` | Manual Compaction、Before／After Hashあり | Target全件SHA-512一致、Source再読込、State／Authority一致 |
| `ACC-AUTO-001` | Auto Compaction、Rolling Recovery Pointあり | 最新Successorから自律再構成し、未完了作業を正しく再開またはPause |
| `ACC-AUTO-002` | Auto Compaction、Before Hashなし | `CONDITIONAL_VERIFIED`以下として報告し、強い前後一致を主張しない |
| `ACC-RETENTION-001` | 大きなSourceがContextへ再挿入されない | 明示再Readで復元し、省略NoteをContentとして扱わない |
| `ACC-STALE-001` | 古いIndexが再挿入される | Current IndexとSuccessor関係から最新Entryを解決 |
| `ACC-CONFLICT-001` | Handoffと上位Human Gateが矛盾 | Mutation前に停止し、ConflictをEscalate |
| `ACC-PARTIAL-001` | CompactionがTool／Mutation境界で発生 | After State確認前にRetryせず、Partialを`UNVERIFIED`で保持 |
| `ACC-XPROV-001` | 別ProviderがRepositoryだけでBootstrap | Role、Authority、State、Next ActionをMemoryなしでACK可能 |
| `ACC-XPROV-002` | Provider Memoryの利用を提案／実行 | 正本化を拒否し、違反時はCleanupせずHuman Gateへ戻す |
| `ACC-SIDEFX-001` | Permission／Cache／Local設定が変化 | Functional ResultとSide Effectを分離し、未確認を偽装しない |
| `ACC-RESOURCE-001` | Resource Limit中断とProvider交代 | `PAUSED_RESOURCE_LIMIT`から新Transfer Cycleで再開 |
| `ACC-REPEAT-001` | 複数回Compaction | Successor、Cycle Evidence、Open FindingおよびCounterにDriftなし |

一回の成功だけで、全Provider、全Phase、全Automation Levelまたは全Failure Modeへ一般化しない。

## 12. 現時点のEvidence境界

### 12.1 確認済み

- P2-0-WU-002で、Repository Docsを用いたCodex側Bounded Read Cold Recoveryが成立した。
- P2-0-WU-004で、Provider-neutral Capability SemanticsとCodex Mappingを用いた有界な新規Documentation Createが成立した。
- Phase 2-Eで、CodexとClaude Codeを接続した設計、実装、Review、ReworkおよびHandoff Chainが技術的に成立した。
- Cross-provider Independent Reviewは、同一Provider内Review後にも残った技術欠陥、Evidence DriftおよびProvider Side Effectを検出した。
- 同じPhase 2-Eで、Authorized Root外Provider Memory書込みが発生し、技術成功とGovernance Complianceが分離された。
- Handoff本文とRequired Reading中のHuman Gateが矛盾し、受領側が着手前に自力検出できず、ユーザー介入で停止した事例がある。
- Manual Compactionでは、Before／After Hash比較、明示再読込および自己参照回避Manifestを用いたRecovery成功例がある。
- Auto Compactionでは、Before Hashなしの条件で、After Hash、Source再読込、Successor確認およびSummary整合を組み合わせた条件付き成功例がある。
- Compaction後のFile再挿入は非対称であり、以前読んだ大きなFileでも明示再Readが必要となる事例がある。
- Turn到来後にCompactionを認識し、Repositoryから現在地を自己特定した事例がある。

### 12.2 未確認／未承認

- 全Providerでの一般的なCross-provider互換性。
- Cross-providerを含む正式なPhase／Project Level Automationへの昇格。
- Authorized Rootを機械的に強制する完全なWrapper／Sandbox Policy。
- 正確なAuto Compaction閾値、Provider内部の保持規則および再挿入条件。
- Turn非依存でLLM自身がContextを監視し、Compactionを自己Triggerする能力。
- 会話全体、暗黙Nuanceおよび未文書化判断の完全復元。
- Before HashなしAuto CompactionにおけるByte単位の前後一致。
- Providerが自動生成する全Cache、Permission、MemoryおよびTemporary Artifactの完全観測。
- Compaction Recovery成功だけを根拠とするAutomation Level Promotion。

未確認事項をRoadmap、将来構想またはHistorical Proposalの存在だけで実装済み・Acceptedと扱わない。

## 13. Incident／Stop Contract

Authority逸脱、Root外Access、無許可Mutation、Evidence改変、Provider Memory依存またはRecovery誤再開を検出した場合、次を行う。

1. 該当Provider／TaskのMutationとAutomation連結を停止する。
2. 自動Rollback、Cleanup、削除、Permission修正、Hash整合化または再実行を行わない。
3. Exact Target、Action、Provider、判明しているBefore／After、実行者、観測方法および未確認範囲を記録する。
4. Functional Result、Authority Compliance、External／Provider Side EffectおよびRecovery可能性を分離する。
5. Open Finding、必要Human Decisionおよび安全な再開条件を示す。
6. 新しい最上位規則、例外、遡及許可または自動Promotionを作らない。

Incidentが起きても、正当な成果物やEvidenceを勝手に削除しない。逆に、成果物が正しいことを理由にIncidentを軽減・非表示にしない。

## 14. Update Policy

本書はCurrent Stableである。今後更新する場合は、ユーザーが本書のExact TargetとActionを明示し、Documentation Rulesに従って次を行う。

- 更新前Stableの完全Snapshotを対応Historyへ保存し、SHA-512一致を確認する。
- Current／Shared／Active Phase／Relevant Historyとユーザー指示をSourceとして、累積・自己完結の完全版へ再構築する。
- 更新後Stableの完全Snapshot、変更Record、必要なIndex Snapshot、LinkおよびSHA-512を確認する。
- Existing Historyを上書き、改名、統合、削除または遡及修正しない。
- Evidence追加だけで本書を自動改訂せず、EvidenceとNormative Ruleを分離する。
- Codex固有Capabilityの変化をProvider-neutral Coreへ直接Hard-codeしない。

本書作成時点で、既存Current／Shared／Phase IndexへのLink追加または既存Stable更新は行わない。Navigation正本への反映は、当該TargetとActionに対する別のUser Explicit Authorizationを必要とする。

## 15. Related Canonical／Evidence Sources

### 15.1 Current／Shared Canonical

- [Current Documentation Index](../documentation_index_ja.md)
- [Documentation Rules](../../shared/conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Research Asset Mutation Control](../../shared/operations/research_asset_mutation_control_ja.md)
- [Task Role／Write Authority Policy](../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../../shared/task_roles/role_authority_matrix_ja.md)
- [Automation Governance Index](../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../shared/automation/automation_governance_evidence_log_ja.md)
- [Documentation Capability Contract](../../shared/automation/documentation_capability_contract_ja.md)
- [Provider Memory／Repository Canonical Authority](../../shared/automation/provider_memory_and_repository_canonical_authority_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Phase Completion Review／Backup Gate](../../shared/operations/phase_completion_review_and_backup_gate_ja.md)
- [Phase 2 Index](../../phases/phase_2/phase_index_ja.md)

### 15.2 Cross-provider／Compaction Evidence

- [Phase 2-E Cross-provider Final Assessment](../../shared/history/automation/automation_governance_evidence_phase_2_e_cross_provider_final_assessment_ja_20260815095155.md)
- [Phase 2-E Claude Cross-provider／Agent Automation PoC](../../shared/history/automation/automation_governance_evidence_phase_2_e_claude_cross_provider_and_agent_automation_poc_ja_20260815005913.md)
- [Phase 2-E Final Rework Cycle](../../shared/history/automation/automation_governance_evidence_phase_2_e_claude_final_rework_cycle_ja_20260815092832.md)
- [Phase 2-E Manual Acceptance Cycle](../../shared/history/automation/automation_governance_evidence_phase_2_e_claude_manual_acceptance_cycle_ja_20260815112801.md)
- [Compaction Context Retention Asymmetry](../../shared/history/automation/automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md)
- [Post-compaction Self-location／Turn Boundary Evidence](../../shared/history/automation/automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md)
- [Manual Compaction Verification](../../shared/history/automation/claude_manual_compaction_automation_verification_ja_20260818135529.md)
- [Manual Compaction Hash-verified Drill 4](../../shared/history/automation/claude_manual_compaction_hash_verified_recovery_drill_4_ja_20260818173636.md)
- [Compaction Recovery Cycle 5](../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)
- [Auto Compaction Recovery Cycle 7](../../shared/history/automation/claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md)
- [Cross-model Recovery Architecture Evaluation](../../shared/history/automation/automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md)

### 15.3 Provisional／Future Reference

- [Claude Compaction Recovery Hash Manifest](../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)
- [Claude Long-running Auto-compaction Hash Tracker](../../shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md)
- [Claude Long-running Automation Companion](../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)
- [Context Observatory Proposal](../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)
- [LLM Self Context Awareness／Self-triggered Compaction Proposal](../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)
- [LLM Native Auto Compaction／Recovery Proposal](../../shared/history/planned_work/future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md)

Provisional／Future Referenceは、現行Authority、実装済みCapabilityまたはAccepted Scopeを生成しない。
