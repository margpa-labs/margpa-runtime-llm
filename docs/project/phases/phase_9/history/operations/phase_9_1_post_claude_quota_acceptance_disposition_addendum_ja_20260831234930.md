# Phase 9-1 Post-Claude Quota Acceptance Disposition Addendum

```yaml
document_id: phase_9_1_post_claude_quota_acceptance_disposition_addendum_20260831234930
document_state: complete_candidate_evidence_addendum
language: ja
created_at: 2026-08-31T23:49:30+09:00
phase: phase_9
program: phase_9_1
authority: phase_9_codex_designer_implementer_p9_1_post_claude_quota_continuation
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
```

## 1. Disposition Policy

Current Working TreeとPackage Recovery、Controller確認済みFocused Evidenceを正本とする。Fixture-backed Production Wiringは、それが証明するSource／Composition範囲に限ってPASSとする。Project Root外Real Artifact InferenceとUser実画面はPASSへ昇格しない。

Disposition語彙：`PASS`、`RESOURCE_GATED / NOT RUN`、`USER MANUAL GATE / NOT RUN`。本再導出で`PARTIAL`／`FAIL`は0件である。Gateは未実施を隠すものではなく、Complete Candidate後にUser Authority／ManualでDispositionする境界である。

## 2. Evidence Catalog

- `A-R`: `docs/project/phases/phase_9/history/index/phase_9_1_p9_1_a_dedicated_runtime_recovery_ja_20260831231500.md`
- `B-R`: `docs/project/phases/phase_9/history/index/phase_9_1_p9_1_b_semantic_109_recovery_ja_20260901010000.md`
- `C-R`: `docs/project/phases/phase_9/history/index/phase_9_1_p9_1_c_judge_repair_rejudge_enforce_recovery_ja_20260901020000.md`
- `D-R`: `docs/project/phases/phase_9/history/index/phase_9_1_p9_1_d_integration_review_recovery_ja_20260901033000.md`
- `AUTH-SRC`: `src/margpa_runtime_llm/entrypoints/web/main.py::_dedicated_model_authority_enabled`、`src/margpa_runtime_llm/bootstrap/web_application.py::build_phase1_web_runtime`
- `AUTH-TEST`: `tests/unit/web/test_web_cli.py::test_dedicated_model_authority_opt_in_is_passed_only_for_local_runtime`、`::test_web_runtime_wires_dedicated_model_authority_opt_in_into_the_role_provider_factory`
- `DEDICATED-TEST`: `tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py`
- `SEMANTIC-TEST`: `tests/unit/runtime_governance/test_semantic_runtime.py`
- `DISPATCH-TEST`: `tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py`
- `REPAIR-SRC`: `src/margpa_runtime_llm/bootstrap/repair_live_integration.py::attempt_live_repair`
- `MANUAL`: `docs/project/phases/phase_9/history/operations/phase_9_1_corrected_user_manual_recheck_sheet_ja_20260831234930.md`

## 3. P9-ACC-001〜038 Individual Matrix

| ID | Disposition | Evidence Pointer | 短い根拠 |
|---|---|---|---|
| P9-ACC-001 | PASS | `D-R` §3、Exact Continuation §3〜4 | Current TreeをCanonicalとして保持し、Phase 6〜8成立SourceのRollback／再実装0。 |
| P9-ACC-002 | PASS | `docs/project/phases/phase_9/phase_index_ja.md` §5、Exact Continuation §1／§7 | Current Source Priorityを維持し、P9-2／P9-3へ未進入。 |
| P9-ACC-003 | PASS | `B-R` §1〜3、`SEMANTIC-TEST::test_provider_short_result_becomes_typed_unknown_not_pass` | NOT_APPLICABLE／UNKNOWN／DEFERRED／FAILEDをTypedに分離し、虚偽PASS 0。 |
| P9-ACC-004 | PASS | `A-R` §2〜3、`src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py` | Provider／Path／BackendはRegistry・Definition・Port境界から注入され、Core hard-code追加0。 |
| P9-ACC-005 | PASS | Exact Continuation §7、本Addendum／Return | P9-1 Return前後にP9-2／P9-3実装0。 |
| P9-ACC-006 | PASS | `A-R` §2／§4／§5、`DEDICATED-TEST` | Artifact／Manifest／Digest／Backend／Capability Probe／Authority PreflightをFixture境界でEvidence化。Real inferenceは別Gate。 |
| P9-ACC-007 | PASS | `DEDICATED-TEST::test_selene_authority_granted_preflight_load_and_evaluate_wire_correctly`、`::test_selene_role_adapter_composes_with_the_real_lifecycle_manager` | Selene Candidate Preflight／Load／Strict Semantic Evaluator／Executed Provider seamをProduction Factory経由で証明。 |
| P9-ACC-008 | RESOURCE_GATED / NOT RUN | `A-R` WU-005／§5 | Project Root外Real Selene Artifact Authorityなし。Fixture PASSをReal Inference PASSへ昇格しない。 |
| P9-ACC-009 | PASS | `DISPATCH-TEST::test_selene_dispatch_unavailable_response_produces_typed_failure`、`A-R` §2 | Malformed／Unavailable等はStrict Typed FailureへFail-closed収束。 |
| P9-ACC-010 | PASS | `DEDICATED-TEST::test_qwen3guard_authority_granted_preflight_load_and_classify_wire_correctly`、`A-R` WU-003 | Qwen3Guard Candidate Load／Target Contract／Executed Provider seamをProduction Factory経由で証明。 |
| P9-ACC-011 | RESOURCE_GATED / NOT RUN | `A-R` WU-005／§5 | Project Root外Real Qwen3Guard Artifact Authorityなし。Real Inference未実施。 |
| P9-ACC-012 | PASS | `A-R` WU-003、`DEDICATED-TEST::test_qwen3guard_authority_granted_preflight_load_and_classify_wire_correctly` | Input／Output target、line contract、category／refusal、Provider Evidence IdentityをFixtureで照合。 |
| P9-ACC-013 | PASS | `AUTH-SRC`、`AUTH-TEST`、`A-R` WU-004 | Authority default False。FlagだけではPreflight／Loadせず、Startup Mode OFFのDedicated Call／resident Load 0。 |
| P9-ACC-014 | PASS | `DEDICATED-TEST::test_selene_role_adapter_composes_with_the_real_lifecycle_manager`、`A-R` WU-004 | Mode ON Atomic Commit、Turn Lease、Mode OFF UnloadをProduction Adapter＋Lifecycle合成で証明。 |
| P9-ACC-015 | PASS | `DISPATCH-TEST::test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_provider`、`::test_selene_shaped_active_adapter_dispatches_via_semantic_evaluator_never_touches_main_service` | Configured／Active／Executed／Evidence ProviderとJudge Roleを分離・一致させる。 |
| P9-ACC-016 | PASS | `C-R` §2、`tests/unit/bootstrap/test_judge_live_integration.py` stage deadline tests | Model Call 0／1以上、Stage、Latency、Budget、Failure ReasonをFixture Test／typed resultで確認可能。 |
| P9-ACC-017 | PASS | `B-R` §1、canonical 109 compile test | ARGD 53＋DAGD 56＝109をDefinition／Point／Capability／Criterion Type別に機械Inventory化。 |
| P9-ACC-018 | PASS | `B-R` §1〜2、semantic criterion adapter compile test | Normalized Descriptorから109 Semantic Criterionへ109／109変換、Unsupported／Silent Drop 0。 |
| P9-ACC-019 | PASS | `DISPATCH-TEST::test_main_shared_active_adapter_genuinely_evaluates_semantic_criteria`、`SEMANTIC-TEST::test_live_turn_covers_all_109_criteria_with_selected_and_budget_deferred_counts` | Main-sharedで実評価、Built-inでnot_applicable、Budget超過でdeferredへRule単位分離。一律Deferredではない。 |
| P9-ACC-020 | PASS | `B-R` §1／§3、built-in semantic judge tests | Built-in対応集合は空集合。109件をNOT_APPLICABLEにし、質的Criterionの虚偽PASS／Model Call 0。 |
| P9-ACC-021 | PASS | `SEMANTIC-TEST::test_live_turn_covers_all_109_criteria_with_selected_and_budget_deferred_counts`、`B-R` WU-004 | selected／evaluated／pass／deviation／unknown／not_applicable／deferredの総和整合をTest。 |
| P9-ACC-022 | PASS | `B-R` WU-004、`SEMANTIC-TEST` evidence assertions | Criterion ID／Descriptor／Rule revision source／Point／Outcome／Reason／Evidence refsをLossless record。 |
| P9-ACC-023 | PASS | `DISPATCH-TEST` Main-shared／Selene dispatch tests | Main Self=`main_self`、Selene=`independent_artifact`をProvider／Evidenceで区別。 |
| P9-ACC-024 | PASS | `C-R` WU-001／WU-005、judge strict decoder tests | accept／needs_repair／unsupported／malformed／timeout／cancelledをStrict DecodeしFail-closed。 |
| P9-ACC-025 | PASS | `DISPATCH-TEST::test_main_shared_judge_repair_and_rejudge_genuinely_execute_via_the_production_repair_composition`、`REPAIR-SRC` | Material DeviationからEligibility／bounded prompt／Candidate GenerationへProduction compositionで到達。 |
| P9-ACC-026 | PASS | 同上Testの`:judge`→`:repair`→`:rejudge` call列 | Repair Candidateを別request identityでRejudgeし、同じFrozen Main-shared Providerを再利用。 |
| P9-ACC-027 | PASS | 同上Test、`C-R` WU-003／WU-005 | Adopt／Reject／Safe Fallback／Failureをtyped final resultとpresented contentへ収束。 |
| P9-ACC-028 | PASS | `SEMANTIC-TEST::test_enforce_deviation_never_executes_repair_when_repair_authority_is_off` | ENFORCEはsupported actionだけを実行し、Repair OFF時にAuthorityを追加しない。 |
| P9-ACC-029 | PASS | `SEMANTIC-TEST` conflict tests、stage budget／repair budget tests、`C-R` | Conflict priority、max repair、deadline、budgetを有界化しLoopなし。 |
| P9-ACC-030 | PASS | `C-R` WU-005列挙のCancel／Deadline／Late publication tests | Cancel／Deadline／OFF／Shutdown後のLate resultをCurrentへ追加しない。 |
| P9-ACC-031 | PASS | `C-R` WU-006、`DISPATCH-TEST` production repair composition | Request ID suffixとFrozen identityでCriterion／Judge／Repair／Rejudge／Final／Recordingを相関。 |
| P9-ACC-032 | PASS | `D-R` Full Suite、feature mode current/historical regression | OFF TurnのCurrent実行なしとHistorical Last Resultを分離。 |
| P9-ACC-033 | PASS | `D-R` §1 `2200 passed, 7 deselected` | Chat／Persistence／Reload／Restart／別Tabを含むCanonical BackendにMaterial Regressionなし。 |
| P9-ACC-034 | PASS | `D-R` §1 | Local RAG／Citation／Manual URL／Dev Agent既存Coverageを含むFull Suite PASS。変更0。 |
| P9-ACC-035 | PASS | `D-R` §1、Exact Continuation §4 | Full 2200 PASS、Mypy 346＋212 clean、Ruff cleanに加えController Focused 62 PASS／対象Mypy・Ruff clean。Frontend無変更。 |
| P9-ACC-036 | PASS | Post-Claude Recovery §6、Corrected Manual §9 | Cycle 1（Requirement／Evidence／Count）とCycle 2（Negative／Gate／Claim／操作順）を実施し、Critical／Major／MVP Blocker 0。 |
| P9-ACC-037 | USER MANUAL GATE / NOT RUN | `MANUAL` | Dedicated Role、Semantic Counts、Judge／Repair／Rejudge、ENFORCE、OFF／Stopの正順Manualを確定。User実画面は未実施。 |
| P9-ACC-038 | PASS | `docs/project/phases/phase_9/phase_index_ja.md`、Post-Claude Exact Return | ClaimをComplete Candidateに制限し、Closure／P9-2／Gitを自己承認しない。 |

## 4. Mechanical Count

Expected row count: `38`。

```text
PASS: 35
RESOURCE_GATED / NOT RUN: 2
USER MANUAL GATE / NOT RUN: 1
PARTIAL: 0
FAIL: 0
TOTAL: 38
```

機械検算は本Matrixの`| P9-ACC-NNN |`行だけを抽出し、行数38、Unique ID 38、最小001、最大038、欠番0、重複0を確認する。

## 5. Maximum Claim

`P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION`。Phase 9-1 Closure、P9-2開始、Real Artifact PASS、User Manual PASSは主張しない。
