# Phase 6 Remaining Rework — Package H Recovery

```yaml
document_id: phase_6_remaining_rework_package_h_judge_repair_failure_recording_recovery_20260826144618
status: package_complete_with_partial_acceptance_next_active
package: P6-RR-H
completed_wus: [P6-RR-H-WU-001, P6-RR-H-WU-002, P6-RR-H-WU-003, P6-RR-H-WU-004, P6-RR-H-WU-005, P6-RR-H-WU-006, P6-RR-H-WU-007, P6-RR-H-WU-008]
created_at: 2026-08-26 14:46:18 JST
next_exact_work_unit: P6-RR-I-WU-001
```

## Result

- 固定30秒Deadlineを廃止し、Role／Provider／Hardware ProfileをKeyとする`load / prompt_build / inference / decode / repair_generation / rejudge / cancel_grace`の7 Stage Budget ContractとConfigを追加した。Local Mac値はFrozen Designどおり`configured_not_hardware_verified`であり、実測済みとは表示しない。
- Live JudgeはPrompt、Inference、Decodeを個別BudgetでGateし、RepairはGenerationとRejudgeを別Budgetで判定する。ENFORCEの待ち上限はStage合計から導出し、単一30秒定数を残していない。
- `judge_timeout / malformed_output / provider_unavailable / evaluation_inconclusive / repair_exhausted`のReason CodeとJA／EN文言を分離した。Timeout文言はUser Inputが原因でないことを明示する。
- Repair PromptはQuestion、Previous Answer、Dialogue、Required Evidence、Judge Reasoningだけでなく、Semantic Criterion ID、Disposition、Reason、Evidence Refを`違反Criterionと禁止された誤り`として再注入する。
- Repair RejudgeはMain Generation Serviceと別のExplicit Selected Judge Service／Model Identity／Independence Roleを受け取れる。FixtureでMain Repair Call 1、Selected Selene Rejudge Call 1、Main-selfへの差し戻し0を確認した。Current Web Dedicated ProviderはUnavailableでありReal Rejudgeは行っていない。
- Evidence矛盾、User訂正無視、根拠なき断定、Premise逸脱の4 Golden Caseを固定し、Semantic Criterion Resultsを欠く裸の`accept 0.95`はStrict Decoderが全件Rejectすることを確認した。
- Live Last ResultにStarted／Completed Timestamp、Frozen Mode、Recording Mode、Configured／Active Provider、Budget Profile、Criterion Count、Judge／Repair／Final Outcome、Reason別Localized Message、Selected Rejudge Identityを追加した。Guard ModeはCurrent Hook ContractがTurn-frozen値を持たないため`null`とし、推測値を記録しない。
- Existing Cancel／Deadline／Pending Evidence ArbitrationのRegressionにより、Terminal OwnerがReject／Cancelした後のEvidence／Last Result追記がないことを再確認した。

## Changed Source／Test／Config

- `config/profiles/phase_6_role_stage_budgets.toml`
- `src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py`
- `src/margpa_runtime_llm/modules/evaluation/application/failure_presentation.py`
- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
- `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`
- `tests/unit/evaluation/test_stage_budget_and_failure_presentation.py`
- `tests/unit/evaluation/test_semantic_golden_fail_closed.py`
- `tests/unit/evaluation/fixtures/phase_6_semantic_golden_cases.json`
- `tests/unit/bootstrap/test_judge_live_integration.py`
- `tests/unit/bootstrap/test_repair_live_integration.py`

## Validation

```text
Judge/Repair/Stage Budget/Failure/Golden Focused: 62 passed / exit 0
Scoped Mypy: 4 test/source entry files PASS / exit 0
Scoped Ruff: PASS / exit 0
Seven Stage Config parse/digest/resolve: PASS
Reason JA/EN distinct matrix: PASS
Selected Judge Rejudge identity/service split: PASS with Fixture
Cancel/Deadline/Late Evidence Arbitration: PASS in focused suite
Integrated Backend Full: NOT RUN in Package H
Frontend: NOT RUN in Package H
Real Model: NOT RUN
Browser: NOT RUN
```

Key SHA-512:

```text
Stage budget config:
f67c3c03c709f92d01915c3eea58bb23eb78b1d314a5b87dc464fb85a316555dbb2456ee297e9d84c976b01f33a4d0c2a00e367ebf990accd2df00c1caa47315
Stage budget contract:
860f5bea543446e19c5a1b2fdd43fe670cf95c2265f2a4e971ae3077d27e297b849edba7ad1739836daaf5de15be6c9561aca4db9b5de3bf776130f9364abfaf
Failure presentation:
d3d4e35cf665955c8571b50ed4f6110d560280f8ee9dc69d959ca86cec15bef1ed36928652666fb183f79a6ed215ddb15a0624a8589ddade3da454f06b771592
Repair live integration:
3c527e48da23c822a93f64833147274b311e64e98191b799e631b035e92af6862b863bb70795bf42390c739ede425e6c58f32681504d06f6753cf005d777a2d8
Judge live integration:
4c95d97ce3552e07b1b6b2309c1d7b9d46ccc8a4bb570ab53e2a997598f1ea2ebdbd4770c207f6114737387de78a6fc1aaa6261198bd545eb997e431ad1cac5c
Golden fixture:
0afed48ca39ad6feb4afea0522f7e590ba205109fde43d6305c355c233c92f9df3438241c1f8b9bf6a8e11084f347ca4ded056d3e95d6fa780faca378db4d846
```

## Acceptance／Finding

```text
P6-RR-ACC-027: PASS / Seven Stage BudgetとRole／Provider／Hardware Resolver
P6-RR-ACC-028: PASS / Five Reason CodeとPresentationを分離
P6-RR-ACC-029: PASS by localized presentation unit matrix; Real JA/EN Turn Browser NOT RUN
P6-RR-ACC-030: PASS / JA・EN Timeout文言でUser-blameを明示否定
P6-RR-ACC-031: CURRENT PASS / Four Golden Prompt + bare accept rejection; Real Selene Golden NOT RUN
P6-RR-ACC-032: CURRENT PASS / Explicit Selected Judge Fixture; Real Dedicated Rejudge UNAVAILABLE
P6-RR-ACC-033: CURRENT PASS / Existing Cancel・Deadline・Late Publication Regression; Full Integrated NOT RUN
P6-RR-ACC-034: PARTIAL / Correlation SummaryをBackendに保持; frozen_guard_mode unavailable; UI pending I
P6-RR-ACC-035: Backend Current Request/Historical identity separation exists; UI projection pending I
open_critical: 0
open_major: Real selected Selene Rejudge unavailable; Guard Mode is not present in JudgeCompletionContext
open_non_critical: Stage budgets are configured, not hardware verified
```

## Authority／Incident Inventory

```text
current package root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
historical P6-RR-INC-001 root-outside action: 1 retained
P6-RR-ACC-039: FAIL retained
active_process: 0
loaded_model_by_this_task: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Hardware Budget Verified, Real Dedicated Rejudge PASS, Frozen Guard Mode Captured, Integrated Full PASS, Browser PASS, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-I-WU-001`
