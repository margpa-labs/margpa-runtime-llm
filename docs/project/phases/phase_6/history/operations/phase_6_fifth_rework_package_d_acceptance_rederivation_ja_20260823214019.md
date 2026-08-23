# Phase 6 Fifth Rework Package D — Acceptance 84 ID個別再導出

```yaml
document_id: phase_6_fifth_rework_package_d_acceptance_rederivation_20260823214019
status: append_only_evidence
phase: phase_6
package: package_d
material_boundary: d_2_acceptance_rederivation
role: 設計者兼実装者役
created_at: 2026-08-23 21:40:19 JST
authority: phase_6_codex_controller_package_d_d2_resume_authority_ja_20260823213619.md
baseline: docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md
id_count: 84
phase_closure_state: do_not_close
```

## 1. 判定方法

Frozen Acceptance Matrixの全84 IDをRange表記へ畳まず、一件ずつ再導出した。過去の`CARRIED_FORWARD`またはTest総数だけをPASS根拠にせず、各行にContract固有のSource／Test／実機／Governance Evidenceを割り当てた。

Statusは正本指定の次だけを用いる。

```text
PASS／PARTIAL／NOT_EXECUTED／UNVERIFIED／DEFERRED／NOT_APPLICABLE
```

Evidence Gradeは次の意味を持つ。

```text
G1 DIRECT_CURRENT:
  Current Source／Test、Package A〜Cの変更後EvidenceまたはCurrent Digestへ直接結合。
G2 DIRECT_REAL:
  実Model／実Server／実Browser／実Artifactの記録済みEvidenceへ直接結合。
G3 VERIFIED_PRIOR_UNCHANGED:
  既存の個別Evidenceがあり、Package A〜Cで当該Sourceが変更されていない。
G4 GOVERNANCE_DIRECT:
  Repository内Recovery／Correction／Action InventoryそのものがEvidence。
G5 INCOMPLETE:
  Contractの一部が未検証または文字どおり成立していない。
```

`G2`は記録済み実機Evidenceを示すが、Provider Memoryや会話記憶を正本にしない。参照先はRepository内文書に限定する。

## 2. Evidence Catalog

- `A`: `history/index/phase_6_fifth_rework_package_a_runtime_switch_integrity_ja_20260823202658.md`
- `B`: `history/index/phase_6_fifth_rework_package_b_deepseek_multiturn_ja_20260823205724.md`
- `C`: `history/index/phase_6_fifth_rework_package_c_recording_path_and_regression_repair_ja_20260823210944.md`
- `R2`: `history/operations/phase_6_governance_evidence_correction_ja_20260823105500.md`
- `R3`: `history/operations/phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md`および同Addendum `20260823184500.md`
- `R4`: `history/operations/phase_6_fourth_rework_acceptance_rederivation_ja_20260823181750.md`
- `CAL`: `history/operations/phase_6_calibration_harness_results_ja_20260823180000.md`
- `RJ`: `history/index/phase_6_d_wu005_real_local_judge_experiment_ja_20260823023000.md`
- `RB`: `history/index/phase_6_i_wu003_real_browser_golden_path_ja_20260823025500.md`、`history/index/phase_6_third_rework_step_6_ui_state_and_real_hardware_ja_20260823174000.md`
- `BASE`: `history/index/phase_6_h_wu001_002_qwen_baseline_experiment_ja_20260823024000.md`
- `QNT`: `history/operations/phase_6_deepseek_quantization_controller_acceptance_ja_20260823142711.md`
- `GOV`: P6-GOV-002〜008のAppend-only Corrections、Package D Recovery群およびD-2 Second Resume Authority。

Catalog Keyだけでなく、各行へ主要Current Test／Source Pathを併記する。

## 3. Model／Runtime Control（14 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-001 | PASS | `RB`; `config/models/qwen3_4b_q4_k_m.toml`; `tests/integration/llama_cpp/test_phase1b_runtime.py` | G2 | Startup Default Qwen実Load済み。C後の実Qwen TestもPASS。D-4回帰対象。 |
| P6-ACC-002 | PASS | `QNT`; DeepSeek Manifest／Completion Evidence | G2 | Canonical→Q8_0→Q4_K_MのDigest／Recipe／SizeがController独立照合済み。Artifact変更0。 |
| P6-ACC-003 | PASS | Current Model Registry／Config; `tests/integration/web/test_runtime_model_control_public_basic_call0.py` | G1 | V4 FlashをLocal Runtimeへ登録・Load・Callする経路0。Current Cycle接触0。 |
| P6-ACC-004 | PARTIAL | `R4`の実Qwen→DeepSeek→Qwen; `A`のSwitch Lease／Binding変更 | G5 | Round-trip実Evidence後にAがSwitch Transactionを変更した。D-3で変更後の実Round-tripを再検証する。 |
| P6-ACC-005 | PASS | `A`; `tests/unit/inference/test_model_access_coordinator.py`; `tests/integration/test_runtime_model_control_smoke.py` | G1 | Main／Background／Switch Lease競合時にUnload／Load／Mutation 0。D-4 Focused再実行対象。 |
| P6-ACC-006 | PASS | `A`; `tests/unit/runtime_model_control/test_runtime_model_controller.py` | G1 | Load失敗RollbackとDouble Failure Fail-closedを変更後Testが直接確認。 |
| P6-ACC-007 | PARTIAL | `B` Multi-turn; `R4` Persistent Conversation保持; persistent／citation／branch Test群 | G5 | A/B変更後のConversation継続は実Modelで成立。一つのD-3 Browser Matrix内でCitation／Branch／Switch後維持を再確認する。 |
| P6-ACC-008 | PASS | `A`; `R3`; `tests/unit/conversation/test_conversation_generation_attempt_provenance.py`; `tests/unit/conversation/test_persistent_attempt_provenance.py` | G1 | Target Handle由来MAIN Binding、Model／Artifact／Backend／Config DigestのTurn永続化がCurrent Testへ結合。 |
| P6-ACC-009 | PARTIAL | `A`; `R4`; `tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py` | G5 | Transaction／Capability Limit TestはPASS。A変更後の同一Model実Context ReloadはD-3必須。 |
| P6-ACC-010 | PASS | `tests/unit/runtime_model_control/test_runtime_model_controller.py`; `tests/integration/web/test_runtime_model_control_mutation_routes.py` | G1 | Reload失敗時にRequested ContextをCurrent化せず旧Snapshot／Binding維持。 |
| P6-ACC-011 | PASS | `R4`; `tests/unit/conversation/test_conversation_generation_runtime_snapshot.py`; `tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py` | G2 | 実BrowserでMax New Tokens=5の次Generation反映とReload 0を確認、Ceiling Testも存在。A〜C影響なし。 |
| P6-ACC-012 | PASS | `tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py`; mutation route Token Boundary Test | G1 | Prompt込みLimit超過はTyped拒否、Backend非接触。Silent Clampを上限超過処理に使用しない。 |
| P6-ACC-012A | PASS | `QNT`; Exact Model Authority Receipts; Current `models` Logical／Resolved配置 | G2 | Logical Symlink／Resolved Targetと許可Scope一致。Model Artifact Mutation 0。 |
| P6-ACC-012B | PASS | Package A〜C Action Inventory; `B`／`QNT`のExact Artifact Inventory | G4 | Sibling Model／未指定Subtree Mutation 0。D-3は許可済みQwen／DeepSeek Read／Loadだけ。 |

## 4. Evaluation／Judge（13 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-013 | PASS | `tests/unit/evaluation/test_evaluation_domain.py`; `test_evaluation_orchestrator.py` | G3 | Dataset／Case／Criteria／Ground Truth／Run／Resultを別Typed Domainで保持。A〜C影響なし。 |
| P6-ACC-014 | PASS | `tests/unit/evaluation/fixtures_loader.py`; `test_baseline_verification.py` | G3 | Ground Truth Revision／Digest／Source追跡あり。Fixture変更なし。 |
| P6-ACC-015 | PASS | `tests/unit/evaluation/test_deterministic_evaluators.py`; `BASE` | G2 | Deterministic EvaluatorのModel Call 0、実Qwen回答6件への適用を分離記録。 |
| P6-ACC-016 | PASS | `R3`; `tests/unit/bootstrap/test_judge_live_integration.py` | G3 | Judge OFFはPrompt／Case／Model Call／追加Mutation 0、Typed skippedだけ。 |
| P6-ACC-017 | PASS | `R2`; `RB`; SSE／Store Spy Test | G2 | OBSERVE後もCanonical Answer不変、Judge Resultは別State／Evidence。AのCoordinator変更は競合を強化。 |
| P6-ACC-018 | PASS | `tests/unit/evaluation/test_judge_role_resolver.py`; `test_judge_mode_controller.py`; `test_judge_live_integration.py` | G3 | Judge Recommendationは直接Authorityを作らず、Repair Eligibility／Policy Resolverを経由。 |
| P6-ACC-019 | PASS | `R3`; `tests/unit/evaluation/test_judge_prompt_and_decoder.py`; malformed／timeout Test | G3 | Typed Decode、Unknown／例外はfailedへFail-closed。 |
| P6-ACC-020 | PASS | `RJ`; `R3`; Judge Evidence `judge_role=main_self` | G2 | Same ArtifactをIndependentと表示せずMAIN_SELFで一貫。 |
| P6-ACC-021 | PASS | `R3`; `CAL`; Judge Evidence Recorder Test | G2 | Prompt／Rubric／Model／Seed状態／Config Digestを追跡。Unpinned Seedはfalseとして記録し捏造0。 |
| P6-ACC-022 | PASS | `CAL` | G2 | Position、Verbosity、Language、Self-preferenceを実Qwen 20 CallでBounded比較。独立Judge／第三者Corpus VariantはPhase 7+へ明示DEFERREDだが、本IDの4次元は実行済み。 |
| P6-ACC-023 | PASS | `RJ`; `RB`; `tests/integration/test_real_local_judge_smoke.py` | G2 | 少なくとも一つを超える実Local LLM Judge Run成立。 |
| P6-ACC-024 | PASS | Cross-phase Conflict Test; Guardrail／Governance Post Hook Resolver | G3 | Judge ResultだけでSafety／Authority Deny解除0。 |
| P6-ACC-024A | PASS | Registry／Projection Tests; `tests/unit/runtime_observability/test_component_identity_projection.py` | G3 | Selene候補未Load時にCurrent／Availableを捏造せずNone／Unavailableへ投影。 |

## 5. Repair（10 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-025 | PASS | `tests/unit/repair/test_repair_mode_controller.py`; Configuration Matrix | G3 | Judge／Repair Mode独立、Default OFF。 |
| P6-ACC-026 | PASS | `R2`; `tests/unit/bootstrap/test_judge_live_integration.py` | G3 | OBSERVEではEligibility表示を維持してもExecutor／追加Generation 0。 |
| P6-ACC-027 | PASS | `R3`; `tests/unit/bootstrap/test_repair_live_integration.py`; `tests/unit/repair/test_state_machine_and_budget.py` | G3 | ENFORCEはRegistry／Authority／実行前後Budget内だけ。 |
| P6-ACC-028 | PASS | `tests/unit/repair/test_repair_domain.py`; persistent attempt provenance Test | G3 | Original／Repair AttemptのID、Role、Provenanceを別Identityとして保存。 |
| P6-ACC-029 | PASS | `R3`; governance／guardrail hook fault Tests | G3 | CandidateはPhase 4／5 Post Pointを再通過し、Hook例外もFail-closed。 |
| P6-ACC-030 | PASS | `R4`; repair budget／exhaustion Tests | G3 | Attempt／Wall Time／Token／Call／Depthを実行前後で有界化。 |
| P6-ACC-031 | PASS | `tests/unit/repair/test_repair_success_evaluator.py`; `test_repair_live_integration.py` | G3 | Before／Afterを同Criteria／Evaluatorで比較。 |
| P6-ACC-032 | PASS | Repair Negative Matrix | G3 | Worse／Unknown／FailureをImprovedへ昇格しない。 |
| P6-ACC-033 | PASS | `R3`; persistence failure chain Tests | G3 | start／complete永続化失敗時にFAILEDへ補償し、Ghost／Double Terminal 0。 |
| P6-ACC-034 | PASS | Recording／Storage Security Tests | G3 | Hidden Originalを通常Presented Turnとして保存せず、Attempt／Security境界に限定。 |

## 6. Observability／Presentation（9 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-035 | PASS | `R3`; requestId相関Frontend／Backend Tests; `RB` | G2 | Request／Turn／Generation／Judge／Repair／Recordingをrequest_idで相関。Reload後も復元。 |
| P6-ACC-036 | PASS | `R3`; sequential request／Feature Modes Tests | G3 | OFF／Busy SkipでもCurrent request_id更新、過去結果混在0。 |
| P6-ACC-037 | PASS | `R3`; Reject-before-model／Feature Modes projection Tests | G3 | 未実行Pointをqueued_or_skipped等Typed Stateで表示。 |
| P6-ACC-038 | PASS | `R3` Addendum; `R4`; terminal state／concurrency Tests | G3 | Terminal一意とFull Vocabulary成立。AのSwitch Leaseは競合境界を強化。 |
| P6-ACC-039 | PASS | Recording／Judge subscriber failure Tests; `C` | G1 | Subscriber／Writer Failureはdegradedへ投影しCanonical成功を捏造・破壊しない。 |
| P6-ACC-040 | PASS | Guardrail reject inference Spy; `RB` | G2 | Pre-model RejectでMain／Judge Call 0。 |
| P6-ACC-041 | PASS | Safe refusal Unit／Frontend Tests; `RB` | G2 | Raw Codeではなく固定JA／EN表示。 |
| P6-ACC-042 | PASS | Persistent Projection Tests | G3 | Safe RefusalはClient ProjectionでありAssistant Turn／Authority／次Contextに混入0。 |
| P6-ACC-043 | PASS | `frontend/src/lib/persistentDetailProjection.test.ts`; persistent web Tests; `RB` | G2 | Reload／Resume後にfailure_reason_codeから安全表示を再構築。 |

## 7. Feedback／Recording（9 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-044 | PASS | `tests/unit/runtime_observability/test_feedback.py`; Call Spy | G3 | FeedbackはPolicy／Authority／Training Mutationを生成しない。 |
| P6-ACC-044A | PASS | Feedback Action Spy | G3 | RatingのみでRetry／Regenerate／Repair自動実行0。 |
| P6-ACC-045 | PASS | `tests/unit/conversation/test_conversation_recording_contract.py`; recording mode Tests | G3 | OFFでEnvelope Build／Hook Call／Write 0。 |
| P6-ACC-046 | PASS | `tests/unit/runtime_observability/test_recording.py`; Schema／Storage Tests | G3 | METADATAはAllowlist Fieldだけ。 |
| P6-ACC-047 | PASS | SafeRecordingEnvelope Positive／Negative Matrix | G3 | FULLはCanonical Input／Presented Answerだけを許可。 |
| P6-ACC-048 | PASS | Recording Security Scan／`extra=forbid` Tests | G3 | Thinking／System／Secret／Tool／RAG Internal／Hidden／Partial保存0。 |
| P6-ACC-049 | PASS | `C`; `tests/unit/runtime_observability/test_local_filesystem_recording_writer.py` 35 Tests | G1 | dir_fd／O_NOFOLLOW、Atomic Rename、Quota、Failure、Degraded、TOCTOU Fault Injectionが変更後PASS。D-4再実行対象。 |
| P6-ACC-050 | PASS | `C` Action Inventory; pytest `tmp_path`／Project-local scratch discipline | G4 | User実`runtime_data` Read／Write 0。D-3/D-4でも0を維持する。 |
| P6-ACC-051 | PASS | `.gitignore`;既存Git Boundary Evidence | G3 | Private Evaluation／Feedback／Task-local EvidenceはIgnore対象。新CycleはGitへ接触せず、D-4でもGitを使って再検証しない。 |

## 8. UI／Identity（12 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-052 | PASS | `RB`; runtime status API／Browser Evidence | G2 | Sidebar Current Main Modelと実Runtime一致。A変更後はD-3 Switch Matrixで再照合。 |
| P6-ACC-053 | PASS | Component Identity Projection Tests; `RB` | G2 | Main／Guard／Judge／Governance Layerを別Field／Row表示。 |
| P6-ACC-054 | PASS | Component Identity State Matrix | G3 | Guard Model NoneとGuardrail Modeは独立入力・独立Projection。 |
| P6-ACC-055 | PASS | `A`; runtime governance binding／identity Tests | G1 | Manifest／Digest／Live BindingからGovernance Layer導出。Switch Commit後Rebindを追加済み。 |
| P6-ACC-056 | PASS | `R3` Addendum; `tests/unit/runtime_observability/test_component_identity_projection.py` | G3 | 実到達可能13 State組を網羅し、到達不能状態を捏造しない。 |
| P6-ACC-057 | PASS | `R4`; status API／Browser Evidence | G2 | Context／Max TokensのCurrent／Limit／Sourceを表示。D-3 Context Reloadで再照合。 |
| P6-ACC-058 | PARTIAL | `RB`; Frontend state Tests | G5 | Settings再Open／Reloadは実Browser済み。別Tab同期がRepository Evidence上未検証。D-3で実Browser確認する。 |
| P6-ACC-059 | PASS | DOM／Translation Tests | G3 | Main Runtime Governance／Guardrail Governance LabelからPhase Suffix除去。 |
| P6-ACC-060 | PASS | Translation String Review／Frontend Tests | G3 | 将来利用者向けLabelへPhase Suffix 0。 |
| P6-ACC-061 | PASS | Phase 3 Panel／Backend Regression Tests | G3 | Panel整理後も内部Definition基盤回帰0。 |
| P6-ACC-062 | PASS | DOM／API Call Spy; Governance Layer Projection Tests | G3 | Phase 6でCurrent Constitution Layerを捏造しない。 |
| P6-ACC-063 | PASS | Response DTO `extra=forbid`; Projection Security Tests | G3 | Path／Secret／Raw Definition／Prompt露出0。 |

## 9. Compatibility／Experiment（9 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-064 | PASS | Persistent／Ephemeral／v1／v2 Web Integration Tests | G3 | A〜Cの変更対象外。D-4 Fullで再実行する。 |
| P6-ACC-065 | PASS | Documentation RAG Conversation／Citation Integration Tests | G3 | TOOL Role／Citation／Restart互換をProject-local Testで確認。D-3 Browser再照合対象。 |
| P6-ACC-066 | PASS | Phase 6 Docs／Experiment Review | G4 | RAG最終品質判定をPhase 7前に主張していない。 |
| P6-ACC-067 | PASS | Persistent Conversation Actions／Web Integration Matrix | G3 | Stop／Retry／Regenerate／Branch／Resume回帰Testあり。BのChat Template変更後はD-3 Matrixで代表経路を再照合。 |
| P6-ACC-068 | PASS | Public／Basic Call-0 Routes／DOM Tests | G3 | Public／BasicでControl／Judge／Repair／Record Call 0。A後Full SuiteもPASS。 |
| P6-ACC-069 | PASS | `CAL`; `scripts/models/phase_6_calibration_harness.py` | G2 | Qwen OFF／OBSERVE／ENFORCE比較のDataset／Model／Mode／Digest／Resultが再現可能。統計的一般化は主張しない。 |
| P6-ACC-070 | PASS | `QNT`; `B`; Model Definition／Capability Evidence | G2 | DeepSeek Q4_K_MをSupportedとして実Load／Multi-turn、V4は非Local Callとして正確分岐。 |
| P6-ACC-071 | PASS | `CAL` | G2 | Token 1024／Latency約29.4s／Call 20／Repair 0／Recording 3000 bytesを別Fieldで計測。 |
| P6-ACC-072 | PASS | `BASE`; Calibration Result Schema | G2 | 実False Negativeを0へ捏造せず、unknown／unavailableを明示。 |

## 10. Automation／Governance（8 ID）

| ID | Status | Evidence Source | Grade | Current Impact／Package A〜C再評価 |
|---|---|---|---|---|
| P6-ACC-073 | PASS | Package 0〜D Recovery Chain、Compaction後のRepository再構成 | G4 | Repository正本だけでCurrent Position／Next Actionを復元できた。 |
| P6-ACC-074 | PASS | Provider利用制限停止Recovery `20260823212427`、Codex Resume／Second Resume Authority | G4 | Quota停止後にPackage Dだけを別Provider Taskへ差分再開。A〜C再実行0。 |
| P6-ACC-075 | PASS | Package A〜D Timeline／Material Boundary Recovery | G4 | 通常境界報告では停止せず、真のStop Conditionだけで停止・再開した。 |
| P6-ACC-076 | PASS | Fifth Review Findings、P6-GOV-007／008、P6-CODEX-042 Recovery | G4 | False Completion、Rework、Incident、Human／Controller Gateを別分類し、Action 0捏造を訂正。 |
| P6-ACC-077 | PARTIAL | P6-GOV-001〜008、P6-CODEX-042、D-2 Second Resume Authority | G5 | Contractの「違反0」はPhase 6累積で文字どおり成立しない。既知Incidentを0へ改変しない。Technical Acceptanceへの現在影響はNONEだが、Authority Compliance／Phase ClosureはController判定待ち。 |
| P6-ACC-077A | PASS | Activation／Audit Review; Exact Model Authorities | G4 | 過去Download例外をPhase 6の無制限Authorityへ再利用0。各LoadはExact Model Authorityへ結合。 |
| P6-ACC-078 | PASS | P6-GOV-002〜008および本書 | G4 | Stable直書き0。Correction／Rederivation／Recoveryは全て新規Append-only。 |
| P6-ACC-079 | PASS | Package A／B-pre／B／C／D-1／D-2 Recovery Inventory | G4 | Material Boundary単位に限定。Per-command／Per-test Evidence濫造0。 |

## 11. Count／Open Result

```text
Total ID         : 84
PASS             : 79
PARTIAL          : 5
NOT_EXECUTED     : 0
UNVERIFIED       : 0
DEFERRED         : 0
NOT_APPLICABLE   : 0

PARTIAL:
  P6-ACC-004  Package A後の実Qwen→DeepSeek→Qwen再検証待ち
  P6-ACC-007  Switch後Conversation／Citation／Branch Browser再検証待ち
  P6-ACC-009  Package A後の同一Model実Context Reload待ち
  P6-ACC-058  別Tab同期の実Browser確認待ち
  P6-ACC-077  Phase 6累積Unauthorized Incidentが0ではない
```

P6-ACC-004／007／009／058はD-3で実行可能なTechnical Evidence Gapである。P6-ACC-077は技術Gapではなく、Historical Authority Complianceの文字どおりの不成立であり、Controller Authorityに従ってTechnical Completionと分離する。

## 12. D-3／D-4へのTransition

- D-3前にPre-run Recovery Entryを作成する。
- D-3は同一Model Context Reload、Qwen→DeepSeek→Qwen、DeepSeek Multi-turn、Conversation／Citation／Branch、別Tab同期、Judge／Repair／Recording／Runtime State、Identity／Binding／Attempt Evidence、Rollback／Busy／ConflictをProject Root内で確認する。
- Package BのDeepSeek Multi-turnは`chat_template.py`がB後未変更であるため再利用可能だが、A後のRuntime Switch／Browser Matrixとの結合はD-3で確認する。
- D-4でBackend Full、Focused Fault、Static、Frontendを実行し、Source変更がなくても全84判定を最終照合する。
- P6-ACC-077を理由なくPASSへ昇格しない。Complete Candidate可否は、元Handoffの「Required PARTIAL 0」とSecond Resume AuthorityのTechnical／Authority分離を両方明示したうえで最終判定する。

