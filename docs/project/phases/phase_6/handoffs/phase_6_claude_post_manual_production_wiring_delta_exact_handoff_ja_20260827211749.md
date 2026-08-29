# Phase 6 Post-Manual Production Wiring Delta — Claude Exact Execution Handoff

```yaml
document_id: phase_6_claude_post_manual_production_wiring_delta_exact_handoff_20260827211749
status: frozen_prepared_not_active
classification: cross_provider_differential_exact_execution_handoff
phase: phase_6
from_provider: Codex
from_role: プロジェクト責任者兼設計統括者役
to_provider: Claude
to_role: 設計者兼実装者役
target_task_identity: fresh_claude_task_pending
created_at: 2026-08-27 21:17:49 JST
implementation_authority: false
activation_key_1_exact_handoff: frozen
activation_key_2_user_start: missing
exact_model_authority_selene_qwen3guard: missing
exact_network_authority_official_provenance: missing
closure_authority: false
git_authority: false
```

## 1. 現在状態と目的

```text
Phase 6                           : IN PROGRESS / CLOSURE BLOCKED
Codex Remaining Rework 0〜I      : IMPLEMENTED / EVIDENCE PRESERVED
Package J                        : BOUNDED COMPLETE CANDIDATE
Controller Independent Review    : ADJUST / P6-GOV-016
User Mac Manual Check M-1〜M-7   : ALL EXECUTED / ADJUST / P6-GOV-017
Differential Design K〜Q         : FROZEN
Claude Implementation Authority : FALSE
```

本Handoffの目的は、Codexが実装したPackage 0〜Iを最初から作り直すことではない。P6-GOV-016とP6-GOV-017で実証されたProduction Wiring GapだけをPackage K〜Qとして修正し、Controller Independent Reviewへ返すことである。

主要Gapは次である。

1. Main DropdownがConfiguredだけを変え、実Main Switchを行わない。
2. Selene／Qwen3GuardのDedicated Production Factory／Routeが未成立。
3. Built-in Deterministic選択時も実際はMain-self LLMを実行する。
4. ARGD／DAGD Semantic Rule 109件が実評価されず、32件Selected／0件Evaluated、残77件の実Dispositionがない。
5. Configured／Active／Executed／Recorded／Displayed Provider Identityが一致しない。
6. Judge／RecordingのCurrent／Historical／Live Refresh／Failure Reasonが不正確。
7. User指定のBounded Advanced Mode／Sidebar UI Deltaが未実装。

## 2. Two-key Activation

本書をClaudeへ渡す、Claudeが全文を読む、PreflightがPASSする、利用可能量が回復する、開始予定日になる、という事実だけではImplementation Authorityは発生しない。

Fresh Claude Taskの初期化は次の順序とする。

### Step 1 — Role／Authority Bootstrap

ControllerまたはUserがFresh Claude Taskへ次を通知する。

```text
Provider: Claude
Role: 設計者兼実装者役
Task Identity: Fresh Task

旧Claude Taskの会話Context、Memory、Authority、未完了状態、自己判断したScopeを継承しない。
最初に指定されたAutomation／Role文書だけを読み、WAITING_FOR_EXACT_USER_STARTで停止する。
```

この段階では実装、Source Mutation、Test、Network、Model Loadを行わない。

### Step 2 — Exact Handoff Bootstrap

本HandoffとMandatory Readingを渡し、Claudeは次を返す。

```text
Mandatory Reading: COMPLETE
Digest Verification: COMPLETE / EXACT MISMATCH LIST
Active Contract: IDENTIFIED
Next Exact Work Unit: P6-RR-K-WU-001
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_USER_START
```

### Step 3 — User Start

Userが次を明示した時だけ、Two-key Activationが成立する。

```text
Phase 6 Production Wiring Delta Reworkを開始する。
```

曖昧な「続けて」「よろしく」「再開して」は、上記Exact Startの代用にしない。

## 3. Frozen Package Identity

### 3.1 Manual Acceptance Evidence

```text
Path:
docs/project/phases/phase_6/history/operations/
phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md

SHA-512:
1a4882f473ffc1019b4f4380e14f237e83ae481de02d92511ade3756f9e4d9e4123959b80b8a204e9b6fa95390161b85230f7685daf2853ccb6b62bbaf738da7
```

### 3.2 Differential Design／Execution／Acceptance Freeze

```text
Path:
docs/project/phases/phase_6/history/operations/
phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_ja_20260827211749.md

SHA-512:
e464ef021708e0f29183053c0045850f5ebc3d5a234a60d3c67fab20b107163d4818d95fc6fcab5befe7999df34e5a85e93b67c29086ffdfe6aca17d022ab4a9
```

Digestが一致しない場合、記憶や会話要約で補完しない。Mismatch Path／Observed Digestを報告し、該当Frozen ContractのMutationを開始しない。他のRead-only照合は継続してよい。

## 4. Mandatory Reading Order

Fresh Taskは次を順番どおり全文読む。部分要約だけで置換しない。

### 4.1 Automation／Role

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`
5. `docs/project/shared/history/planned_work/claude_fresh_designer_implementer_task_activation_sequence_reservation_ja_20260826094454.md`
6. `docs/project/shared/history/automation/claude_task_recreation_and_cross_provider_role_identity_operating_correction_ja_20260826094454.md`
7. `docs/project/shared/history/automation/codex_fresh_executor_phase_6_remaining_rework_long_run_stop_resume_return_and_independent_review_evidence_ja_20260826204058.md`

### 4.2 Phase 6 Stable Contract

8. `docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md`
9. `docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md`
10. `docs/project/phases/phase_6/adr/phase_6_adr_ja.md`
11. `docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md`
12. `docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md`

### 4.3 Remaining Rework Baseline

13. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_design_freeze_ja_20260825130924.md`
14. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md`
15. `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_j_bounded_completion_recovery_ja_20260826202200.md`
16. `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_bounded_complete_candidate_handoff_ja_20260826202200.md`

### 4.4 Controller／User Finding

17. `docs/project/phases/phase_6/history/operations/phase_6_gov016_remaining_rework_controller_independent_review_ja_20260826202919.md`
18. `docs/project/phases/phase_6/handoffs/phase_6_user_mac_bounded_manual_check_after_remaining_rework_ja_20260826202919.md`
19. `docs/project/phases/phase_6/history/operations/phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md`
20. `docs/project/phases/phase_6/history/operations/phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_ja_20260827211749.md`
21. 本Exact Handoff。

過去のComplete Candidate／Rework HandoffはHistorical Evidenceであり、本差分Scopeを縮小しない。矛盾時の優先順は次である。

```text
Latest explicit User instruction
→ 本Exact Handoff
→ P6-RR-DELTA Freeze
→ P6-GOV-017
→ P6-GOV-016
→ Original P6-RR Freeze
→ Phase 6 Stable Contract
→ Historical Evidence
```

## 5. Exact Objective

Package K〜Qを連結実行し、次を成立させる。

1. Production Compositionが選択ProviderのFactory／Lifecycle／Routerを使用する。
2. Main Dropdownを実Switch Transactionへ接続し、Provider Selection／Model Status／Sidebarを同期する。
3. Selene Dedicated JudgeとQwen3Guard Dedicated Guardを実Production経路へ接続する。
4. Built-in Deterministicから暗黙LLM Callを完全に除去する。
5. ARGD／DAGD Semantic Rule 109件すべてに実Disposition／Reasonを与える。
6. Selected Provider別Stage BudgetとRepair Rejudgeを接続する。
7. Configured／Active／Executed／Recorded／Displayed Identityを一致させる。
8. Current／Historical／OFF／Live Refresh／Recording Correlation／Failure Reasonを修正する。
9. User指定のBounded Advanced Mode／Sidebar UI Deltaだけを前倒し実装する。
10. Original Acceptance 40 IDとDelta Acceptance 20 IDを再導出し、ControllerへComplete Candidateを返す。

## 6. Package Execution Contract

Frozen Work UnitはP6-RR-DELTA Freeze §5を正本とする。

```text
P6-RR-K : Recovery / As-built Reconciliation
P6-RR-L : Official Provenance / Artifact Authority / Factories
P6-RR-M : Provider Routing / Lifecycle / Main Switch
P6-RR-N : Semantic / Built-in / 109 Rule Integration
P6-RR-O : Dedicated Guard / Judge / Repair / Budget
P6-RR-P : Observability / Recording / Bounded UI Delta
P6-RR-Q : Integrated Verification / Acceptance / Return
```

Package 0〜Iを再実装しない。必要な修正が既存実装に重なる場合、現在のSourceを土台とする最小差分に限定し、成立済みConcurrency、Cancellation、Atomicity、Recording、Migration、Main Runtimeを弱体化しない。

各Package終了時に次へRecovery Indexを作る。

```text
docs/project/phases/phase_6/history/index/
phase_6_post_manual_delta_package_<k_to_q>_<topic>_ja_<YYYYMMDDHHMMSS>.md
```

Indexには少なくとも次を記載する。

```text
Package / Completed WU
Frozen Contract Digest
As-built before / after
Changed File and semantic purpose
Focused / Static / Full evidence
Acceptance disposition
Open Finding
Incident accounting
Authority / Root / Network / Git / runtime_data / Provider Memory inventory
Task-owned temporary / active process / loaded model
next_exact_work_unit
```

Recovery Index作成後もTrue Stop Conditionがなければ自走継続する。

## 7. Authorized Root／Mutation Scope

Authorized RootはProject Rootだけである。

```text
margpa-runtime-llm/
```

User Start後、P6-RR-DELTAに必要な最小差分として次を変更できる。

- `src/margpa_runtime_llm/modules/runtime_governance/`
- `src/margpa_runtime_llm/adapters/runtime_governance/`
- `src/margpa_runtime_llm/modules/evaluation/`
- `src/margpa_runtime_llm/adapters/evaluation/`
- `src/margpa_runtime_llm/modules/guardrail_governance/`
- `src/margpa_runtime_llm/adapters/guardrail_governance/`
- `src/margpa_runtime_llm/modules/runtime_model_control/`
- `src/margpa_runtime_llm/modules/inference/`
- `src/margpa_runtime_llm/modules/runtime_observability/`
- `src/margpa_runtime_llm/bootstrap/`
- `src/margpa_runtime_llm/web/`
- `src/margpa_runtime_llm/entrypoints/web/`
- `frontend/src/`
- 対応する`tests/`。
- `config/models/`のRole Definition。
- `config/judge_templates/selene/`のExact Official Template／Manifest。
- `config/profiles/`のRole／Stage Budget最小差分。
- `docs/project/phases/phase_6/history/index/`のRecovery。
- `docs/project/phases/phase_6/history/operations/`のAppend-only Correction／Evidence。
- `docs/project/phases/phase_6/handoffs/`のReturn Handoff。

Canonical `definitions/`はRead-onlyであり、Phase 6を通すためにSource Definitionを変更しない。

## 8. Dedicated Model／Network Authority Boundary

### 8.1 Existing Receiptの限界

既存の`phase_6_exact_model_authority_receipt_ja_20260822212732.md`はQwen／DeepSeekを対象にしたHistorical Receiptである。Selene／Qwen3Guardへ適用範囲を拡張しない。

本Handoffは、次を許可しない。

- Project Root外に解決されるSelene／Qwen3Guard Symlink TargetのRead／Stat／Load。
- Artifact全体またはSiblingのInventory／Digest。
- Model Download、Update、Quantization、Move、Delete、Promotion。

Real Dedicated Providerを検証する前に、UserまたはControllerが別のExact Model Authority Receiptを発行しなければならない。Receiptは少なくとも次を固定する。

```text
Role / Model ID
Project-visible path
Resolved exact target
Allowed read / stat / load / inference operations
Forbidden sibling traversal
Mutation = 0
Validity period / Work Unit
Disk / Memory / Hardware gate
Return evidence
```

Receiptがない場合、Factory、Router、Fixture、Failure、UIを継続し、Real Model項目を`NOT RUN / AUTHORITY UNAVAILABLE`とする。これだけを理由にPhase 6 Delta全体を停止しない。

### 8.2 Official Provenance Network

参照候補の正本は次である。

```text
Selene Prompt Templates:
https://github.com/atla-ai/selene-mini/tree/main/prompt-templates

Selene Model:
https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B

Qwen3Guard Model:
https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B

Qwen3Guard Technical Description:
https://qwenlm.github.io/blog/qwen3guard/
```

Network GET／Cloneは本Handoffだけでは許可されない。Exact Domain／URL／Method／保存先を定めたUser Network Authorityがある場合だけ取得する。Package Install、Model Download、Homebrew変更、Repository CloneをProvenance GETへ便乗させない。

Network Authorityがない場合、Localに既に保存されたExact Evidenceを検証し、足りないProvenanceをTyped PARTIALとする。存在しないOfficial Contractを推測・創作しない。

## 9. Project内Temporary Contract

Activation後、最初に次を作る。

```text
.venv/.t/phase_6_claude_post_manual_delta_<YYYYMMDDHHMMSS>/
```

- 全`pytest`に`--basetemp=<task-temp>/pytest`を指定する。
- Frontend Commandは`frontend/`をWorkdirとする。
- `NPM_CONFIG_CACHE`、`TMPDIR`、Python／XDG／HF／Browser CacheをTask Temp内へ指定する。
- `/dev/null`、`/tmp`、User Cache、OS Default TempへRedirect／Writeしない。
- 既存`.venv/.t/`、`.t/`、他Task TempをCleanupしない。
- Task-owned TempだけをFinal Returnで列挙し、無断削除しない。

## 10. Forbidden Actions

次は常に不許可である。

- Authorized Root外Action。Read、Stat、Enumeration、Redirect、Temp作成を含む。
- `.claude/`、`.codex/`その他Provider Memory内部のRead／Write／Enumeration／Semantic Use。
- User `runtime_data/`のRead／Write／Migration／Test Use。
- Git Command全般。Read-only `git diff/status/log`も含む。
- Commit、Push、Branch、Tag、Backup、Release。
- 無許可Network、Package Install、Homebrew変更、Model Download。
- Model Artifact／Canonical DefinitionのMutation。
- Roadmap、Public Docs、Phase 6 Closure、Phase 7への変更。
- 既存Evidenceの削除、改変、Incident 0への書換え。
- Scope外UI磨き込み、Phase 7 RAG、Phase 8 Agent、Phase 9 Experiment、Phase 10項目。

Projectの状態把握にGitを使わない。対象File、Recovery Index、指定Digest、Test EvidenceからAs-builtを構成する。

## 11. Execution Control

### 11.1 Entry

- EntryでCanonical Full Suiteを無条件再実行しない。
- Package JのBackend／Mypy／Ruff／Frontend EvidenceをBaselineとして読み、変更前はFocused Probeだけを使う。
- SourceとProduction Wiringを直接照合し、Fixture PASSをProduction PASSとしない。

### 11.2 Long Run

- K-WU-001からQ-WU-006まで、True Stop Condition以外で連結実行する。
- Package完了、進捗報告、性質の変化、Network unavailable、Real Model unavailableを通常停止理由にしない。
- 不明点はFrozen ContractとSourceから解決し、User選択が最終仕様を変える場合だけ停止する。
- Userへの進捗報告は日本語で簡潔に行い、報告後も自走する。

### 11.3 Auto-Compaction／5時間制限

Claude Platformが自動再開した場合は、次を行う。

1. 本Handoff、P6-RR-DELTA、P6-GOV-017、最新Recovery Indexを再読する。
2. 指定Digestと`next_exact_work_unit`を確認する。
3. Gitを使わず、対象File本文からCurrent Mutationを再構成する。
4. 完了Package／WUを再実行しない。
5. Active Process／Model Load／Task Tempを確認し、差分再開する。

自動再開機能が動かない場合は`STOPPED_RESOURCE／next_exact_work_unit`をReturnし、再開を捏造しない。

## 12. True Stop Conditions

次だけは即時停止し、Append-only Incident Recoveryと`STOPPED_SAFE` Return Handoffを作る。

- Project Root外Action。
- Provider Memory内部接触。
- User `runtime_data`接触。
- 無許可Git／Network／Install／Model Artifact Action。
- Canonical Definition／Frozen Contract／Model Artifact Integrity mismatch。
- Scope外の不可逆Mutation。
- User DecisionなしではFinal仕様が実質的に変わる新しいMaterial Scope。
- 実Resource Hard StopによりCommandを安全に完了・停止できない。

次は単独ではTrue Stop Conditionではない。

- Provider unavailable。
- Hardware unavailable。
- Official ProvenanceをNetwork取得できない。
- Focused Test failure。
- Open Major finding。
- Package完了。
- Compactionが近い。
- 実装が慎重さを要する。

これらは記録、修正、隔離またはPARTIAL分類を行い、可能な後続を継続する。

## 13. Required Verification

### 13.1 Focused

少なくとも次を検証する。

- Production Factory availability／failure／rollback。
- Main Configured→Active Switch／failure rollback／status convergence。
- Selene selected routeとMain-self非実行。
- Qwen3Guard additive routeとRule Base維持。
- Built-in DeterministicでModel Call 0。
- Semantic 109件の全Disposition／Batch Merge／Cancel／Late Publish。
- Provider別Budget、Repair、Selected Provider Rejudge。
- Current／Historical／OFF／Live Refresh。
- Recording Request correlation。
- Bounded UI Delta。

### 13.2 Canonical

Final Package Qで実行する。

```text
Backend Full Test
Canonical Mypy: pyproject.toml files scope
Ruff Format Check
Ruff Check
Frontend Typecheck
Frontend Lint
Frontend Test
Frontend Build
```

Test Temp／Cacheは§9へ隔離する。既知Failureを0へ捏造しない。

### 13.3 Real Provider／Browser

- Exact Model Authorityがある場合だけSelene／Qwen3Guard Real Loadを行う。
- Main Qwen→DeepSeek→Qwenは、既存Artifact AuthorityとCurrent Scopeが有効な場合だけ実行する。
- User Mac専用Metal／Browser／Two-tab／RestartはUser Manual Gateにできる。
- Real Model／Browser未実施をFixture PASSで代替しない。

## 14. Acceptance Re-derivation

Final Returnでは次を両方示す。

1. Original P6-RR Acceptance 40 IDの全Disposition。
2. P6-DELTA-001〜020の全Disposition。

少なくとも次のOriginal IDは差分修正後に再導出する。

```text
P6-RR-ACC-003〜009
P6-RR-ACC-014〜018
P6-RR-ACC-019〜035
P6-RR-ACC-037〜039
```

`PASS / PARTIAL / NOT RUN / USER MANUAL GATE / FAIL`を区別する。P6-RR-INC-001とP6-RR-ACC-039のHistorical Nonconformanceを保持し、Literal Incident 0を主張しない。

## 15. Claim Boundary

Claudeが主張できる最大状態は次である。

```text
Phase 6 Production Wiring Delta Rework:
  COMPLETE_CANDIDATE_WITH_EXACT_PASS_PARTIAL_NOT_RUN_FAIL

Phase 6 Closure: NOT CLAIMED
Phase 7: NOT STARTED
```

次を主張しない。

- ConfiguredだけでActive／Executedである。
- Built-in表示だけでDeterministic経路が成立した。
- Selected 32だけで109件を評価した。
- Test PASSだけでProduction Wiringが成立した。
- FixtureだけでReal Selene／Qwen3Guardが成立した。
- Real Model未実行で品質Acceptanceが成立した。
- User Manual GateをClaudeがPASSした。
- Incidentが0だった。
- Phase 6 Closure、Phase 7 Ready、Git Ready。

## 16. Exact Return Format

Final Returnは日本語で、少なくとも次を含む。

```text
Provider / Role / Task Identity
Status
Completed Package / WU
Frozen Contract Digest verification
Changed files and semantic purpose
Configured / Active / Executed / Recorded Main, Guard, Judge
Main Switch result and status convergence
Selene / Qwen3Guard Factory, artifact, prompt / output contract identity
Built-in Model Call count
Semantic 109 disposition count and remaining reason count
Judge / Repair / Rejudge budget and provider identity
Current / Historical / OFF / Live Refresh evidence
Recording correlation evidence
Bounded UI result
Original Acceptance 40 disposition
Delta Acceptance 20 disposition
Focused / Static / Full / Frontend / Real Provider / Browser evidence
Open Critical / Major / Non-critical findings
Historical and current incident accounting
Root-outside / Provider Memory / runtime_data / Git / Network / Model mutation inventory
Task-owned temporary / active process / loaded model
Claims not made
Exact next action: Controller Independent Review
```

Return Handoff Pathは次の形式とする。

```text
docs/project/phases/phase_6/handoffs/
phase_6_claude_post_manual_production_wiring_delta_<status>_handoff_ja_<YYYYMMDDHHMMSS>.md
```

Return作成後は停止する。Phase 6 Closure、Git、Backup、Roadmap、Phase 7へ進まない。
