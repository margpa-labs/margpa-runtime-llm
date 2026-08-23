# Phase 6 Claude Complete Candidate Handoff

```yaml
document_id: phase_6_claude_complete_candidate_handoff
status: complete_candidate
phase: phase_6
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 03:10:00 JST
```

本文書は`phase_6_claude_execution_handoff_ja.md`§10で要求されたComplete Candidate
Handoffである。P6-0からP6-Iまでを自走完了し、本文書作成後は指示どおりPhase 6-J／
Git／Phase 7へは進まず停止する。詳細Evidenceは
`docs/project/phases/phase_6/history/index/`配下の33件のRecovery Entryを一次資料
とし、本文書はその要約・横断的Cross-checkに専念する。

## 1. Phase 6-I Recommendation

```text
Recommendation: Phase 6をCOMPLETE_CANDIDATEとしてPhase 6-J（Codex Independent
  Review／User Mac Manual Acceptance）へ引き渡すことを推奨する。

根拠:
  - Runtime Model Control（6-B）は実Hardware・実UI（Production Composition Root
    経由）の両方でEnd-to-endの実証が完了している。
  - Evaluation／Judge／Repair／Recording（6-C〜6-F）は、Domain／Application／
    Contract層が全てFail-closed原則に従って実装され、Unit＋Adversarial（6-I-WU-001）
    のTestで裏付けられている。
  - しかし、下記§4／§5に列挙するとおり、Evaluation／Judge／Repair／Recordingの
    「実Conversation Generation Flowへの実配線」（Live-path Integration）は、
    Runtime Model Control（6-B）を除き、依然としてDomain／Application層止まりで
    あり、本Session内では意図的に後続へ回した。これは個々のWork Unitで都度
    Docstring／Recovery Entryに明記した既知の設計判断であり、隠蔽された欠陥ではない。
  - この状態でもCOMPLETE_CANDIDATEとして提出することが適切と判断した理由は、
    Frozen Handoff §9のStop Conditionsが「Phase 7／8／10以降を実装しなければ
    Phase 6が成立しない重大衝突」を停止理由としており、Live-path Integration自体は
    Phase 6の成立要件（各Subsystemの独立した正しさ）を損なわず、Codex Independent
    ReviewとUser Mac Acceptanceの場でその要否・優先度を判断すべき性質の作業だからである。
  - 全79件のAcceptance Matrix ID（`phase_6_acceptance_matrix_ja.md`）を本文書内で
    1件ずつ再検証する作業は本Session内では実施していない。既知のGapは§5に列挙した
    Item（P6-ACC-022／029／049／051／053の一部／069の一部／071の一部）に限定される
    と判断しているが、これは各Recovery Entryの記述との突合であり、独立した
    全数Auditではない。Codex Independent ReviewでのFull Auditを推奨する。
```

## 2. Technical／Security Blockers

```text
Technical Blocker（1件）:
  DeepSeek-R1-0528-Qwen3-8BのGGUF変換が、convert_hf_to_gguf.pyのBPE
  Pre-tokenizer未対応（NotImplementedError）によりBlockされている
  （`phase_6_a_wu002_pretokenizer_blocker_ja_20260822223100.md`）。
  既知の2解決策（llama.cpp/Homebrew更新、HF Hub照会）はいずれもDependency
  Acquisition Authority Receiptで明示的に許可されていないNetwork／Homebrew
  操作を要するため、CURRENT_TOOLCHAIN_UNSUPPORTEDとして分類し、User指示
  どおり再エスカレーションしていない（Controller-owned Followupへ回した、§4）。

Security Blocker: 0件識別。
  P6-I-WU-001（`phase_6_i_wu001_adversarial_fault_matrix_ja_20260823030000.md`）
  でSecret非露出を構造的に確認済み（extra="forbid" Contract、Web Error Response
  のSafe Message化、Load Failure ReasonのWeb非露出）。
```

## 3. Governance Incidents

```text
0件。Frozen Handoff §9の7 Stop Conditionsのいずれも、本Session内で実際に
充足したことはない（Trigger 0）。DeepSeek関連のNetwork／Homebrew要求は
Blockerとして正しく分類・回避し、Userへの不要な再確認は行っていない
（Session前半でNetwork例外について不要にUserへ確認した1件のみ、User訂正後は
再発 0）。models Symlink Resolved Target外・Stable直接書き込み・Irreversible
Migration・Canonical Artifact破壊のいずれも発生していない。
```

## 4. Controller-owned Work（後続Batch／Controller側で扱うべき項目）

```text
1. DeepSeek Toolchain Follow-up
   llama.cpp/convert_hf_to_gguf.pyのBPE Pre-tokenizer対応、またはHF Hubから
   対応済みGGUFを取得する経路のいずれかを、新規・明示的なNetwork／Homebrew
   Authorityの発行後に実施する。現時点ではNOT EXECUTED。

2. Evaluation／Judge／Repair／RecordingのLive Generation Path配線
   - Judge: JudgeModeControllerのMode変更は現在Report専用。実際にConversation
     Generationの各Turnに対しLLM-as-a-Judgeを起動する経路が未接続。
   - Repair: execute_repair_plan()は実装・Unit Test済みだが、実Conversation
     Generation Serviceのpre/post hookへの接続（New Attempt生成→Phase 4/5全Point
     再通過→Rejudge→Presented Answer選択）が未実施（P6-ACC-029未充足）。
   - Recording: RecordingServiceにReal Filesystem Writer Adapter
     （Atomic Write／Quota／Failure／Degraded、.gitignore境界）が存在しない
     （P6-ACC-049／051未充足）。Conversation Generation側の呼び出し箇所も未接続。
   これらは6-B-WU-006（Runtime Model Controlの実Bootstrap配線）と同種の
   Production Integration Riskであり、各WU完了時に個別にDocstring／Recovery
   Entryへ明記し、本Sessionでは意図的にScope外とした。

3. Guard Model／Governance Layer IdentityのAPI Route／Frontend露出
   Domain層のprojection関数（project_guard_model_identity／
   project_governance_layer_identity）は実装・Test済みだが、Web Route・UIには
   Main／Judgeの2Rowのみ配線されている（P6-ACC-053部分未充足）。

4. Judge Calibration／Bias Matrix（P6-D-WU-004）
   Position／Verbosity／Language／Self-preference比較Infrastructureは
   Phase 6-H Experiment Freezeと合わせて実施する方針だったが、6-Hでは
   OFF-mode Baselineのみ実施し、本Matrix自体は着手していない
   （P6-ACC-022未充足、Backlog）。

5. Mobile-width Interactive検証・Enter／Space Keyboard Activation
   `phase_6_g_wu006_accessibility_findings_ja_20260823021500.md`のとおり、
   Browser Automation Harnessの制約によりUNVERIFIED（Tool制約、App側の
   preventDefault()等は未検出）。Real Browser Golden Path（6-J User Mac
   Acceptance）での人手再検証を推奨。
```

## 5. Deferred Evidence／Current Impact

| Deferred Item | Current Impact |
|---|---|
| DeepSeek実Hardware Round-trip（Qwen→DeepSeek→Qwen） | Generic Switch機構自体はFake検証＋Qwen側実Hardware検証（同一Model定義でのContext Resize Switch Cycle、B-WU-007）で裏付け済み。DeepSeek固有のArtifact Round-tripのみ不在。Qwen単独運用では影響なし。 |
| Qwen Mode比較（OBSERVE／ENFORCE） | Judge／Repair／Guardrail／Governanceが未Live配線のため、6-HはOFF-mode Baselineのみ実施（`phase_6_h_wu001_002_qwen_baseline_experiment_ja_20260823024000.md`）。Baseline自体は実測・再現可能（Dataset＋Script保存済み）。Mode間の効果比較はLive配線後まで不可。 |
| RAG最終品質判定 | Acceptance P6-ACC-066どおりPhase 7前に完了主張していない（設計上の意図的Deferral、欠陥ではない）。 |
| Repair Candidateの全Governance／Guardrail Point再通過（P6-ACC-029） | Repair Orchestrator自体は状態遷移・Budget・Success評価まで実装済みだが、実Generation Flowへの接続が無いため、この保証は現時点で実測不可（Domain Testでは検証済み、Live Integration Testは存在しない）。 |
| Recording永続化（Atomic Write／Quota／Git境界、P6-ACC-049／051） | Real Writer Adapter不在のため実測不可。RecordingServiceのOFF/METADATA/FULL境界およびProtected Data Negative Matrix自体はDomain Testで確定済み。 |

## 6. Exact Mutation（全Phase 6横断・要約）

```text
新規Recovery Entry: 33件（docs/project/phases/phase_6/history/index/、
  Phase 6-0からPhase 6-I-WU-003まで時系列で全件記録済み）。

主要新規Module（src/margpa_runtime_llm/modules/）:
  runtime_model_control/（domain, application, ports.py）
  evaluation/（domain, application: judge_role_resolver, judge_prompt_builder,
    judge_output_decoder, judge_budget_gate, judge_mode_controller,
    evaluation_orchestrator）
  repair/（domain, application: repair_eligibility_resolver,
    repair_success_evaluator, repair_orchestrator, repair_mode_controller）
  runtime_observability/（domain: event, recording, feedback；
    projection: status_projection, component_identity_projection；
    presentation: safe_refusal；application: recording_service,
    recording_mode_controller）

主要新規Adapter（src/margpa_runtime_llm/adapters/）:
  runtime_model_control/（llama_cpp_backend, generation_busy_gate,
    model_definition_registry）
  evaluation/deterministic/evaluators.py

主要Bootstrap／Web変更:
  bootstrap/web_application.py（runtime_model_control_enabled、
    feature_modes_enabled配線、本WU-003で追加）
  bootstrap/runtime_model_control.py（新規）
  entrypoints/web/main.py（--phase-6-runtime-model-control、
    --phase-6-feature-modes CLI Flag追加、本WU-003で追加）
  web/runtime_model_control_routes.py、web/feature_modes_routes.py（新規）
  web/app.py（Local-loopback Gate、Router登録、Exception Handler追加）
  web/contracts.py（WebRuntimeへ4 Field追加）

Frontend新規（frontend/src/components/）:
  RuntimeModelStatusPanel.tsx／.test.tsx
  FeatureModesPanel.tsx／.test.tsx
  SettingsModal.tsx（両Panel配線、advancedTabVisible恒常化）

新規Test（Backend）: 累計で1305件相当から1405件へ増加（本Session開始時点比、
  Phase 6全体での新規Unit／Integration／model_smoke Test）。
新規Test（Frontend）: 165件相当から187件へ増加。

Git Mutation: 0（全Recovery Entryで明記のとおり、本Session中は一度もgit add／
  commit／push等を実行していない。既存のClean Working Treeを維持）。
```

## 7. DeepSeek Canonical／Derived／Load Evidence

```text
Canonical: 読み取り専用Accessは`phase_6_0_entry_reconciliation_and_freeze_recovery`
  で確認済み（Exact Model Authority Receipt記載のSymlink Resolved Target経由）。
Derived (gguf/manifests/conversion_work): 未作成。§2記載のPre-tokenizer
  Blockerにより変換未完了、Write-only-new-create領域への書き込み実績 0。
Load Evidence: 実DeepSeek ArtifactのLoad試行は0回（Derived Artifact不在のため
  試行自体が不可能）。CURRENT_TOOLCHAIN_UNSUPPORTED／NOT EXECUTEDとして確定。
```

## 8. Qwen→DeepSeek→Qwen／Rollback

```text
Generic Switch Mechanism（Idle-only Gate、Unload/Load、Atomic Commit、
  Load Failure→Rollback、Rollback Failure→Unavailable）:
    COMPLETE。Fake Backend（_QWEN_KEY⇔_DEEPSEEK_KEY相当のIdentity）による
    Unit Test（test_runtime_model_controller.py、6 Test）で全経路検証済み
    （`phase_6_b_wu003_status_determination_ja_20260822234500.md`）。
    実Qwen Hardwareでの同一機構の実証（Context Resize Switch Cycle）は
    `phase_6_b_wu007_real_hardware_manual_load_evidence_ja_20260823022500.md`
    で確立済み。

実DeepSeek Artifactを用いたReal Round-trip: NOT EXECUTED（§7参照、Derived
  Artifact不在のため実行不可）。

Classification: PARTIALLY_INTEGRATED（機構は実証済み、対象ArtifactがQwen×2
  相当に限定）。
```

## 9. Context／Max Tokens

```text
Unit Test: test_dynamic_context_and_tokens.py（6 Test、Context超過拒否、
  Reload失敗時のCurrent非採用、Max New Tokens Atomic変更、CAS Stale拒否を
  含む）で機構を検証済み。

実Hardware（pytest, model_smoke）: `test_runtime_model_control_smoke.py`で
  実Qwen3-4Bに対しContext Size 4096→2048の実Resize Cycleを実測（5.23秒、
  1 passed）。

実Production UI（本WU、6-I-WU-003）: 実際に起動したProduction Web App
  （Fake Fixtureではなく本物のCLI Entrypoint経由）上で、Context Size
  8192→4096への変更をSettings UIから実行し、実Unload/Reload・Revision 0→1
  ・State=active維持を実機・実Browserで確認した。Max New Tokensについては
  UI上のApply経路自体は同一WU-003検証環境で表示・操作可能であることを
  確認したが、値変更そのものの実Apply実行はContext Size変更のみで代表させ、
  Max New Tokens単独の実Production Apply実行は本Session内では未実施
  （Unit＋Model Smoke Testでは既に検証済みのため、Risk等価と判断）。
```

## 10. Judge／Calibration／Repair／Budget

```text
Judge:
  Typed Contract（LlmJudgeRequest/Response、prompt_digest経由でRaw Prompt
    非保持）、Role Resolver（MAIN_SELF／SHARED_ARTIFACT／INDEPENDENT_ARTIFACT／
    UNAVAILABLE）、Prompt Builder（決定的）、Strict Decoder（Fail-closed、
    6種のMalformed Shapeで検証）を実装・Unit Test済み。
  実Hardware: `test_real_local_judge_smoke.py`で実Qwen3-4BによるSelf-judge
    Round-tripを実測（3.65秒、JSON Decode成功、MAIN_SELF Independenceとして
    正直に記録）。
  実Production UI: 本WU（6-I-WU-003）でJudge Mode Toggle（off→observe）を
    実Serverに対しApplyし、Repair／Recordingと独立して変化することを実機確認。
  Live Generation介入: 未配線（§4-2参照）。

Calibration／Bias Matrix（Position／Verbosity／Language／Self-preference）:
  NOT EXECUTED（P6-D-WU-004、Backlog、P6-ACC-022未充足）。

Repair:
  Domain（Strategy識別子、State Machine、Budget Exhaustion判定）、Eligibility
    Resolver（Guardrail Deny最優先を保証）、Success Evaluator（Worse／Unknownを
    Improvedへ非昇格）、Orchestrator（execute_repair_plan、Before/After Run Ref
    分離）を実装・Unit Test済み（19+3 Test）。
  実Production UI: Repair Mode Toggle（off→observe）を実機Applyで確認。
  Live Generation介入（実際のRepair実行、Phase 4/5全Point再通過）: 未配線
    （§4-2、P6-ACC-029未充足）。

Budget:
  check_repair_budget()でMax Attempt／Depth超過をRaiseすることをUnit Testで
  直接検証済み（test_budget_exhausted_on_attempts_raises／on_depth_raises）。
  P6-I-WU-001のAdversarial Fault Matrixにも同項目としてEvidence登録済み。
```

## 11. Safe Refusal／Request Status

```text
Safe Refusal:
  render_safe_refusal()（JA／EN固定文言）をDomain層に実装済み
  （`phase_6_f_wu001_002_003_recovery_ja_20260823002000.md`）。
  実Production UI（本WU、6-I-WU-003）: Guardrail Mode Enforceを実際にApplyし
  （Configuration Control経由のCAS Apply成功、Revision 2）、Injection Marker
  を含む入力（"ignore previous instructions..."）を実送信した結果、実際に
  `Error: guardrail_reject_input`でBlockされAssistant回答が生成されないこと
  を実機で確認した。ただしこのUI表示は既存Phase 5由来のError Code表示であり、
  render_safe_refusal()のJA／EN固定文言そのものがこの経路で使われている
  ことまでは確認していない（正直な記録、未検証）。両者が同一Presentation
  Layerに統合されているかはCodex Independent Reviewでの確認事項とする。

Request Status:
  project_current_request_status()／project_historical_latest()を実装・
  Unit Test済み（Current Requestへの過去Point混在が構造的に不可能）。
  実Production UI: Guardrail Enforce Reject試行後、`guardrail.input`の
  Statusが「State: — → State: evaluated, Severity: high, Detection数: 5,
  Match数: 1, 実行Action数: 1」へ実際に変化することを実機確認（Not-invoked
  から実測値への遷移を実Browserで確認）。
  P6-I-WU-001のAdversarial Fault Matrixで、失敗State（"failed"）が他Pointの
  成功Stateと混在してもCoerceされず透過することも別途Unit Testで確認済み
  （`test_status_projection.py`）。
```

## 12. Feedback／Recording／Sensitive Data

```text
Feedback:
  UserFeedback／FeedbackRating／FeedbackRequestedAction／should_trigger_action()
  を実装・Unit Test済み。Rating単独ではAction（Retry／Regenerate／Repair）が
  Triggerされないことを直接検証（P6-ACC-044A）。No-auto-trainingはTraining
  Pipeline自体を実装しないことで保証（不在による保証）。

Recording:
  RecordingMode（OFF／METADATA／FULL）、SafeRecordingEnvelope（extra="forbid"）、
  RecordingService（OFF時はEnvelope構築・Writer呼び出しとも0回）を実装・
  Unit Test済み（11+2 Test、うち2件は本WU-001で追加したWriter Failure時の
  Fail-closed伝播Test）。Protected Data Negative Matrix（thinking／
  system_prompt／secret／rag_internal_context／tool_internal_state／
  hidden_original／partial_outputの7 Field）を構造的に受理不可能なことを
  直接検証済み。
  実Filesystem Writer Adapter: 未実装（§4-2、§5参照）。Atomic Write／Quota／
  Failure／Degraded（P6-ACC-049）、Private Evaluation／FeedbackのGit Stage
  除外（P6-ACC-051）は、Writer不在のため現時点で実測対象が存在しない
  （PASSともFAILとも主張しない、Evidence未生成として記録）。

Sensitive Data／Secret非露出:
  P6-I-WU-001（Adversarial Fault Matrix）でCode Audit済み。
  RuntimeModelStatusResponse等のWeb Response Contractは全てextra="forbid"＋
  明示的Field Allowlistで構成され、Load/Rollback Failureのreason
  （Local File Path等を含みうる）はWeb層のCatch-all 502 Responseで固定Safe
  Messageに置換され、Snapshotのfailure_reasonもWeb Responseへ一切露出しない
  ことを確認済み。
```

## Validation（Phase 6全体、直近実行分）

```text
Backend Full Suite : 1405 passed, 5 deselected in 61.55s
Backend model_smoke : 4 passed, 1 skipped, 1403 deselected
Ruff                : All checks passed!
Mypy                : Success: no issues found in 418 source files
Frontend typecheck  : エラー0
Frontend lint       : エラー0
Frontend test       : Test Files 22 passed (22) / Tests 187 passed (187)
Frontend build      : 成功（app.js 292.30kB gzip 84.82kB）
Git Mutation        : 0（Working Tree Clean維持）
```

## False Completion Self-check

```text
本文書のいかなる記述も「未測定の事実をPASSとして主張」していない。
Live Generation Path未配線、Recording Writer不在、Calibration Matrix
未着手、DeepSeek NOT EXECUTED、Guard／Governance Layer Identity UI未露出、
Mobile／Keyboard a11y UNVERIFIEDの6点は、いずれも本文書内で明示的に
NOT EXECUTED／UNVERIFIED／Backlogとして記録し、Evidence不在をEvidence
不在のまま提示した。全79件のAcceptance Matrix IDに対する網羅的な
1件ずつのRe-auditは実施していない旨も§1に明記した。
```

## Human Burden（Phase 6-J以降でUserに残る作業）

```text
1. Codex Independent Reviewの実施（Git Mutation 0のため、Review対象は
   Working Tree差分そのもの）。
2. User Mac Manual Acceptance（Acceptance Matrix §9の10項目）。ただし
   項目9「Judge OBSERVEとRepair ENFORCEの有界Golden Path」は、Live
   Generation配線が未完了のため、現状のWorking Treeでは実施不可能である
   ことを事前に認識されたい（§4-2参照）。
3. §4記載のController-owned Work（DeepSeek Toolchain、Live Path配線、
   Recording Writer、Guard/Governance Identity UI、Calibration Matrix、
   a11y再検証）について、Phase 6-J内で実施するかPhase 7以降へ回すかの
   意思決定。
```

## Rollback

```text
本Session中のGit Mutationは0件（全てWorking Tree上のUncommitted Changeとして
存在）。Rollbackが必要な場合、`git status`／`git diff`で本Session差分の
全容を確認したうえで、対象File単位のgit checkout、またはWorking Tree全体の
git stash／git resetのいずれかをUserが選択可能（Claude側では実行しない、
Destructive Git Operationは常にUser自身の判断・実行に委ねる）。
Runtime Data面では、本WU-003検証で使用したConversation Persistenceは
既存User実Data（runtime_data/persistent/配下）と完全に分離したScratchpad
Directory（`/private/tmp/claude-501/.../scratchpad/golden_path_runtime_data`）
のみを使用しており、Rollback対象はSession終了後の自動消滅のみで足りる。
```

## Next Exact Route

```text
本文書の作成をもってP6-I COMPLETE_CANDIDATEに到達した（Frozen Handoff §9の
Stop Condition「P6-I COMPLETE_CANDIDATE到達」に該当）。指示どおりPhase 6-J、
Git、Phase 7へは進まず、ここで停止する。
```
