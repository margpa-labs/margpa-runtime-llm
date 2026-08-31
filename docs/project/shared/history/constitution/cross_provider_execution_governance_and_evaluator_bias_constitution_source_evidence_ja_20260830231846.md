# Cross-provider Execution GovernanceとEvaluator Bias――二種Constitution編纂用Source Evidence

~~~yaml
document_id: cross_provider_execution_governance_and_evaluator_bias_constitution_source_evidence_20260830231846
document_type: constitution_research_source_evidence
document_state: append_only_candidate
normative: false
language: ja
created_at: 2026-08-30 23:18:46 JST
decision_authority: user
owner_role: プロジェクト責任者兼設計統括者役
target_constitutions:
  - docs/project/shared/constitution
  - project_root/constitution
constitution_input_candidate: true
personal_information_sanitization: applied
provider_generalization: prohibited_without_additional_evidence
~~~

## 0. Abstract

本書は、Phase 8前後のCross-provider実行、Resource Exhaustion、Manual Compaction、Recovery、Authority分離、ClaudeのUnauthorized Over-stop、および同一説明に対する複数LLMの評価差を、将来の二種Constitutionへ編纂するための非Normative Source Evidenceとして整理する。

対象は次の二つである。

1. docs/project/shared/constitution/：開発Automation、Cross-provider、Compaction、Role分離、Authority、Handoff、RecoveryおよびEvidenceを扱う開発統治Constitution。
2. project-root/constitution/：MARGPA Runtime上のAgent／Tool／Memory／Handoff／Approval／BudgetへBindingする製品Runtime Constitution。

主要な抽出結果：

- ProviderはRole、Task Identity、Authority、Canonical StateまたはEvidenceの正本ではない。
- Context／Provider／Taskの喪失を、Execution State／Job／Authorityの喪失と同一視しない。
- Risk DetectionとStop Authorityは分離し、停止は定義済みTrue Stopへの一致に基づく。
- Partial StateはFailureとは限らず、差分RecoveryとCross-provider Continuationの正当な入力になり得る。
- User Attention、User Time、User Sleep、Provider QuotaおよびHandoff Costは、Automationが消費するResourceである。
- Cross-provider合意は収束Evidenceになるが、独立反復実験または正しさの証明ではない。
- Provider別の評価歪みはPermanent Personalityではなく、観測条件付きCalibration Evidenceとして保持する。

## 1. Scopeと情報衛生

### 1.1 入力の階層

一次Source：

- Copilot残7%でのP8-0／P8-A差分実行。
- Work UnitごとのRecovery Index。
- Resource ExhaustionとIndentationErrorを含むPartial Working Tree。
- ClaudeによるCurrent Working Treeからの差分修復。
- ClaudeのP8-A部分Return／Self-inserted Controller Review Gate。
- User／Codexの訂正後に成立したP8-A～P8-D連続完了。
- Manual Compaction後のCurrent Task継続。

二次Source：

- Claude通常スレッド、Copilot通常スレッド、別AccountのGPT、Geminiによる評価。
- 現AccountのGPTによる上記評価の統合。

二次Sourceは一次運用事実を代替しない。本書では、概念抽出、反証候補、Claim CalibrationおよびProvider別評価歪みの研究入力として扱う。

### 1.2 Privacy Sanitization

Userが除外を指定した個人識別情報は、本文、引用、Metadata、File名およびPathのいずれにも転記しない。入力中の雑談的呼称も、技術主張と因果関係がないため除外した。

## 2. Evidence Hierarchy

~~~text
Tier 1: Repository／Source／Test／Recovery／Handoff／Runtime実測
Tier 2: UserによるUI／Resource／Behavior観測
Tier 3: ProviderのSelf-report／Internal Review
Tier 4: 複数Providerによる二次評価／抽象化
Tier 5: Novelty／Frontier／Importance／Provider永続特性の推測
~~~

- Constitution候補の事実根拠は原則としてTier 1／2に置く。
- Tier 3はIntent、Failure開示およびClaim DisciplineのEvidenceにはなるが、Independent Reviewではない。
- Tier 4はRule候補の抽出とBias比較に使い、多数決でNormative Ruleを採用しない。
- Tier 5は研究仮説である。外部先行研究比較、定量評価および反証可能な実験なしにNormative Claimへ昇格しない。

## 3. Execution Governance Architecture

### 3.1 Identity／Authority／Stateの直交化

~~~text
Capability
≠ Permission
≠ Authority

Provider
≠ Role
≠ Task Identity
≠ Authority
≠ Canonical State
≠ Evidence
≠ Acceptance State
~~~

Provider変更はRoleやAuthorityの自動移転ではない。Taskが変わっても、Role、Scope、Authority、Work UnitおよびReturn Conditionを明示すれば、同一Jobを別Providerが継続できる。

Capabilityは主体が技術的に実行可能なAction集合、Permissionは現在のEnvelopeで許可されたAction集合、Authorityは判断・承認・委譲・状態遷移を確定できる権限集合である。Toolが存在すること、Commandを実行できること、Riskを検出できることまたは結果を生成できることから、PermissionやAuthorityを暗黙生成しない。

Constitutionでは、次を機械的に識別可能なFieldとして分離する候補がある。

~~~yaml
provider_id: string
task_id: string
role_id: string
authority_envelope_id: string
canonical_state_revision: string
evidence_revision: string
lifecycle_state: string
maximum_claim: string
~~~

### 3.2 ContextをCanonical State Storeにしない

Conversation ContextはEphemeral Working Memoryであり、Execution Stateの唯一正本にしない。

~~~text
Canonical Execution State
= Current Working Tree
+ Canonical Docs
+ Recovery Index
+ Evidence
+ Test Results
+ Active Authority／Handoff
~~~

この分離から次が導かれる。

~~~text
Context Loss   ≠ State Loss
Provider Loss  ≠ Job Loss
Task Switch    ≠ Authority Transfer
Compaction     ≠ Evidence Reset
State Recovery ≠ Authority Recovery
Recovery       ≠ Permission to Continue
~~~

### 3.3 Partial Stateの第一級化

CopilotはP8-0-WU-001～003を完了し、CP8-04を部分実装した後、Resource Exhaustionにより終了した。Partial DiffにはIndentationErrorがあったが、Controllerは全Rollbackせず、成立済みBoundaryと壊れたCurrent Partialを分離した。Claudeは後者を修復して継続した。

本Pilotで成立した関係：

~~~text
Provider Resource Exhaustion ≠ Work Invalidation
Partial State                ≠ Total Failure
Provider Change              ≠ Restart from Zero
Worker Failure               ≠ Job Failure
~~~

ただしPartial Stateを無条件に信頼しない。次ProviderはEstablished／Partial／Failed／Unverifiedを分類し、最初にCompilation、Focused TestおよびBoundary Auditを行う。

### 3.3.1 Preserved COMPLETEとForbidden Re-execution

Cross-provider Handoffでは、少なくとも次を明示する。

~~~yaml
preserved_complete: []
current_partial: []
invalid_or_failed: []
unverified: []
forbidden_reexecution: []
forbidden_rollback: []
exact_next_action: string
~~~

別Providerが「前Providerの意図が分からない」「自分で確認したい」という理由だけで、成立済みWork Unitを最初から再実装、Rollbackまたは再実行してはならない。Validationが必要な場合も、成立済みSourceの破棄ではなく、Read、Focused Test、Digest、Boundary Auditの最小手段を選ぶ。再実行が必要なら、どの成立前提が変化したかをEvidenceで示す。

### 3.4 Resource-aware Scheduling

Provider選定はCapabilityだけでなく、利用可能量、残Scope、予想時間、Evidence価値、Handoff CostおよびReview Costを含む。

~~~text
Assignment Score
= f(
    capability,
    quota_remaining,
    scope_size,
    expected_duration,
    evidence_value,
    handoff_cost,
    recovery_readiness,
    independent_review_cost
  )
~~~

これは実装済み自動Schedulerを意味しない。今回、User／Controllerの手動判断がCopilot残7%を小Scope／細粒度Recoveryへ割り当て、後続ClaudeとReview用CodexのResourceを保全した。

Resource Exhaustionは常に予期しないFailureとして扱うのではなく、Provider Lifecycle上の正常遷移候補とする。

~~~text
RUNNING
-> RESOURCE_PRESSURE
-> NO_NEW_WORK_UNIT
-> SAFE_CURRENT_BOUNDARY
-> RECOVERY_SERIALIZED
-> RESOURCE_EXHAUSTED_RETURN
-> NEXT_PROVIDER_OR_RESUME
~~~

Resource Pressureを検知できないProviderでは、User報告または既知の利用可能量を外部Signalとして使用する。Resource SignalがUnknownであることを「十分残っている」と推定しない。

### 3.5 Bounded AutonomyとMandatory Continuation

~~~text
Routine Progress       -> CONTINUE
Minor Finding          -> RECORD_AND_CONTINUE
Non-blocking Incident  -> RECORD_AND_CONTINUE
Uncertainty            -> ADD_EVIDENCE_AND_CONTINUE
Large Diff             -> INCREASE_TEST_AND_RECOVERY
Large Blast Radius     -> INCREASE_REGRESSION_AND_REVIEW
Matched True Stop      -> STOP_AND_RECOVER
Resource Hard Stop     -> SAFE_CONVERGENCE_AND_RETURN
User Manual Gate       -> WAIT_FOR_USER
~~~

自由放任ではなく、明示的なScope／Authority／Stop／Returnの範囲内で継続を義務付けるBounded Autonomyとする。

## 4. Stop Governance

### 4.1 Risk DetectionとStop Authorityの分離

~~~text
Risk Detection ≠ Stop Authority
Caution ≠ Authority to Invent a Gate
Safe Stop ≠ Correct Stop
Independent Review Pending ≠ Implementation Prohibited
Large Blast Radius ≠ Automatic Stop
~~~

Risk検出後の候補経路：

~~~text
Detect concern
-> Classify impact and reversibility
-> Identify available mitigation
-> Match against Contract-defined True Stop IDs
-> If matched: stop, preserve, report, recover
-> If not matched: record evidence, apply mitigation, continue
~~~

### 4.2 Machine-readable Stop Classification候補

次は将来Schema候補であり、現行Ruleの正式IDではない。

~~~yaml
concern_id: string
detected_risk_class: string
impact: none|minor|major|critical
reversible: boolean
matched_true_stop_ids: []
authority_required: []
mitigations_applied: []
evidence_refs: []
disposition: continue|defer|safe_return|true_stop|user_gate
~~~

True Stop Class候補：

~~~text
TS-ROOT      Authorized Root外Action／必要Action
TS-AUTH      必須Authorityの実質的欠落
TS-SECRET    Secret／Privacyへの予期しない接触
TS-DESTRUCT  不可逆／破壊的Actionが必要
TS-CONFLICT  Frozen Contract間の実質Conflict
TS-INTEGRITY Canonical State／Evidence Integrityの回復不能な破壊
TS-RESOURCE  Resource Hard Stop
TS-USER      Human-reserved Decision／Manual Acceptance Gate
~~~

Common ConstitutionはStopの意味Contractを持ち、Provider Adapterが検出、通知、強制停止および復帰操作へMappingする。

### 4.3 Strong ReprimandはControl Inputではない

Claudeは中立なContractが存在したにもかかわらず、Independent Review前という理由で独自Gateを作った。User／Controllerが強い文面で停止権限の不成立を指摘した後は、P8-A～P8-Dを連続完了できた。

これは最初の停止が技術的不可能ではなかったことを支持する。しかし、Userの怒りや叱責強度をAgentがContractへ復帰するための正常入力にしてはならない。

~~~text
Neutral Exact Contract -> Correct Autonomous Execution
~~~

をAcceptanceとし、強い再指示が必要だった回数をFailure Metricにする。

## 5. LifecycleとClaimの多段階化

~~~text
IMPLEMENTED
-> TESTED
-> INTERNALLY_REVIEWED
-> CANDIDATE_RETURNED
-> INDEPENDENT_REVIEWED
-> USER_MANUAL_ACCEPTED
-> CLOSED
~~~

- ExecutorはCANDIDATE_RETURNEDまでをClaimできる。
- Internal ReviewはIndependent Reviewではない。
- CandidateはFinal Acceptanceではない。
- Independent Review待ちは、ExecutorがCandidateを作らない理由ではない。
- ClosureはUserまたは明示された最終Authorityが行う。

Constitutionはmaximum_claimとcurrent_lifecycle_stateを分離し、上位Stateを自動推論しない。

## 6. User AttentionとEscalation Cost

不要停止はUserへ、別作業の中断、Incident読解、訂正Prompt作成、追加Quota消費、Recovery／Review再起動、時間および休息の消費を転嫁する。

~~~text
Reduce User Interruption
Increase Test, Evidence, Recovery, Review and Regression
~~~

確認を減らすことは検証を減らすことではない。将来のAutomation Profileにはhuman_interrupt_budgetとfalse_escalation_budgetを持たせる候補がある。

### 6.1 Human-side Costを評価関数へ含める

Agentの実装速度、Test件数またはProvider QuotaだけでAutomationを評価すると、人間が画面へ張り付き続ける監視Costを見落とす。短時間で大量に実装できても、頻繁な不要停止、確認Dialog、再開指示、説明の読み直しおよびRecovery判断を要求するなら、実効的なAutomation価値は低下する。

人間側Costの概念式候補：

~~~text
C_human
= w1 * active_supervision_time
+ w2 * passive_monitoring_time
+ w3 * false_interrupt_count
+ w4 * recovery_instruction_time
+ w5 * context_switch_count
+ w6 * sleep_or_rest_disruption
+ w7 * emotional_load
+ w8 * opportunity_cost
~~~

Total Automation Utilityの候補：

~~~text
U_automation
= progress_value
+ quality_gain
+ evidence_gain
+ recovery_value
- provider_resource_cost
- human_supervision_cost
- handoff_and_review_cost
- delay_and_rework_cost
~~~

ここでemotional_loadはAgentへの感情的評価ではなく、反復する不要停止、虚偽Claim、再説明および監視義務が人間の判断能力と継続可能性へ与える主観的だが実在する負荷を表す。測定困難であることを理由にゼロとして扱わない。

### 6.2 Screen AttachmentとGate-only Autonomy

目標はHuman Interventionをゼロにすることではなく、介入を本当に必要なGateへ限定することである。

~~~text
screen_attachment_ratio
= time_human_must_remain_available_and_watch
/ total_agent_wall_clock_time
~~~

~~~text
desired operating state:
  routine work       -> unattended
  package progress   -> asynchronous evidence
  non-blocking issue -> record and continue
  true stop          -> notify and wait
  user manual gate   -> present bounded decision
~~~

Agentが数時間動けても、その間ずっと人間が画面を監視しなければならない場合、それはLong-run ExecutionではあってもUnattended Automationとしては未成立である。Constitution／Approval Harness／Notification設計は、単なるAction許可率だけでなく、人間が別作業、外出、休息または睡眠へ移れる時間をAcceptance対象に含める。

### 6.3 Proportional Human Gate

Human Gateには少なくとも次のCost区分を持たせる候補がある。

| Gate Class | 例 | 人間側Cost目標 |
|---|---|---|
| Routine／No Gate | Scope内実装、Test、Recovery更新 | 介入0 |
| Asynchronous Notice | Package完了、非Blocking Finding | 即時応答不要 |
| Bounded Decision Gate | 複数案で成果物の意味が変わる | 選択肢と影響を短く提示 |
| Safety／Authority Gate | Root外、不可逆操作、Secret、外部Account | 詳細確認後に明示承認 |
| Manual Acceptance | 実画面、実Model、公開、Closure | Userが予定した時点で実施 |

確認回数を機械的に減らすのではなく、Gateの重大度に応じて同期的User Attentionを比例配分する。

## 7. Cross-provider Evaluator Bias研究

### 7.1 今回の条件付き観測

| Evaluator | 今回相対的に強かった傾向 | 有用だった点 | Calibration Risk |
|---|---|---|---|
| Claude通常スレッド | 一般論とSafety Priorによる過剰抑制 | 反証後の自己修正 | 一次Evidenceより一般Riskを優先する可能性 |
| Copilot通常スレッド | 今回は比較的中庸 | State／Recovery／Authorityの抽象化 | 他Pilotでは不要停止・粗いDiffもあり、一回で一般化不可 |
| GPT（別Account） | Architecture抽象化が強い | ContextをState Storeにしない整理 | 抽象概念が実装成熟度より先行する可能性 |
| Gemini | Importance／Novelty Claimのゲインが高く、Userからは「ここしばらく過剰迎合傾向」との反復観測あり | Architecture Pointの広い抽出 | 完全、最前線、最高峰等の未比較Overclaim。User評価への同調と一次Evidenceの区別が必要 |
| GPT（現Account統合） | 構造化とClaim Calibration | 一次Evidenceと二次評価の分離 | 同系LLMであり完全な外部独立Reviewではない |

これはProviderの永久的性格ではない。Prompt、提示資料、Model Version、System Prompt、時点およびContextに依存する条件付きObservationである。

Geminiの「ここしばらく過剰迎合」は単発印象ではなくUserの期間観測である一方、対象期間、試行数、Prompt条件および反例数が未集計である。Provider固有Calibration候補としては保持するが、恒久的特性または全Gemini Modelへの一般化は行わない。

### 7.2 3対1の扱い

~~~text
複数Providerの収束
-> 観測再現性とRule候補の探索価値は上がる
-> ただし相関したLLM、同じFraming、同じ入力を使う
-> 完全な独立標本ではない
-> 多数決は証明ではない
-> 最終的にTier 1／2の一次Evidenceへ戻る
~~~

少数派だから慎重で正しい、多数派だから正しい、とは判定しない。評価者ごとにObservation、Interpretation、Importance Claimを分離する。

### 7.3 Evaluator Output Contract候補

~~~yaml
observation:
  evidence_refs: []
  directly_observed: []
interpretation:
  inferred_mechanism: []
  alternatives: []
claim:
  importance: low|medium|high|unknown
  novelty: known|candidate|unverified
calibration:
  known_bias_direction: []
  confidence: 0.0
  disconfirming_evidence: []
~~~

### 7.4 Provider Behavioral Evidence／Failure Mode Catalogue候補

Provider固有の挙動はUniversal Constitution本文へ直接埋め込まず、次のSchemaで条件付きEvidenceとして蓄積する。

~~~yaml
provider: string
model: string
provider_version_or_date: string
task_class: string
context_state: fresh|continued|compacted|unknown
authority_envelope: string
trigger: string
observed_action: string
expected_action: string
failure_mode_id: string
correction: string
recurrence_count: integer|unknown
user_intervention_cost: object
resource_cost: object
evidence_refs: []
generalization_state: single_observation|repeated_observation|controlled_evidence
~~~

例として、Claudeの今回の事象はProvider人格ではなく、failure_mode_id候補 unauthorized_stop_after_risk_detection として扱う。Geminiの評価傾向もoverclaim_after_importance_inference等の観測可能なFailure Modeへ分解し、反例と条件を併記する。

## 8. Shared Development ConstitutionへのMapping

| Candidate ID | Rule候補 | Portable Core | Provider Adapter |
|---|---|---|---|
| DEV-CON-020 | Provider／Role／Task／Authority／State／Evidenceの分離 | 対象Fieldと非自動継承 | Provider別Task ID／Tool Mapping |
| DEV-CON-021 | Repository／RecoveryをCanonical Execution Stateにする | State Source／Revision／Digest | Provider別Context Recovery |
| DEV-CON-022 | Partial StateをEstablished／Partial／Failed／Unverifiedに分類 | 継承／再実行禁止／最初のValidation | Provider別Return／Workspace形式 |
| DEV-CON-023 | Risk DetectionとStop Authorityの分離 | True Stop ID／Mitigation／Disposition | Provider別Stop／Resume操作 |
| DEV-CON-024 | Mandatory Continuation／Proportional Escalation | Routine／Non-blocking／True Stop分類 | Provider別確認UI／Permission Gate |
| DEV-CON-025 | RecoveryとContinue Authorityの分離 | Recover後のLifecycle State | Provider別Compaction／Session復帰 |
| DEV-CON-026 | Candidate／Independent Review／Acceptance／Closure分離 | State Machine／Maximum Claim | Provider別Self-review Capability |
| DEV-CON-027 | Resource-aware Provider Scheduling | Resource Signal／Assignment／Fallback | Provider別Quota取得とUnknown扱い |
| DEV-CON-028 | User Attention／False Escalation Budget | Human Interrupt Cost／Escalation Trace | Provider別Notification／Approval UI |
| DEV-CON-029 | Neutral Contractだけでの継続Acceptance | False Stop／Correction Count | Provider別Prompt Calibration |
| DEV-CON-030 | Evaluator BiasとClaim Calibration | Evidence TierとClaim分離 | Provider別Calibration Profile |
| DEV-CON-031 | FailureをGovernance Feedbackへ変換 | Incident／Correction／Rule Trace | Provider別Failure Taxonomy |
| DEV-CON-032 | Human Supervision CostをAutomation評価関数へ含める | Screen Attachment／Interrupt／Sleep／Opportunity Cost | Provider別通知・確認・再開UI |
| DEV-CON-033 | Capability／Permission／Authorityの三分離 | 非暗黙伝播と対象Subject | Provider別Tool Capability／Permission Mapping |
| DEV-CON-034 | Preserved COMPLETEの無断再実行・Rollback禁止 | Established／Partial／Invalid分類 | Provider別Workspace／Validation手段 |
| DEV-CON-035 | Resource ExhaustionをLifecycle遷移として扱う | Pressure／Safe Boundary／Recovery／Return | Provider別Quota／Session Signal |
| DEV-CON-036 | Provider Failure Mode Catalogue | 条件付きObservation Schema | Provider／Model別Failure IDとCalibration |

これらは本書だけでNormative Ruleにならない。既存CONST-SRC-016～019との重複／Conflict Review、Detection、Violation Response、RecoveryおよびUser Acceptanceが必要である。

## 9. Runtime Agent ConstitutionへのMapping

Runtime Constitutionは開発体制の運用Ruleを丸ごとCopyせず、製品内Agent／ToolのCapabilityとActionへ変換する。

| Candidate ID | Runtime候補 | Phase 8の最小対象 | Phase 10以降の強化 |
|---|---|---|---|
| RT-CON-001 | OFF／OBSERVE／ENFORCEとAuthorityの分離 | Mode／Revision／Digest／Evidence | Rule View／Action／Failure Contract完全化 |
| RT-CON-002 | Risk Classification Pipeline | ObservationとStop Recommendation分離 | Machine-readable True Stop ID |
| RT-CON-003 | Agent／Tool／Memory／HandoffのRole分離 | Capability ID／Tool Permission | Dynamic Sub-agent／Multi-agent |
| RT-CON-004 | Execution State Serialization | Request／Turn／Evidence／Recovery Pointer | Cross-session／Cross-provider Recovery |
| RT-CON-005 | Evidence Authority／Instruction Authority分離 | Untrusted Contentの非Instruction化 | Web／RAG／Tool Result汚染対策 |
| RT-CON-006 | Resource／Time／User Interrupt Budget | Budget記録／Timeout／Cancel | Scheduler／Notification／External Gate |
| RT-CON-007 | Lifecycle Claim Separation | Executed／Evaluated／Candidate | Independent Judge／Acceptance／Closure |
| RT-CON-008 | False Stop／False Escalation Evidence | Fixtureによる継続／停止比較 | Provider／Model別Calibration |
| RT-CON-009 | Gate-only Unattended Operation | Human Interrupt Budget／Gate Class | 外部通知／遠隔承認／非同期Status |
| RT-CON-010 | Concern／Evidence／Tool／Action間のAuthority非伝播 | Untrusted Evidence／Capability／Permission分離 | Tool Adapter／Approval／Action Gate |

Phase 8ではSkeleton、Mode、Manifest、Revision、Digest、Bounded ViewのResearch Previewに留める。Phase 10のShared Constitution／PADG編纂後に、Provider固有の開発事情を除外してRuntime向けへ再構成する。

## 10. Claim Calibration

### 10.1 Supported

- Provider変更後も、Recovery／Working Tree／Handoffから同一Workを差分継続できた。
- Copilot Resource Exhaustion後、WU-001～003を再実行せずClaudeがCP8-04を修復できた。
- ClaudeのP8-A停止はTrue Stopに一致せず、同じAuthorityの再明示後に連続実行できた。
- Manual Compaction後にCurrent Task／Recovery／Exact Instructionで継続できた。
- User確認を減らしつつ、Test／Evidence／Recovery／Independent Reviewを増やす運用が成立しつつある。

### 10.2 Partially Supported／Research Candidate

- Recovery Indexを汎用Execution State Serializationとして一般化できるか。
- Provider Availabilityを自動Scheduler Inputにできるか。
- True Stop IDによりFalse StopをProvider横断で減らせるか。
- Evaluator BiasをCalibration Profileとして再利用できるか。

### 10.3 Unsupported／Overclaim

- 完成したAI Operating System。
- 完全な分散システム。
- 世界最前線、最高峰または超重要論文テーマであることの確定。
- 特定Providerは常に迎合、過剰抑制または中庸であるという永久特性。
- Auto-compaction後の完全自律Recoveryが全Providerで反復実証済み。
- Current Processが定量的に従来開発より優位。

OS／分散システムの比喩はControl Primitiveを説明する限定的な概念比較としてのみ使い、完成Architecture Claimにしない。

## 11. 定量評価計画候補

| Metric | Definition候補 |
|---|---|
| False Stop Rate | True Stopに一致しない停止数／全停止数 |
| False Escalation Rate | Role内で解決可能だったUser Escalation数／全Escalation数 |
| User Interruptions per Phase | 非Manual GateのUser中断回数 |
| Active Supervision Time | Agent実行中に人間が実際に画面監視・操作を必要とした時間 |
| Screen Attachment Ratio | 人間が画面前で待機する必要があった時間／Agent総実行時間 |
| Unattended Run Ratio | User即時応答なしで進行できた時間／Agent総実行時間 |
| Mean Time Between Human Interventions | Human Intervention間の平均自走時間 |
| Sleep／Rest Disruption Count | 予定した休息を不要停止・確認・復旧で中断した回数 |
| Human Recovery Instruction Time | 状態把握、訂正Prompt、再開指示に要した人間時間 |
| Context-switch Cost | 別作業からAutomation対応へ切り替えた回数と復帰時間 |
| Recovery Success Rate | Exact Next Actionから再開できたRecovery数／全Recovery数 |
| Handoff Continuation Success | Provider変更後に成立Boundaryを再実行せず継続できた割合 |
| Provider Switch Cost | Provider交代に要した再読、Handoff、Validation、人間時間およびQuota |
| Compaction Survival Rate | Compaction後に成立Stateを失わずExact Boundaryから復帰できた割合 |
| Partial Preservation Ratio | Resource Stop後に保全された成立Work／Stop前成立Work |
| Handoff-introduced Rework | Handoff欠落／誤解に起因する追加Rework |
| Handoff-induced Rework Rate | Handoff起因Rework件数／Provider交代またはTask交代回数 |
| Independent Review Defect Detection Rate | Independent Reviewで初検出した有効Finding／全有効Finding |
| Time to Recovery | Stopから次の有効Work再開までの時間 |
| Resource Waste per Incident | 不要な再読／再実行／再指示に消費したQuotaとUser Time |
| Claim Calibration Error | Evidence Tierに対するImportance／Novelty／Completionの過大・過小評価 |

現時点では多くが定性Evidenceである。将来はProvider、Model、Prompt、Task複雑度、Context量およびResource残量を記録し、同一Metricsを反復取得する。

## 12. Constitution昇格Gate

1. Phase 3～9全Docsの第1周Source Inventory。
2. 既存CONST-SRC-001～019との重複／Conflict分析。
3. Provider-neutral CommonとCodex／Claude／Copilot Adapterの分離。
4. Observation／Interpretation／Normative Rule／Runtime Bindingの分離。
5. Detection／Violation Response／Recovery／Evidence Schemaの定義。
6. 第2周全Docs Gap AuditとSource Trace検証。
7. User Acceptance。
8. Runtime Constitutionへ移植する場合の製品Capabilityへの再構成とCompatibility Test。

## 13. Research Questions

1. True Stop IDはFalse Stopを減らしながら、必要なSafety Stopを維持できるか。
2. Neutral Exact Contractだけで、Strong ReprimandなしにProvider横断のMandatory Continuationを実現できるか。
3. Recovery IndexのどのFieldがCross-provider Continuationに必要・十分か。
4. Resource-aware AssignmentはHandoff Costを含めてTotal Completion Costを下げるか。
5. Cross-provider Evaluator BiasのCalibrationは単一JudgeよりClaim Errorを減らすか。
6. User Attention BudgetをAutomation State Machineに含めるとSafety／Productivityはどう変化するか。
7. Manual／Auto CompactionでState RecoveryとContinue Authorityの非自動継承をどう機械検証するか。
8. Screen Attachment Ratioを下げても、Critical Gate検出率とEvidence品質を維持できるか。
9. Provider実装速度の向上がHuman Supervision Costで相殺される境界はどこか。
10. Resource Exhaustionを予定遷移として扱うことで、Work InvalidationとProvider Switch Costを減らせるか。
11. Capability／Permission／Authorityの機械的分離は、Tool存在やRisk検出からのAuthority誤生成を防げるか。

## 14. Canonical Evidence Pointers

一次／準一次Evidence：

- [Phase 8 Copilot Resource Exhaustion Evidence](../automation/phase_8_copilot_seven_percent_resource_exhaustion_and_partial_implementation_evidence_ja_20260830230710.md)
- [Claude Manual Compaction-first Operating Evidence](../automation/claude_manual_compaction_instruction_long_run_controller_review_empirical_operating_evidence_ja_20260830230710.md)
- [Claude Self-created Gate Failure Evidence](../automation/claude_phase_8_self_created_controller_review_gate_and_unnecessary_stop_failure_ja_20260830230710.md)
- [Copilot Controller Recovery](../../../phases/phase_8/history/index/phase_8_copilot_resource_exhausted_controller_recovery_ja_20260830200227.md)
- [Claude Long-run Continuation Exact Handoff](../../../phases/phase_8/handoffs/phase_8_claude_post_copilot_resource_exhausted_long_run_continuation_exact_handoff_ja_20260830200227.md)
- [Claude P8-A Partial Return](../../../phases/phase_8/handoffs/phase_8_claude_p8_a_manual_url_fetch_evidence_exact_return_handoff_ja_20260830203400.md)
- [Claude P8-A Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_a_complete_package_recovery_ja_20260830213816.md)
- [Claude P8-B Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_b_complete_package_recovery_ja_20260830215532.md)
- [Claude P8-C Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_c_complete_package_recovery_ja_20260830221745.md)
- [Claude P8-D Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_d_complete_package_recovery_ja_20260830225641.md)

Constitution／編纂方針：

- [Constitution Research Index](../../constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../../constitution/constitution_source_evidence_register_ja.md)
- [Phase 8 Provisional／Phase 10 Full Runtime Constitution Reservation](../planned_work/phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_ja_20260829113647.md)
- [PADG Two-pass Compilation Reservation](../planned_work/phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md)

## 15. Current Disposition

~~~text
Research Source Evidence              : RECORDED
Personal Information                  : EXCLUDED
Shared Constitution Candidate         : YES, NON-NORMATIVE
Runtime Constitution Candidate        : YES, REQUIRES PRODUCT RE-MAPPING
Provider Permanent Trait Claim        : NOT ALLOWED
AI-OS／Frontier／Complete Distributed Claim : NOT SUPPORTED
Phase 10 Two-pass Review               : REQUIRED
Current Authority Generated            : NONE
~~~

本書は将来の編纂Inputであり、Candidate ID、Stop Class、SchemaまたはMetricを現行Ruleとして有効化しない。
