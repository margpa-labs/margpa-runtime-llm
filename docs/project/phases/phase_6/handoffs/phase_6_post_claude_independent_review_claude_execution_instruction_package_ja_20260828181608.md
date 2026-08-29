# Phase 6 Post-Claude Independent Review — Claude Copy-paste Execution Instruction Package

```yaml
document_id: phase_6_post_claude_independent_review_claude_execution_instruction_package_20260828181608
status: current_copy_paste_instruction_package
classification: user_relay_cross_provider_execution_instruction
created_at: 2026-08-28 18:16:08 JST
provider: Claude
role: 設計者兼実装者役
task_state: continued_task_with_imminent_compaction_and_resource_stop_risk
context_remaining_user_report: 6_percent
five_hour_availability_remaining_user_report: 39_percent
active_handoff: phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md
implementation_authority: REQUIRES_MESSAGE_3_EXACT_START
phase_6_closure: PROHIBITED
git: PROHIBITED
```

## 1. 使用方法

現在のClaude `設計者兼実装者役` Taskへ、Message 1、Claude Receipt、Message 2、Claude Receipt、Message 3の順でそのまま送る。

Context残量6%のため、Message 2読了中またはMessage 3開始直後のAuto-Compactionを前提とする。5時間枠残39%のため、途中Resource Stopも前提とする。Message 3は、CompactionまたはResource Stopが起きても最新Recovery Indexから差分復旧できるよう、Entry前・Work Unitごと・Package境界・高Cost処理前のIndex更新を強制する。

Claudeが5時間制限解除後に自動再開しない場合だけ、Message 4を送る。

## 2. Message 1 — Continued Role／Authority Re-bootstrap

```text
【Continued Claude Task／Role・Authority Re-bootstrap】

Provider: Claude
Role: 設計者兼実装者役
Task Identity: Current Claude Task
Task State: CONTINUED_REWORK_TASK_WITH_IMMINENT_COMPACTION

このTaskはFresh Taskではなく、直前のPhase 6 Production Wiring Delta Complete Candidateを返したCurrent Claude Taskです。

ただし、Context残量はUser観測で約6%です。Auto-Compaction後の会話記憶、要約、旧判断、旧Complete Candidate ClaimをAuthorityまたはCurrent Contractとして使用しないでください。Repository内のStable Role文書、P6-GOV-019、最新Exact Rework Handoff、Recovery Indexだけを正本としてください。

5時間枠残量はUser観測で約39%です。Resource Stopが起こり得ることを前提にしてください。

このMessage段階で許可するのは、次の3文書のReadとReceipt返却だけです。

1.
<PROJECT_ROOT>/docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md

2.
<PROJECT_ROOT>/docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md

3.
<PROJECT_ROOT>/docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md

まだSource／Test／Config／Frontend／Docs Mutation、Command実行、Network、Git、Model Load、Browser、Phase 6 ClosureまたはPhase 7を開始しないでください。

全文読了後、次だけを日本語で返してください。

Provider: Claude
Role: 設計者兼実装者役
Task Identity: Current Claude Task
Task State: CONTINUED_REWORK_TASK
Mandatory Role Reading: COMPLETE
Conversation Context as Authority: PROHIBITED
Repository Recovery as Canon: REQUIRED
Context Remaining Signal: 6% RECEIVED
Five-hour Remaining Signal: 39% RECEIVED
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_HANDOFF

返却後は停止してください。
```

## 3. Message 2 — Exact Differential Handoff Bootstrap

```text
【Phase 6 Post-Claude Independent Review／Exact Differential Handoff Bootstrap】

Controller Independent Reviewにより、直前のComplete CandidateはPhase 6 Closure Candidateとして棄却され、ADJUST／REWORK REQUIREDになりました。

次の3文書を全文読んでください。

1. Controller Independent Review Evidence
<PROJECT_ROOT>/docs/project/phases/phase_6/history/operations/phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md

SHA-512:
f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240

2. Exact Differential Rework Handoff
<PROJECT_ROOT>/docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md

SHA-512:
8de37770693bf84c7e6a51fb46189341a2f3035a3ccf30c19bf6dcb1284f1991a0322573c783d65153820dbdea62e6e99063f697fbded637ef65132b35d5736a

3. Automation Empirical Result
<PROJECT_ROOT>/docs/project/shared/history/automation/claude_fresh_task_internal_review_rework_loop_empirical_result_ja_20260828180240.md

SHA-512:
ac85b4ed40cecd3364956ca9889d207de04516c48e76c0f6e55e39e74c896d8ed7f439a2692b64b954a9720d7e085de8730081c40e1fabf715f827ce22692d8f

Exact Rework Handoff §3に指定されたMandatory Reading 1〜26を、記載順で全文読んでください。Base Exact Handoff、P6-GOV-018 Addendum、Manual Evidence、Claude Candidate、P6-GOV-019、Source再導出対象を省略しないでください。

優先順位は次です。

1. Stable Role／Authority Rule
2. P6-GOV-019 Controller Independent Review
3. 最新Exact Differential Rework Handoff
4. Base Exact Handoff＋P6-GOV-018 Addendum
5. Historical Candidate／Recovery Evidence
6. 会話ContextまたはClaude自身の旧判断

Preserved Baseline:
- Phase 6 Package 0〜I
- Claude Package K〜QのうちP6-GOV-019で棄却されていない成果
- 成立済みRegression Evidence

Superseded Claims:
- Open Major 0
- P6-CODEX-047等の完全解消Claim
- P6-DELTA-021 PASS
- P6-DELTA-026 PARTIAL
- 直前CandidateをClosure Candidateとして扱うこと

Current Open Major:
- P6-CODEX-062〜068

Next Exact Work Unit:
- P6-RR-R0-WU-001

この段階で許可するCommandは、指定文書のReadとSHA-512照合に必要なRead-only Commandだけです。Mutation、Test、実装調査Command、Network、Git、Model LoadまたはBrowserを開始しないでください。

DigestとMandatory Reading確認後、次だけを日本語で返してください。

Provider: Claude
Role: 設計者兼実装者役
Task Identity: Current Claude Task
Mandatory Reading 1-26: COMPLETE / MISSING
P6-GOV-019 Digest: MATCH / MISMATCH
Exact Rework Handoff Digest: MATCH / MISMATCH
Automation Evidence Digest: MATCH / MISMATCH
Active Contract: P6-GOV-019 + Phase 6 Post-Claude Independent Review Exact Rework Handoff
Preserved Baseline: Phase 6 0-I + accepted K-Q results
Superseded Claims: RECOGNIZED
Current Open Major: P6-CODEX-062-068
Next Exact Work Unit: P6-RR-R0-WU-001
Recovery Index Requirement: ENTRY + EACH WORK UNIT + EACH PACKAGE + PRE-COMPACTION/RESOURCE-STOP
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_USER_START

Digest不一致またはReading Missingがあれば、Observed DigestとExact Pathを返してください。
Receipt返却後は停止してください。
```

## 4. Message 3 — Exact Start／Recovery-intensive Long-run

```text
Phase 6 Post-Claude Independent Review Reworkを開始する。

P6-GOV-019とPhase 6 Post-Claude Independent Review Exact Rework HandoffをActive Execution Contractとして、P6-RR-R0-WU-001からP6-RR-R8-WU-008まで差分Long-runしてください。

Context残量約6%および5時間枠残約39%のため、Recovery Indexを次のMandatory Contractで作成してください。

1. 最初のSource／Test／Config／Frontend Mutationまたは実装Commandより前に、Entry Recovery Indexを作成する。
   Directory:
   docs/project/phases/phase_6/history/index/
   Required content:
   - Active Contract Path／Digest
   - Context 6% Signal
   - Five-hour 39% Signal
   - Preserved Baseline
   - Open Finding P6-CODEX-062〜068
   - Current Package／Work Unit
   - Changed File 0時点Inventory
   - Exact Next Action

2. 各Work Unit完了直後に、Current Package Recovery IndexへAppend-onlyでCheckpointを残す。

3. 各Package開始時にPackage Entryを作り、各Package完了時にFinal Package Recovery Indexを必ず作る。

4. 次の前には必ず最新Checkpointを作る。
   - Full Test／Canonical Static Verification
   - Frontend Build
   - Browser／Model Load
   - 長時間Command
   - Auto-Compactionが近いと判断した時
   - 5時間制限またはResource Stopが近い時
   - True Stop Conditionにより停止する直前

5. Auto-Compaction後または5時間制限解除後は、実装を再開する前に必ず次を全文再読する。
   - Stable Role文書3件
   - Active Exact Rework Handoff
   - 最新Package Recovery Index
   - 直前Package Recovery Index
   - Current Package Section
   その後、成立済みWork Unitを再実行せずExact Next Actionから差分再開する。

6. Platformが5時間制限解除後に自動再開する場合も同じRecovery手順を実行する。自動再開しない場合は停止状態を保持し、UserのResume Messageを待つ。

7. Index未作成のまま次Packageへ進むことを禁止する。進捗報告だけでRecovery Indexを代替しない。

Package R0〜R8を連結実行してください。Routineな設計選択、既知のFinding、Authority不要なFixture作業、Internal ReviewでFindingが出たことを理由にUserへ確認せず、許可Scope内を継続してください。

Selene／Qwen3Guardの実Model AuthorityまたはNetwork Authorityは付与していません。Authority不要のFactory、Router、Lifecycle、Budget、Fixture、Failure、UI、Semantic 109件、Recording／Observabilityを継続し、実Model項目だけをNOT RUN／AUTHORITY REQUIREDへ分類してください。

Implementation Freeze後、Claude Internal Review Cycle 1を実施してください。Requirement／AcceptanceごとにScenarioをExecutable Negative Testへ変換し、P6-GOV-018 Scenario A〜CとP6-GOV-019 Reproductionを必ず実行してください。FindingがあればReworkし、Cycle 2以降を行ってください。

Open Majorが残る場合は0へ捏造しないでください。

進捗報告は日本語で行い、報告後もTrue Stop Conditionがなければ自走継続してください。

Maximum Claim:
COMPLETE_CANDIDATE または COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE

禁止:
- Phase 6 Closure
- Phase 7
- Git Stage／Commit／Push／Branch
- Backup
- Roadmap／Public／Stable Constitution更新
- Provider Memory
- User runtime_data
- 未許可Network
- Project Root外Model Artifact接触
- Historical Evidenceの上書き／削除

完了後はPackage R8 Final Recovery IndexとExact Return Handoffを作成し、プロジェクト責任者兼設計統括者役によるIndependent Review待ちで停止してください。
```

## 5. Message 4 — Auto-compaction／5時間制限後のManual Resume

Claudeが自動再開しない場合だけ送る。

```text
【Phase 6 Post-Claude Independent Review Rework／Exact Recovery Resume】

Provider: Claude
Role: 設計者兼実装者役
Task Identity: Current Claude Task

Phase 6 Post-Claude Independent Review Reworkを、最新Recovery Indexから差分再開してください。

会話Context、Compaction Summaryまたは制限前の記憶だけで再開しないでください。

再開前に必ず次を全文読んでください。

1. Stable Role文書3件
2. Active Exact Rework Handoff
3. docs/project/phases/phase_6/history/index/ 内の最新Package Recovery Index
4. その直前のPackage Recovery Index
5. Current Package Section

最新Recovery IndexのPath、Digest、Last Completed Work Unit、Exact Next Work Unitを日本語で一度報告した後、成立済みPackage／Work Unitを再実行せず自走継続してください。

Recovery Indexが存在しない、Digestが一致しない、またはCurrent SourceとIndexが矛盾する場合だけSTOPPED_SAFEで返してください。

Authority、禁止事項、Maximum Claim、Return ContractはActive Exact Rework Handoffと開始Messageから変更ありません。
```

## 6. Controller Correction Record

本Instruction Packageは、Exact Rework Handoff作成時にCopy-paste指示文を同時作成しなかったController運用違反を是正する。Stable Rule：

`docs/project/shared/task_roles/codex_controller_cross_task_cross_provider_instruction_package_operating_rule_ja.md`

同Ruleに従い、今後もCross-provider Rework／Resume／Addendumごとに、Pathと開始宣言だけではなく完成済みInstruction Packageを同時作成する。
