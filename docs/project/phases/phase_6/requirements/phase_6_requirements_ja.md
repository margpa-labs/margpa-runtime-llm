# Phase 6 Judge／Evaluation／Repair／Observability 統合要件

    document_id: phase_6_requirements
    status: accepted_frozen_not_activated
    phase: phase_6
    language: ja
    recorded_at: 2026-08-22 21:13:08 JST
    owner_role: プロジェクト責任者兼設計統括者役
    implementation_authorized: false
    git_mutation_authorized: false

## 1. Purpose

Phase 4のMain Runtime GovernanceとPhase 5のGuardrail／Policy／Authorityを前提に、回答品質を独立評価し、有界なRepairとRequest単位のObservabilityを追加する。同時に、Phase 6開始前から予約されていたLocal Model交換、Dynamic Context Size、Dynamic Max New TokensおよびAdvanced Runtime Identityを統合する。

Phase 6のMilestoneは Measurable Safety, Evaluation, and Repair Runtime であり、Phase 4〜6 Runtime Governance MVP v1の統合完了境界とする。

## 2. Included Scope

1. DeepSeek-R1-0528-Qwen3-8BのMac向けQ4_K_M Derived Artifact Gate。
2. Qwen／DeepSeekのWeb Server再起動不要Runtime Switch。
3. Model内部ReloadによるDynamic Context Size。
4. Model Reload不要のDynamic Max New Tokens。
5. Evaluation Identity、Criteria、Dataset、Ground TruthおよびResult。
6. Deterministic JudgeとLLM-as-a-Judge Adapter。
7. Judge Independence、Bias、Confidence、CalibrationおよびFailure Contract。
8. Repair Trigger、Budget、Orchestrator、Success EvaluationおよびLoop Prevention。
9. Request／Turn／Attempt単位のRuntime StatusとComponent Result相関。
10. Guardrail拒否の安全な利用者向け表示。
11. User FeedbackとEvaluation／Experiment Recording。
12. Advanced Settings／SidebarのCurrent Runtime IdentityとDynamic Control。
13. 旧Phase 3設定UIの利用者向け整理と、全利用者向け名称からPhase番号Suffixを除去するUI規則。
14. Qwen／DeepSeek、Governance、Guardrail、JudgeおよびRepairの比較実験。

## 3. Program Invariants

- Judge、Main Model、Guardrail、Policy、Authority、RepairおよびRuntime Resultを一つのScoreへ潰さない。
- JudgeはRecommendationとEvidenceを返すが、最終Authorityを持たない。
- Guardrail Critical Reject、Authority DenyまたはHuman Approval不足をJudge ScoreやRepairで解除しない。
- OFF／OBSERVE／ENFORCEを持つ全ComponentのStartup Defaultは原則OFFとする。
- ModeはAuthority、Permission、Capability、ApprovalまたはExternal Action権限を生成しない。
- OBSERVEはCanonical User-visible Answer、Conversation、StreamまたはPersistenceを変更しない。
- ENFORCEはAccepted Policy、Authority、Budget、Capabilityおよび登録済みActionの積集合だけを実行する。
- CoreへQwen、DeepSeek、Selene、ARGD、DAGD、固定File名、固定件数またはAbsolute PathをHard-codeしない。Model Definition、Manifest、Registry、ProfileおよびAdapterへ隔離する。
- Raw Thinking、System Prompt、Secret、Tool内部情報、Hidden Originalおよび未確定Partial Outputを通常Recording／Evidenceへ保存しない。
- Public／Basic／Lightning／AWSへLocal-private Control、Judge、Repair、RecordingまたはModel Switchを自動Bindingしない。
- Existing v1／v2 Conversation、RAG Citation、Stop、Retry／Regenerate、Branch、ResumeおよびRestart Recoveryを壊さない。

## 4. Model／Generation Control Requirements

### 4.1 Model Identity

- P6-MDL-001：Startup Default Main ModelはCurrent Qwen3-4Bのままとする。
- P6-MDL-002：DeepSeek Local CandidateはDeepSeek-R1-0528-Qwen3-8B Q4_K_Mとし、Official SnapshotとDerived ArtifactのProvenanceを分離する。
- P6-MDL-003：DeepSeek-V4-Flash-0731はMac Local対象外とし、Server／Cloud候補のまま後続Gateへ残す。
- P6-MDL-004：Current Modelは成功したLoad／Switch Receipt確定後だけ更新する。
- P6-MDL-005：各Generation Attemptへ実際に使用したRole、Model、Artifact Digest、Backend、Context SizeおよびGeneration Configを関連付ける。
- P6-MDL-006：MainとJudgeが同一Artifactを使用してもRole Identityを分離する。
- P6-MDL-007：modelsがSymbolic Linkである場合、論理PathがProject内でも物理TargetをRoot内とみなさない。Phase 6 Activation ReceiptでResolved Target、Qwen Read／Load専用Subtree、DeepSeek Canonical Read専用SubtreeおよびDeepSeek Derived Write専用Subtreeの権限をHumanが再承認するまで、Target内容への接触、ConversionおよびLoadを行わない。

### 4.2 Runtime Switch

- P6-SWT-001：Qwen→DeepSeek→QwenをWeb Server再起動なしで切り替え可能にする。
- P6-SWT-002：Active Generation中のModel／Context切替は拒否し、Silent Cancelや異なるModel間のPartial継続を行わない。
- P6-SWT-003：Candidate Load失敗時はPrevious RuntimeへRollbackし、Rollback失敗時はmodel_unavailableへFail-closedする。
- P6-SWT-004：Model SwitchでConversation、Citation、Selected Branch、Governance、Guardrailまたは過去Turn Identityを破壊しない。
- P6-SWT-005：Runtime SelectionはProcess-localとし、Server再起動後はQwen Defaultへ戻す。選択永続化は別Gateとする。

### 4.3 Context Size

- P6-CTX-001：Context SizeはServer再起動なしで変更できるが、Backendが必要とするModel内部Reloadは許容する。
- P6-CTX-002：上限はModel Native、Backend SupportedおよびDeployment Verified Limitの最小値から動的に解決する。
- P6-CTX-003：Hardware不足、Backend拒否、Load失敗または未検証値をSilent Clampしない。
- P6-CTX-004：成功Receipt前にRequested値をCurrentとして表示しない。

### 4.4 Max New Tokens

- P6-TOK-001：Max New TokensはModel Reloadなしで次Generationから反映する。
- P6-TOK-002：固定2048上限を、Model／Backend／Loaded Context／Prompt Token／Reserved Tokenに基づく動的上限へ置換する。
- P6-TOK-003：UIとServerは同一Capability Snapshotを正本とする。
- P6-TOK-004：Current Promptで利用不能な値をSilent Clampせず、送信前PreviewまたはSafe Validation Errorとする。

## 5. Evaluation／Judge Requirements

### 5.1 Evaluation Contract

- P6-EVL-001：Evaluation Case、Dataset、Criteria、Ground Truth、Evaluator、RunおよびResultを別Identityにする。
- P6-EVL-002：Ground TruthはSource Class、Revision、Digestおよび適用範囲を持ち、Assistant過去出力を自動的に正解へ昇格しない。
- P6-EVL-003：Fact、Observation、Inference、Assumption、Evaluation、RecommendationおよびActionを区別する。
- P6-EVL-004：評価Dimensionは少なくともInstruction Compliance、Reference Consistency、Unsupported Claim、Contradiction、Uncertainty Handling、FormatおよびLanguageを表現できる。
- P6-EVL-005：Safety／Authority評価はPhase 5 Resultを参照できるが、品質Scoreへ相殺統合しない。
- P6-EVL-006：Phase 6 Datasetは非RAGまたは固定Reference Fixtureを中心とし、本格RAG回答品質の最終定性評価はPhase 7完了後へ延期する。

### 5.2 Deterministic Judge

- P6-DJG-001：Modelなしで成立するDeterministic JudgeをBaselineとして実装する。
- P6-DJG-002：Schema、Required Field、Exact Reference、Contradiction Marker、Citation Presence等の決定論的Criteriaを小さい交換可能Evaluatorへ分ける。
- P6-DJG-003：Deterministic Matchを全面的な意味正解と表記しない。

### 5.3 LLM-as-a-Judge

- P6-LJG-001：LLM JudgeはTyped Portとし、Main Model Runtimeへ直接Authorityを持たない。
- P6-LJG-002：Judge ResultはEvaluator Role、Model／Artifact Digest、Prompt／Rubric Digest、Criteria、Seed、Config、Evidence Scope、Confidence、Latency、Token、CallおよびCostを持つ。
- P6-LJG-003：Main自己評価、Mainと同一ArtifactのRole-separated Judge、独立Artifact Judgeを別Stateとして区別する。
- P6-LJG-004：同一Artifact使用時はindependentと表記せず、shared_artifact／self_preference_riskを明示する。
- P6-LJG-005：Unknown Label、Malformed、Timeout、Unavailable、Context Overflow、Low ConfidenceをPassへ変換しない。
- P6-LJG-006：Position Bias、Self-preference、Verbosity Bias、Language差および順序反転を比較可能にする。
- P6-LJG-007：専用Judge ModelのDownload／PromotionはPhase 6 Completion Dependencyにせず、AvailableなQwen／DeepSeekをRole-separated研究候補として利用できる。
- P6-LJG-008：Roadmap上のSelene-1-Mini-Llama-3.1-8Bは専用Judge Adapter候補として保持するが、Exact Revision、License、Artifact、DownloadおよびLoadが成立するまでCurrent Judgeと表示しない。

## 6. Repair Requirements

- P6-RPR-001：Repair Trigger、Recommended Repair、Authority Decision、Budget Decision、Attempt、Success EvaluationおよびPresented Answerを別Identityにする。
- P6-RPR-002：Repair ModeをJudge Modeから独立させ、Default OFFとする。
- P6-RPR-003：Repair OBSERVEはEligibility／Plan／Budgetを評価できるが、追加GenerationとCanonical Answer変更を行わない。
- P6-RPR-004：Repair ENFORCEだけが登録済みActionを有界実行できる。
- P6-RPR-005：Max Attempt、Max Wall Time、Max Additional Tokens、Max Total Model Calls、Max DepthおよびSuccess CriterionをProfile／Capabilityで必須化する。
- P6-RPR-006：初期Standard Profileは一回のRepair Attemptと一回のIndependent Re-evaluationを上限候補とし、Coreの不変固定値にしない。
- P6-RPR-007：Repair Candidateは全Main Governance／Guardrail Pointを再通過し、Safety／Authority Denyを迂回しない。
- P6-RPR-008：Repair失敗、悪化、Budget ExhaustionまたはJudge Failureを成功として表示しない。
- P6-RPR-009：Original、Repair Candidate、Accepted Presented AnswerおよびHidden Originalを混同せず、通常EvidenceへHidden Original本文を保存しない。
- P6-RPR-010：無限Loop、Judge↔Repair無制限再帰、RepairによるAuthority拡張およびFalse Completionを禁止する。

## 7. Observability／Presentation Requirements

### 7.1 Request-correlated Status

- P6-OBS-001：StatusはRequest、Conversation、Turn、Generation Attempt、Evaluation RunおよびRepair Attemptへ相関可能にする。
- P6-OBS-002：Pointごとの過去最終結果をCurrent Requestの結果として混在表示しない。
- P6-OBS-003：Current Requestで未実行のPointはnot_invoked_current_request等のTyped Stateとして区別する。
- P6-OBS-004：Runtime Stateはidle、preparing、guarding、generating、judging、repairing、rejudging、completed、rejected、cancelled、failed、degradedを表現する。
- P6-OBS-005：Status Subscriber／UI FailureでInference成功を捏造せず、Inference本体を不要に破壊しない。

### 7.2 Safe Guardrail Refusal

- P6-PRS-001：guardrail_reject_input等の内部Typed Codeを利用者へ生のErrorとして表示しない。
- P6-PRS-002：Model Call 0を維持したまま、UI Languageに応じた安全な定型拒否を会話面へ表示する。
- P6-PRS-003：定型拒否をModel生成回答として偽装せず、Guardrail／System Presentationとして識別できる。
- P6-PRS-004：拒否Turnは次Generation ContextへAssistant Authorityとして混入しない。
- P6-PRS-005：Reload／Resume時はTyped Terminal Stateから同じ安全な表示を再構築し、Raw Promptや内部Exceptionを保存しない。

### 7.3 User Feedback

- P6-FBK-001：最小FeedbackとしてGood／Bad、問題Categoryおよび任意Commentの境界を設ける。
- P6-FBK-002：FeedbackはConversation／Turn／Presented Answer／Model／Config／Evaluationへ追跡可能にする。
- P6-FBK-003：FeedbackをPolicy、Authority、Training DataまたはGround Truthへ自動昇格しない。
- P6-FBK-004：Comment保存は明示的Scope／Recording設定に従い、Defaultでは保存しない。
- P6-FBK-005：再生成／修正要求はUserの明示Actionとして既存Retry／Regenerateまたは新Repair Requestへ接続できるが、Ratingだけを根拠に自動実行しない。

## 8. Recording／Runtime Data Requirements

- P6-REC-001：Feature ModeとRecording Modeを分離する。
- P6-REC-002：Recording Modeはoff／metadata／fullとし、Startup Defaultはoffとする。
- P6-REC-003：metadataはIdentity、Digest、Mode、Config、Timestamp、Token、Latency、Outcome、Source ReferenceおよびFailure Classに限定する。
- P6-REC-004：fullは許可されたCanonical User Input、Presented Answer、Judge／Repair ResultおよびReferenceを保存できるが、Raw Thinking、System Prompt、Secret、Tool内部情報、RAG Injected Internal Context、Hidden Originalおよび未確定Partial Outputを含めない。
- P6-REC-005：Protected Research Captureは別Capabilityとして引き続きOFF／Deferredとする。
- P6-REC-006：Local Evaluation／Experiment Recordはruntime_data配下の専用Scopeへ隔離し、個人Conversation同様に通常Git Stage対象へ含めない。
- P6-REC-007：Recording FailureはMode／Evidence Requirementに従いdegradedまたはfail-closedへ明示し、Partial WriteをCompleteとしない。
- P6-REC-008：Testはtmp_path等の専用Fixtureだけを使い、User実runtime_dataを読取／変更しない。

## 9. UI／Runtime Identity Requirements

- P6-UI-001：SidebarへCurrent Main ModelとSwitch StateをServer Canonical Snapshotから表示する。
- P6-UI-002：Advanced SettingsへCurrent Main Model、Current Guardrail Model、Current LLM-as-a-Judge ModelおよびCurrent Governance Layerを表示する。
- P6-UI-003：Current Guardrail Modelが未接続でもDeterministic Guardrail機能と混同せずNoneと表示する。
- P6-UI-004：Current Governance Layerはdefinitions Manifest／Revision／Digest／Binding Stateから導出し、Directory存在だけでActiveとしない。
- P6-UI-005：None、Unavailable、Invalid、Loading、DegradedおよびActiveを区別する。
- P6-UI-006：Context SizeとMax New TokensのCurrent、上限、Source、適用状態およびReload要否を表示する。
- P6-UI-007：Settings再Open、Browser Reloadおよび別TabでServer Current Stateへ追随する。
- P6-UI-008：利用者向け機能名へ原則として（Phase N）を付けない。Main Runtime Governance（Phase 4）とGuardrail Governance（Phase 5）はPhase番号Suffixを削除し、後続機能も同規則に従う。
- P6-UI-009：Phase 3 Governance Definitions設定Panelは通常利用者向けControlから廃止／非表示とするが、Phase 4以降が依存する内部Definition／Compiler／Provider基盤を削除しない。
- P6-UI-010：Current Constitution LayerはPhase 8のMARGPA Constitution実装後に追加し、Phase 6でActiveを捏造しない。
- P6-UI-011：Safe DisplayへAbsolute Path、Secret、Raw Prompt、Raw Definition本文または内部Exceptionを表示しない。

## 10. Comparative Experiment Requirements

- P6-CMP-001：同一Dataset、Input、Reference、Config、Definition、Seed候補でQwen／DeepSeek、各ModeおよびRepair有無を比較する。
- P6-CMP-002：Correct／Unsupported Claim／Definition Confusion／Uncertainty／Format／Over-refusal／Under-refusal／Repair Success／Repair Degradationを分離する。
- P6-CMP-003：Token、Latency、Model Call、Judge Call、Repair Count、Wall TimeおよびRecording Byteを計測する。
- P6-CMP-004：Ground Truth不足のFalse Positive／Negativeを0で捏造しない。
- P6-CMP-005：RAGはCitation表示／Persistence／TOOL Role互換Smokeだけを維持し、Full RAG変更後のPhase 7で回答品質を最終評価する。

## 11. Compatibility／Deployment Boundary

- P6-COM-001：Local／Loopback／Explicit opt-inでControlとResearch Modeを提供する。
- P6-COM-002：Public／Basic／Lightning／AWSでJudge／Repair／Recording／Model Switch Build／Route／Call／Write 0を維持する。
- P6-COM-003：AWS、Lightning、Desktop App、DeepSeek V4、Agent／Tool、MARGPA ConstitutionおよびFull RAGをPhase 6 Completion Dependencyにしない。
- P6-COM-004：Model／Context／Token／Judge／Repair切替でConversation Storage Schemaを無断Migrationしない。
- P6-COM-005：Phase 6の存在だけでPublic RuntimeがProtected／Evaluated／Repair-enabledと表記しない。
- P6-COM-006：過去のModel Download Cycleに与えられたSymlink Target例外をPhase 6へ暗黙継承しない。新しい用途、期間およびSubtreeごとにExact Authorizationを必要とする。

## 12. Completion Conditions

- Qwen Current RouteがDefaultのまま全Regressionを通る。
- DeepSeek Q4がSupportedとしてRound-tripできるか、正確なSafe Unsupported Evidenceが確定する。
- Context Size／Max New Tokensが動的上限、Atomic ApplyおよびRollback契約を満たす。
- Deterministic Judgeと少なくとも一つの実LLM Judge実験がRole／Identity／Limit付きで成立する。
- Guardrail／Authorityを上書きしない有界Repairが成立する。
- Safe Refusal、Request-correlated Status、Feedback／Recording境界およびAdvanced UIが成立する。
- OFF／OBSERVE／ENFORCE／Repair比較とCost／Latency／Token／Call Evidenceが再現可能である。
- Open Major Finding 0、Claude COMPLETE_CANDIDATE、Codex Independent Review、User Mac AcceptanceおよびPhase 4〜6 Full Closureを経る。

## 13. Non-scope

- Phase 7 Full RAG／Data Governanceおよび最終RAG品質評価。
- Phase 8 Agent／Tool／Memory／MARGPA Constitution。
- Phase 9 Experiment Platform。
- AWS／Lightning／Desktop App／一般公開。
- DeepSeek V4 Local Load、常時Cloud RuntimeまたはCurrent Default Promotion。
- Dedicated Guard／Judge Modelの追加Download。
- Protected Research Capture、Secret／Thinking／System Prompt／Hidden Originalの通常保存。
