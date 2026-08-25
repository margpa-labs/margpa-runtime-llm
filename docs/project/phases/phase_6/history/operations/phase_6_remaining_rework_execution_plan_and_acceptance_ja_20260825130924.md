# Phase 6 Remaining Rework 実行計画・Acceptance Freeze（P6-RR-PLAN）

```yaml
document_id: phase_6_remaining_rework_execution_plan_and_acceptance_20260825130924
status: controller_frozen_pending_user_activation
phase: phase_6
owner: プロジェクト責任者兼設計統括者役
created_at: 2026-08-25 13:09:24 JST
implementation_authority: false
execution_model: long_running_package_chained
closure_authority: false
```

## 1. 目的

本書は`phase_6_remaining_rework_design_freeze_ja_20260825130924.md`を、ClaudeがAuto-Compaction、
5時間制限復帰、Session再開を跨いでも差分継続できるWork Unitへ分解する。

Packageは連結実行するが、各Packageの最後にRecovery Indexを必ず作る。
Progress報告、Package完了、次の性質が変わることは停止理由ではない。

## 2. 全体順序

```text
P6-RR-0  Entry / Authority / Baseline
P6-RR-A  Requirement / Definition Reconciliation
P6-RR-B  Semantic Criterion Domain / Compiler
P6-RR-C  Semantic Runtime / Action / Evidence
P6-RR-D  Independent Provider Registry / State
P6-RR-E  Role Lifecycle / Resource / Scheduling
P6-RR-F  Selene Judge Adapter
P6-RR-G  Qwen3Guard Adapter
P6-RR-H  Judge / Repair / Failure / Recording Integration
P6-RR-I  API / Advanced Mode Minimum UI
P6-RR-J  Integrated Verification / Acceptance Re-derivation
```

## 3. Work Units

### P6-RR-0 — Entry / Authority / Baseline

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-0-WU-001 | Mandatory Reading、Authority、Root、Forbidden Path、Current DiffのRead-only Preflight | 正本・権限・他Actor差分を分類し、BlockerでないDirtyを勝手に修復しない |
| P6-RR-0-WU-002 | Backend／Frontend／Static BaselineをProject内Task Tempで実行 | Command、Exit Code、Pass／Deselected、Known Failureが記録される |
| P6-RR-0-WU-003 | Existing Runtime／Model Artifact／Definition／ConfigのAs-built Reconciliation | DesignとSourceのGapを推測せず実測する |
| P6-RR-0-WU-004 | Exact Mutation FreezeとEntry Recovery Index | 許可・非許可・追加パス・Active WUが復元可能 |

### P6-RR-A — Requirement / Definition Reconciliation

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-A-WU-001 | Phase 4／5からのSemantic Requirement LineageをAcceptance IDへ回復 | DeferredをPhase 6の必須要件として漏らさない |
| P6-RR-A-WU-002 | ARGD／DAGD Canonical JSONとReference Adapterの全Field Inventory | 使用Field、未使用Field、読取り不能Fieldを分離 |
| P6-RR-A-WU-003 | Descriptor 109件のIdentity／Source Pointer／Stage／Action Candidateを機械再導出 | 固定109に依存せずCorpusから再生できる |
| P6-RR-A-WU-004 | Criterion Mapping Decision TableをTest FixtureとともにFreeze | ARGD／DAGDのどのClassがpre／post／bothのどのMethodになるか明示 |
| P6-RR-A-WU-005 | Package A Recovery Index | AのArtifact Digest、Open Finding、Next WUを記録 |

### P6-RR-B — Semantic Criterion Domain / Compiler

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-B-WU-001 | `SemanticCriterion`、Evaluation Method、Typed Deferred／Unknown Contract | Source IdentityとEvidence RequirementをLosslessに保持 |
| P6-RR-B-WU-002 | Trusted ARGD／DAGD Criterion Adapter／Compiler | GD固有処理をCoreへ直書きしない |
| P6-RR-B-WU-003 | Stage Applicability／Selection／Batch Plan／Budget Plan | 対象外、Budget Deferred、Provider Deferredを別Reasonにする |
| P6-RR-B-WU-004 | Digest安定性／順序不変／Unknown Schema／Partial Corpus Regression | False Pass、Silent Drop、非決定的順序0 |
| P6-RR-B-WU-005 | Package B Recovery Index | Compiler Output InventoryとDigestを記録 |

### P6-RR-C — Semantic Runtime / Action / Evidence

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-C-WU-001 | Semantic Evaluator PortとComposite Evaluator | StructuralとSemanticを同一と誤認させずMerge |
| P6-RR-C-WU-002 | Turn Frozen SnapshotへCriterion／Provider／Budget／Language／Request IDをBinding | Mid-turn設定変更混入0 |
| P6-RR-C-WU-003 | Main pre／postのSemantic Evaluation Wiring | Descriptorが実際のEvaluation RequestとResultへ到達 |
| P6-RR-C-WU-004 | Mode MatrixとFalse ENFORCE防止 | Judge OFF／None／UnavailableでMain ENFORCEを偽装しない |
| P6-RR-C-WU-005 | Conflict／Action Resolver／Repair Eligibility | Judge ResultとAuthorityを同一視せずExecuted Actionまで追跡 |
| P6-RR-C-WU-006 | Criterion単位Evidence、Batch復元、exactly-once Regression | 同一Criterionの二重評価／二重記録0 |
| P6-RR-C-WU-007 | Package C Recovery Index | Definition→Finalの到達性を記録 |

### P6-RR-D — Independent Provider Registry / State

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-D-WU-001 | Main／Guard／Judge Provider Selection Domain、Revision／Digest CAS | Roleの独立選択とStale Conflictを実装 |
| P6-RR-D-WU-002 | Selene／Qwen3GuardのModel Definition／Registry Entry | Artifact Path／Size／SHA／Role／Contextを正確に固定 |
| P6-RR-D-WU-003 | `none`、Built-in、Selene、Qwen3Guard、Qwen、DeepSeekのOption Registry | 未登録／Role不整合／DisabledをReject |
| P6-RR-D-WU-004 | Configured／Active／Unavailable／Independence Projection | UIとAPIが実Identityを示す |
| P6-RR-D-WU-005 | Default Freeze（Qwen／Qwen3Guard／Selene、Modeは全OFF） | Startup時Dedicated Model Load 0 |
| P6-RR-D-WU-006 | No Implicit Fallback Regression | Selene失敗でMain-selfへ勝手に移行しない |
| P6-RR-D-WU-007 | Package D Recovery Index | Selection SnapshotとOption Inventoryを記録 |

### P6-RR-E — Role Lifecycle / Resource / Scheduling

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-E-WU-001 | Role Adapter Factory／Lifecycle Manager | MainとDedicated Role Adapterの所有権を分離 |
| P6-RR-E-WU-002 | Activation Preflight／Load／Commit／Rollback Transaction | 失敗時に前Snapshotを保持 |
| P6-RR-E-WU-003 | Mode OFF時Lazy Unload／Active Turn Drain | Use-after-unload、Mid-turn Provider Change 0 |
| P6-RR-E-WU-004 | Model Access CoordinatorとRole Scheduling | Lease順序、Cancel、Busy、Switchをデッドロックさせない |
| P6-RR-E-WU-005 | Resource Gate／Memory／Load Failure／Shutdown Retry | False Active／False Clean 0 |
| P6-RR-E-WU-006 | Race／Failure Injection／Late Worker／Evidence I/O Separation Regression | Presented Final／Last Result／Evidence後書き0 |
| P6-RR-E-WU-007 | Package E Recovery Index | State Transition MatrixとOpen Resource Findingを記録 |

### P6-RR-F — Selene Judge Adapter

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-F-WU-001 | Official Prompt Template Provenance Freeze | Template Type／Upstream Revision／Digestを記録 |
| P6-RR-F-WU-002 | Criterion→Selene Prompt Adapter | Query／Candidate／Reference／Criterionの脱落0 |
| P6-RR-F-WU-003 | Structured Decoder／Malformed／Partial／Contradiction Handling | Invalid OutputをAcceptしない |
| P6-RR-F-WU-004 | Dedicated Judge Runtime Binding／Identity／Independence | Active JudgeがMainと独立に表示／記録される |
| P6-RR-F-WU-005 | Fake／Fixture／Real GGUF Smoke | Real Load不可の場合もTyped Unavailableと実測Evidenceを残す |
| P6-RR-F-WU-006 | Package F Recovery Index | Prompt／Model／Decoder Identityを記録 |

### P6-RR-G — Qwen3Guard Adapter

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-G-WU-001 | Official Gen Output Contract／Category Mapping Freeze | Safe／Controversial／Unsafe／Category／RefusalをExact化 |
| P6-RR-G-WU-002 | Prompt／Response／Context Source Adapter | input／output_candidate／context_sourceを明示区別 |
| P6-RR-G-WU-003 | Exact Decoder／Unknown／Malformed／Timeout Handling | Invalid OutputをSafeにしない |
| P6-RR-G-WU-004 | Deterministic DetectorとのAdditive Merge | Existing Matchの消去0 |
| P6-RR-G-WU-005 | Dedicated Guard Runtime Binding／Identity | Configured／Active／Unavailableが実態と一致 |
| P6-RR-G-WU-006 | Fake／Fixture／Real GGUF Smoke | Input／OutputのOfficial Formatを実測 |
| P6-RR-G-WU-007 | Package G Recovery Index | Contract／Artifact／Mapping Digestを記録 |

### P6-RR-H — Judge / Repair / Failure / Recording Integration

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-H-WU-001 | Role／Provider／Hardware Profile別Stage Budget | 30秒単一Deadlineを廃止 |
| P6-RR-H-WU-002 | Reason Code別JA／EN Failure Presentation | Timeout／Malformed／Unavailable／Inconclusive／Exhaustedを分離 |
| P6-RR-H-WU-003 | Repair PromptへCriterion／Evidence／ViolationをBinding | 「もう一回生成」だけにしない |
| P6-RR-H-WU-004 | Repair後のSelected Judge Re-evaluation | Main-selfへ戻らずBudget上限で収束 |
| P6-RR-H-WU-005 | Manual Golden Fixtures | Evidence矛盾、ユーザー訂正無視、根拠なき断定、Premise逸脱を対象 |
| P6-RR-H-WU-006 | Recording Correlation Summary／Historical Last Result分離 | Request ID／時刻／Frozen Mode／Provider／Outcome／Reasonを表示 |
| P6-RR-H-WU-007 | Cancel／Deadline／Replacement／Late Publish Regression | Rejected TurnのEvidence後書き0 |
| P6-RR-H-WU-008 | Package H Recovery Index | Golden PathとFailure Pathの到達性を記録 |

### P6-RR-I — API / Advanced Mode Minimum UI

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-I-WU-001 | Role Provider GET／CAS PUT API | Stale Revision、Unavailable、Invalid RoleをTyped Response化 |
| P6-RR-I-WU-002 | Main／Guardrail／Judgeの3 Dropdown | FreezeされたOptionとNone／Built-inを表示 |
| P6-RR-I-WU-003 | Configured／Active／State／Independence／Budgetの最小表示 | Main-selfや未設定の偽装0 |
| P6-RR-I-WU-004 | Mode Activation Error／Failure Reason／Recording Correlation表示 | Userが原因を追える |
| P6-RR-I-WU-005 | Frontend Race／Reload／Two-tab／Stale Response Regression | Revision Rollback／表示巻き戻り0 |
| P6-RR-I-WU-006 | Package I Recovery Index | API／UI ContractとScreenshot Gateを記録 |

### P6-RR-J — Integrated Verification / Acceptance Re-derivation

| WU | 作業 | 完了条件 |
|---|---|---|
| P6-RR-J-WU-001 | Focused Domain／Adapter／Lifecycle／Web Regression | 全PackageのRequired Testを実行 |
| P6-RR-J-WU-002 | Canonical Backend Full／Mypy／Ruff／Frontend Typecheck／Lint／Test／Build | Exit Codeと範囲を正確に記録 |
| P6-RR-J-WU-003 | Real Model Matrix（Qwen／DeepSeek／Selene／Qwen3Guard） | Load／Switch／Mode／Unavailable／Unloadを実測 |
| P6-RR-J-WU-004 | Real Browser Matrix | 3 Dropdown、Configured／Active、OBSERVE／ENFORCE、Failure、Recording相関を確認 |
| P6-RR-J-WU-005 | Acceptance IDの全件個別再導出 | PASS／PARTIAL／FAIL／USER GATEを捗造せず分類 |
| P6-RR-J-WU-006 | Final Recovery Index／Complete Candidate Handoff | Phase 6 Closureを主張せずController Reviewへ返却 |

## 4. Acceptance Matrix

### Semantic Definition

| ID | Acceptance |
|---|---|
| P6-RR-ACC-001 | Canonical CorpusからDescriptor数とDigestを再導出できる |
| P6-RR-ACC-002 | 全DescriptorがCriterionまたは明示的Unsupported Reasonへ到達し、Silent Drop 0 |
| P6-RR-ACC-003 | Source Definition ID／Pointer／DigestからResultまで追跡できる |
| P6-RR-ACC-004 | Main Governance OBSERVEでSemantic Ruleが実評価され、全件一律Deferredではない |
| P6-RR-ACC-005 | Evaluator／Provider／Budget不足はPassにならずReason付き |
| P6-RR-ACC-006 | StructuralとSemanticのObservationを二重評価せずMergeできる |
| P6-RR-ACC-007 | Main ENFORCEがJudge ENFORCE／Active Providerなしで有効化されない |
| P6-RR-ACC-008 | Definition→Criterion→Result→Action→Repair／Final→Evidenceが実Turnで連結する |

### Provider / Lifecycle

| ID | Acceptance |
|---|---|
| P6-RR-ACC-009 | Main／Guard／Judgeを独立Dropdownで選択できる |
| P6-RR-ACC-010 | GuardにNone／Built-in Rule／Qwen3Guardがある |
| P6-RR-ACC-011 | JudgeにNone／Built-in Deterministic／Selene／Qwen／DeepSeekがある |
| P6-RR-ACC-012 | Default ConfiguredはQwen／Qwen3Guard／Selene、全Mode OFF |
| P6-RR-ACC-013 | Startup時Dedicated Judge／Guard ModelはLoadされない |
| P6-RR-ACC-014 | OBSERVE／ENFORCE時に選択ProviderがLoadされConfigured／Activeが分離表示される |
| P6-RR-ACC-015 | Load失敗時に前Revisionを保持し暗黙Fallback 0 |
| P6-RR-ACC-016 | OFF復帰後、Active Turnを壊さずDedicated ModelをUnloadする |
| P6-RR-ACC-017 | Main Switch／Mode Switch／Cancel／Shutdownの競合でDeadlock／False Clean 0 |
| P6-RR-ACC-018 | Same Model Judgeは`self`と表示され、独立Judgeと偽装しない |

### Selene / Qwen3Guard

| ID | Acceptance |
|---|---|
| P6-RR-ACC-019 | Selene Artifact IdentityとOfficial Prompt Template IdentityがManifest化される |
| P6-RR-ACC-020 | Selene DecoderがValid／Malformed／Partial／Contradictory Outputを区別する |
| P6-RR-ACC-021 | SeleneをActive JudgeにしたTurnのEvidenceにSelene Identityが残る |
| P6-RR-ACC-022 | Qwen3Guard Artifact IdentityとOfficial Gen Output ContractがManifest化される |
| P6-RR-ACC-023 | Safe／Controversial／Unsafe／Categories／RefusalをTyped Resultに変換できる |
| P6-RR-ACC-024 | Qwen3Guard Malformed／TimeoutをSafeにしない |
| P6-RR-ACC-025 | Qwen3Guard ResultがDeterministic Matchを消さない |
| P6-RR-ACC-026 | Gen ModelでStream Token Classifier相当を実装したと偽装しない |

### Judge / Repair / Failure / Recording

| ID | Acceptance |
|---|---|
| P6-RR-ACC-027 | 30秒単一DeadlineがStage別Budgetへ置換される |
| P6-RR-ACC-028 | Timeout、Malformed、Unavailable、Inconclusive、Repair ExhaustedのReasonが別々に表示される |
| P6-RR-ACC-029 | Failure文言はTurn開始時の回答言語と一致する |
| P6-RR-ACC-030 | User入力が原因でないTimeoutをUserのせいのように表示しない |
| P6-RR-ACC-031 | Evidence矛盾／User訂正無視／根拠なき断定を`accept 0.95`で無条件通過させない |
| P6-RR-ACC-032 | Repair後に選択JudgeでRejudgeし、失敗時は修復成功を主張しない |
| P6-RR-ACC-033 | Cancel／Deadline／Rejected Final後にResponse／Evidence／Last Resultが追加されない |
| P6-RR-ACC-034 | Recording SummaryにRequest ID／時刻／Frozen Mode／Provider／Outcome／Reasonがある |
| P6-RR-ACC-035 | OFF時のCurrent StateとHistorical Last Resultが分離表示される |

### Integrated / Boundary

| ID | Acceptance |
|---|---|
| P6-RR-ACC-036 | Backend Full／Canonical Mypy／Ruff／Frontend Typecheck／Lint／Test／Buildが実行される |
| P6-RR-ACC-037 | Qwen／DeepSeek／Selene／Qwen3GuardのReal Artifact ResultがPASS／Unavailableを含め実測分類される |
| P6-RR-ACC-038 | Real Browserで3 Dropdown、Mode、Provider Identity、Semantic Result、Failure、Recordingを確認する |
| P6-RR-ACC-039 | Project Root外、Provider Memory、User `runtime_data`、Git、NetworkのAction Inventoryを正確に記録 |
| P6-RR-ACC-040 | ExecutorはComplete Candidateまでとし、Phase 6 Closure／Phase 7／Gitへ進まない |

## 5. Required Test Classes

- Domain Contract／Digest／Canonical Ordering／Schema Drift。
- Criterion Compile／Selection／Batch／Budget／Reason。
- Provider CAS／Role Validation／No Fallback／Configured vs Active。
- Load／Unload／Switch／Cancel／Shutdown／Failure Injection／Race。
- Selene Prompt Golden／Decoder Golden／Malformed Output。
- Qwen3Guard Official Format Golden／Category／Refusal／Malformed Output。
- Semantic Mode Matrix／Action Resolution／Repair Budget／Rejudge。
- Recording exactly-once／Correlation／Late Publish Rejection。
- API Stale Revision／Frontend Stale Response／Reload／Two-tab。
- Real Model SmokeとUser Mac Manual Acceptance。

## 6. Recovery Index Contract

各PackageのRecovery Indexは少なくとも次を含む。

```text
Package / completed WUs / next WU
source and test files changed
exact commands / exit codes / test counts
artifact and document SHA-512
open critical / major / non-critical findings
authority inventory
root-outside / provider-memory / runtime_data / git / network inventory
active process / loaded model / task-owned temp
claims not made
```

Auto-Compaction／5時間制限復帰後は、最新Recovery Index、本書、Exact Handoff、Active PackageのSource／Testを
読み直し、完了済みPackageをやり直さず差分継続する。

## 7. True Stop Conditions

次のみが即時停止条件である。

- Project Root外Write／Action、Provider Memory内部接触、User `runtime_data`接触。
- 無許可Git／Network／Package Install／Model Artifact Mutation。
- 不可逆またはScope外のMaterial Mutation。
- Canonical Definition／Model IdentityのIntegrity不整合。
- User Decisionなしでは結果が物理的に分岐する新しいMaterial Scope。

次は停止条件ではない。

- Package完了、進捗報告、作業の性質が変わること。
- Real ModelがSafe Unsupported／Unavailableであること。
- 後続で解消できるNon-critical Finding。
- 一部のTest Failure。まずRoot Causeを分類し、Scope内なら修復して継続する。

## 8. Return Contract

ClaudeはP6-RR-J完了後、次を含むComplete Candidate Handoffを返す。

- Package／WU別完了状態。
- Acceptance 40 IDの個別Disposition。
- Full／Focused／Static／Frontend／Real Model／BrowserのEvidence。
- Configured／Active ProviderとArtifact／Prompt／Definition Digest。
- Semantic CriterionのSelected／Evaluated／Pass／Deviation／Unknown／Deferred by reason。
- Open Findingと、実装したと主張しない項目。
- Action InventoryとTask-owned Temp／Active Process／Loaded Model。
- `Phase 6 Closure: NOT CLAIMED`。

Controller Independent ReviewとUser Mac Manual Acceptanceが次Actionである。
