# MARGPA Runtime LLM 現行未解決課題Registry

```yaml
document_id: current_unresolved_findings_registry
document_type: shared_stable_current_unresolved_findings_source
document_state: current
language: ja
created_at: 2026-08-29 10:51:39 JST
last_reclassified_at: 2026-09-02 10:32:28 JST
decision_authority: user
authority_owner: Nazuna Research
maintainer_role: プロジェクト責任者兼設計統括者役
current_project_stage: individual_poc_mvp_portfolio
current_delivery_target: phase_9_mvp_then_phase_10_portable_autonomous_development_governance_package
history_snapshot: ../history/未解決/phase_9_1_all_judge_operational_failure_and_rework_order_snapshot_ja_20260902103228.md
```

## 1. 本書の役割

本書は、今すぐ修正しないFindingを隠蔽せず、かつ全件を現在PhaseのClosure Blockerにしないための現行正本である。

各Findingは、技術的重大度、現在の優先度、影響範囲、延期先、再開条件およびClosure Blockerかを分離して管理する。

本書へ記録されたことは、次のいずれも意味しない。

- 問題が解決済みである。
- 問題が存在しない。
- 現在Phaseで必ず直す。
- 将来も直さない。

## 2. Current Decision Premise

```text
Project: Nazuna Research一人によるPoC／MVP／就職Portfolio
Resource: 金銭、AI利用可能量、時間、Hardwareとも強い制約あり
Current Priority: Phase 9までのMVP成立
Next Priority: Phase 10冒頭のPortable Autonomous Development Governance Package
Default: 主経路を止めないHardening／UI Polishは延期可能
```

判断正本：

`docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`

## 3. Priority／Closure定義

| Priority | 意味 | Phase Closure |
|---|---|---|
| P0 | 現Phaseの中心機能、User主経路、Data／Safety、次Phase土台を壊す | 原則Block |
| P1 | 近接Phaseで直す価値が高いが、回避可能または主経路は成立 | 原則Blockしない |
| P2 | Phase 9／10のUI、Observability、Hardeningへ延期可能 | Blockしない |
| P3 | Product化、Cloud、Server、企業利用等の条件成立後 | Blockしない |

## 4. Phase 6 — Currentまたは直近解決済みClosure Blockers

### UF-P6-001 — Mode OFF／Provider切替後の新規Role Lease拒否

```yaml
source_finding: P6-CODEX-089
status: resolved_R26_controller_bounded_review_pass
severity: major
priority: resolved_former_P0
closure_blocker: false_covered_by_final_user_manual_gate
impact_scope: Judge_Guard_role_provider_lifecycle
deferral_target: none_current_phase
reopen_condition: OFF_or_pending_unload_state_can_still_start_new_role_turn
```

Mode OFF、Provider切替、DrainまたはUnload待ちの状態でも新しいLeaseを発行できる場合、画面上のMode／Provider状態と実実行が一致しない。研究結果の誤認とUnload競合を起こすためPhase 6で閉じる。

Acceptance条件：OFF／Degraded／Pending Unload／Failed Adapterでは新規実行を拒否し、既存Turnだけが有界にDrainする。

R26 SourceおよびFocused Testで成立し、2026-08-29のController Bounded ReviewでPASS。実Browser上の最終確認はUF-P6-005へ統合する。

### UF-P6-002 — Selene／Qwen3GuardのConfigured／Active／Executed一致

```yaml
source_findings:
  - P6-CODEX-046
  - P6-CODEX-048
  - P6-CODEX-062_to_068
status: known_user_manual_fail_deferred_by_user_override
severity: major
priority: P1_new_phase_10_reserved
closure_blocker: false_by_explicit_user_override
impact_scope: dedicated_judge_and_guard_provider_runtime
deferral_target: new_phase_10_governance_semantic_runtime_completion
reopen_condition: new_phase_10_entry_or_configured_provider_is_reported_or_used_without_matching_active_and_executed_provider
```

Selene／Qwen3Guardを選択した時、実際にLoad／Inferenceされるか、利用不能ならModeを有効化せずExact Failureへ収束する必要がある。`Active none`のままConfigured名をExecuted Evidenceへ記録してはならない。

Real Artifact品質の高度評価は延期可能だが、Selene／Qwen3Guardを実際に使えるようにすることはPhase 6の中心機能である。2026-08-29 User Manualでは両方とも`Active none`で、Source上は`dedicated_model_authority_granted=False`固定によりLoad前に拒否されていた。正直な失敗表示だけではAcceptanceを満たさない。

### UF-P6-003 — ARGD／DAGD Semantic 109件のLive Turn実評価

```yaml
source_findings:
  - P6-GOV-015
  - P6-CODEX-057
status: known_user_manual_fail_deferred_by_user_override
severity: major
priority: P1_new_phase_10_reserved
closure_blocker: false_by_explicit_user_override
impact_scope: main_runtime_governance_semantic_evaluation
deferral_target: new_phase_10_governance_semantic_runtime_completion
reopen_condition: new_phase_10_entry_or_live_UI_remains_Deferred_109_or_selected_criteria_have_zero_evaluated_results
```

MARGPAの中心であるGD Semantic RuleがCompile／Selected表示だけで実評価されない状態は、Phase 6の目的を満たさない。2026-08-29 User Manualでは109件全件が`Deferred（意味評価待ち）`のままで、Built-in Judgeは32件を全件`not_applicable`、77件を`deferred`、`evaluated=0`とした。Budgetで一部Deferredになることは許容するが、Budget内Criterionは実評価する。

### UF-P6-004 — Judge／Repair Golden PathとFail-safe

```yaml
source_findings:
  - P6-GOV-010
  - P6-GOV-017
  - P6-GOV-018
status: known_user_manual_fail_deferred_by_user_override
severity: major
priority: P1_new_phase_10_reserved
closure_blocker: false_by_explicit_user_override
impact_scope: live_judge_repair_presentation
deferral_target: new_phase_10_governance_semantic_runtime_completion
reopen_condition: new_phase_10_entry_or_obvious_evidence_contradiction_is_accepted_or_repair_path_cannot_complete_truthfully
```

実画面でJudgeが誤答を自己承認する、選択していないProviderへ誤帰属する、Repairが成立しない、Failure時にRaw Candidateを不正に通す状態はPhase 6で閉じる。

Modelが全事実を正答することはAcceptanceにしない。検証不能時に正確なFailureへ収束し、Repair成功時はCandidate／Repair／Rejudge／Presentationが相関することを求める。

2026-08-29 User ManualではJudge／Repair ENFORCEでも全32件が`not_applicable`となり、2 Turnとも`判定結果を確定できませんでした。`のSafe Fallbackだけだった。Repair／Rejudge／修復回答は未成立。

### UF-P6-005 — User Mac Real Browser最終Manual Acceptance

```yaml
status: user_gate_failed_known_debt_accepted_for_phase_progression
severity: gate
priority: P1_new_phase_10_reserved
closure_blocker: false_by_explicit_user_override
impact_scope: real_browser_real_runtime
deferral_target: new_phase_10_post_rework_user_manual_acceptance
reopen_condition: new_phase_10_rework_complete_or_any_frozen_core_manual_scenario_is_retested
```

Source／Fixture／TestだけでPhase 6 Closureへ昇格しない。Current Rework後、Userが実画面でProvider、Semantic、Judge／Repair、Recording、Stop、継続性を確認する。

2026-08-29の確認ではMain切替、Recording、Stop、継続性はPASSしたが、Dedicated Provider、Semantic、Judge／RepairがFAILした。正本Evidenceは`docs/project/phases/phase_6/history/operations/phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_ja_20260829164049.md`。

## 5. Phase 6 — Recorded but Non-blocking Findings

### UF-P6-006 — Tracked Worker Admission／Shutdown TOCTOU

```yaml
source_finding: P6-CODEX-088
status: resolved_R25_controller_bounded_review_pass
severity: major_if_triggered
priority: P2
closure_blocker: false_unless_current_production_path_reproduces_material_effect
impact_scope: shutdown_hardening
deferral_target: Phase_10_hardening
reopen_condition: production_shutdown_returns_clean_while_live_worker_can_mutate_or_block_unload
```

Negative ProbeでRaceは成立したためFinding自体は保持する。ただし、Current WebRuntimeの外側Drain順とUser主経路でMaterial Effectが再現しない限り、PoC Closureを止めない。

R25で既に修正中のため成果は保持するが、これを起点に追加Concurrency Hardeningを無制限に派生させない。

R25のAtomic AdmissionとRace TestをControllerが照合し、Focused Test PASS。追加Concurrency探索は行わない。

### UF-P6-007 — Qwen3Guard ManifestのAnti-corruption Validation

```yaml
source_finding: P6-CODEX-090
status: resolved_R27_controller_bounded_review_pass
severity: major_if_manifest_corrupted
priority: P2
closure_blocker: false
impact_scope: future_contract_integrity_hardening
deferral_target: Phase_10_hardening
reopen_condition: current_manifest_or_binding_differs_from_pinned_official_contract
```

Current Checked-in ManifestはPinned Qwen公式Sourceと一致している。偽Provider、偽Protocol、偽Categoryを将来注入した場合の拒否強化は価値があるが、現PoC主経路を止めない。

R27でExact Cross-field Validatorが追加され、偽Provider等のConstruction拒否をFocused Testで確認した。

### UF-P6-008 — Qwen3Guard Provider IdentityのEvidence Round-trip

```yaml
source_finding: P6-CODEX-091
status: resolved_R27_controller_bounded_review_pass
severity: evidence_major
priority: P1
closure_blocker: false_if_executed_provider_is_truthful_else_reclassify_P0
impact_scope: observability_audit_evidence
deferral_target: Phase_9_observability_or_Phase_10_hardening
reopen_condition: UI_or_evidence_misattributed_executed_provider
```

Artifact SHA、Revision、Manifest Digest等の完全Round-tripは延期可能。ただし、どのProviderを実行したかという最低限のIdentityまで誤る場合はUF-P6-002へ統合してP0とする。

R27で`ModelDetectionProvenance`が追加され、3 Target×5 Outcome形状のRound-tripをController Focused Testで確認した。

### UF-P6-009 — Unload Exception後のAdapter残留

```yaml
source_finding: IR-R24-001
status: resolved_R26_controller_bounded_review_pass
severity: moderate_to_major_if_reused
priority: P1
closure_blocker: false_if_failed_adapter_cannot_receive_new_lease
impact_scope: lifecycle_failure_recovery
deferral_target: Phase_9_or_Phase_10_hardening
reopen_condition: failed_or_degraded_adapter_can_execute_new_turn
```

Adapter Mapへの残留自体は即Blockerにしない。新規Leaseが拒否され、表示がFailureを正しく示すなら延期する。再実行できる場合はUF-P6-001としてP0。

R26でUnload成功／失敗の両方でAdapter Referenceを除去し、失敗時は`DEGRADED / provider_unload_failed`へ収束することを確認した。

### UF-P6-010 — Real Model品質とLocal Hardware制約

```yaml
status: research_candidate_not_product_accepted
severity: quality_limitation
priority: P1
closure_blocker: false_for_framework_if_runtime_failure_is_truthful
impact_scope: Qwen_DeepSeek_Selene_Qwen3Guard_quality_and_latency
deferral_target: Phase_7_web_RAG_then_Phase_9_experiment_then_Phase_10_model_hardware
reopen_condition: pathological_repeat_unbounded_generation_or_false_runtime_success
```

Qwen／DeepSeekの誤答、DeepSeek Q8→Q4再量子化Caveat、Selene／Qwen3GuardのLocal Mac性能は研究課題として残す。Model回答品質が低いこと自体でFramework Phase 6を無限に止めない。

病的反復が無限生成になる、Runtime Failureを成功表示する、選択Providerと実行Providerが異なる場合はP0へ戻す。

## 6. Phase 7 — Phase 11以降へ延期したExternal Web Findings

### UF-P7-001 — 実Web Provider／Manual Grounding／Server OFF／Consent Enforcement

```yaml
source_findings:
  - P7-CODEX-001
  - P7-CODEX-002
  - P7-CODEX-003
  - P7-CODEX-004
status: known_debt_deferred_by_explicit_user_decision
severity: major
priority: P1_phase_11_plus_reserved
closure_blocker: false_for_phase_7_by_explicit_scope_reduction
impact_scope: real_web_search_grounded_chat_network_consent
deferral_target: phase_11_plus_governed_external_web_knowledge_runtime
reopen_condition: phase_11_plus_entry_or_external_provider_enablement_authority
```

ClaudeのLocal Corpus、Web Security PortおよびData Controls基礎は保持する。ただしProduction WebはFixture固定で、Manual EvidenceはChat回答／Citationへ接続されず、Web検索OFFはFrontend Local State、外部送信Consentは実行経路へ未接続である。この技術状態は未解決のまま保持する。

2026-08-29のUser Decisionにより、実Provider、External Network、Web-grounded Chat、一般URL Fetchおよび外部送信EnforcementはPhase 11以降へ延期した。Phase 7では実Web検索をClaimせず、External Provider `none`相当、Activation `disabled／OFF`相当、External Network Call 0を安全な境界とする。

Phase 11以降では、Provider／Credential／Cost／Privacy／Consent／SSRF／Parser Isolation／Prompt Injection／Poisoning／Provenance／Citationを一体のExternal Knowledge Runtimeとして再開する。Public SearXNG Instanceその他の第三者Endpointを公開Demoの既定値へHard-codeしない。

Controller Review正本：

`docs/project/phases/phase_7/history/operations/phase_7_codex_controller_bounded_independent_review_adjust_ja_20260829215534.md`

User Scope Reclassification正本：

`docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md`

### UF-P7-002 — Fixture CallとOutbound Network CallのObservability分離

```yaml
source_finding: P7-CODEX-005
status: known_debt_deferred_with_external_web_runtime
severity: moderate
priority: P2
closure_blocker: false_independent
impact_scope: web_search_observability
deferral_target: phase_11_plus_governed_external_web_knowledge_runtime
reopen_condition: external_web_runtime_observability_design_or_provider_enablement
```

`network_calls_made`がFixture Provider Callも実Networkとして数える。Phase 7ではFixtureを実Web成功とClaimせず、本件単独の追加Rework Loopは作らない。Phase 11以降のProvider実接続時に、`provider_calls_attempted`と`outbound_network_calls_attempted`を分離する。

### UF-P7-003 — 削除／更新済みSource由来Factの過去Context再利用

```yaml
status: reproduced_and_deferred_after_phase_7_manual_pass
severity: moderate_research_integrity
priority: P1
closure_blocker: false
impact_scope: conversation_context_freshness_semantic_governance
deferral_target: Phase_9_semantic_governance_judge_repair
reopen_condition: phase_9_stale_fact_governance_design_or_old_fact_is_presented_despite_current_evidence
```

Local Corpus削除後、RAG OFFの同一Conversationでは過去Turnの`CEDAR-153`を再出力した。RAG ONでは
Current CorpusがNO_HITとなり、根拠なし回答とNO_HIT Citationへ正しく収束した。従ってCurrent RAG Indexの
残留ではなく、Historical Conversation Contextの再利用である。

Phase 9では過去Citation／Revision／DigestとCurrent Source Lifecycleを比較し、削除／更新済みSource由来Factを
`stale_evidence`としてSemantic GD、Judge、RepairおよびRejudgeへ接続する。RAG OFFの通常会話を過剰遮断せず、
追跡可能なStale FactとFreshness-sensitive Questionへ限定する。

### UF-P7-004 — Qwenの一時的な回答言語逸脱

```yaml
status: intermittent_model_quality_observation
severity: model_quality
priority: P2
closure_blocker: false
impact_scope: answer_language_adherence
deferral_target: Phase_9_model_language_governance
reopen_condition: repeated_wrong_language_output_or_configured_language_is_systematically_ignored
```

NO_HIT質問で一度ロシア語回答が生成されたが、同じ機能経路の再実行では日本語へ戻った。Phase 7 RAGの
構造的不具合を示すEvidenceはなく、Qwenの一時的な言語遵守逸脱の可能性が高い。繰り返す場合は
Configured Answer Language、Semantic JudgeおよびPresentation Boundaryで再評価する。

### UF-P7-005 — Identifier質問に対する無関係Project DocsのFalse-positive Grounding

```yaml
status: reproduced_during_phase_8_final_manual_regression
severity: moderate_research_integrity
priority: P1
closure_blocker: false_for_phase_8
impact_scope: local_RAG_retrieval_relevance_and_grounded_synthesis
deferral_target: Phase_9_semantic_governance_judge_repair
reopen_condition: phase_9_false_positive_grounding_design_or_unrelated_project_docs_are_presented_as_current_evidence
```

Local Corpus `TEST 11`を削除した後の新規Chatで、削除済みFact `3475`および削除済みLocal Corpus Citationは
再出力されなかった。一方、Query中の`Local Corpus`、`TEST`、`11`等の一般語に反応し、無関係なProject Docs
3件をCitationとして取得して、質問へ関係のない内容から回答を組み立てようとした。

これはUF-P7-003の「削除済みFactを過去Contextから再利用する問題」とは別である。Current Local Corpus削除と
Citation Freshnessは成立しているが、Retrieval RelevanceがNO_HITへ収束せず、False-positive Evidenceを
`GROUNDED_READY`相当として扱うSemantic／Grounding課題である。Phase 9でQuery-Source関連度、Identifier一致、
Evidence Sufficiency、Judge／RepairおよびStrict NO_HIT候補を統合して扱う。

## 7. Phase 8 — Controller Review後の未解決

### UF-P8-004 — Constitution PreviewのAction Permission／Violation Presentation欠落

```yaml
source_finding: P8-CODEX-012
status: resolved_P8_RW7_controller_targeted_review_pass
severity: major
priority: resolved_former_P0
closure_blocker: false
impact_scope: constitution_three_mode_preview_and_P8_ACC_021
deferral_target: none
reopen_condition: preview_loses_three_axis_semantics_or_misrepresents_active_runtime_authority
minimum_fix_scope: preview_contract_projection_UI_tests_only
estimated_resource_cost: one_short_bounded_rework_cycle
resolution_evidence: docs/project/phases/phase_8/history/operations/phase_8_codex_controller_constitution_preview_semantics_single_targeted_re_review_ja_20260831072057.md
```

P8-RW7は`evaluation_disposition`、`action_permission`、`violation_presentation`をBackend Contract、REST Projection、
日本語／英語UIへ損失なく追加した。Current Manifestの未対応Ruleは`typed_unsupported`、適用RuleのないViewは
`not_evaluated`として表示し、Production Active ModeはOFF固定のまま維持する。

2026-08-31のCodex Controller Targeted ReviewでP8-CODEX-012をRESOLVED、P8-ACC-021をPASSと判定した。
Production Activation、Runtime Enforcement、GD接続または新Rule Engineは追加していない。

### UF-P8-003 — Completion GateがFrozen EnvelopeのGate Reasonsへ現れない

```yaml
source_finding: P8-CODEX-011
status: resolved_P8_MR9_user_final_manual_pass
severity: major_governance_truthfulness
priority: resolved_former_P0
closure_blocker: false
impact_scope: dev_agent_completion_approval_gate_reason_presentation
deferral_target: none_for_current_micro_rework
reopen_condition: awaiting_completion_approval_displays_non_completion_gate_reason
```

`important_gate_only` RunはRuntime上`awaiting_completion_approval`で正しく停止し、Typed Completion Approval Evidenceの
Contract上のGate Reasonも`completion`である。P8-MR9前は実画面がCompletion承認時にもRun EnvelopeのTool Gate Reasonを
参照し、`Gate Reason: external_write`と表示していた。

P8-MR9後のUser実画面で、Tool Gateは`external_write`、Completion Gateは`completion`、最終Runは`completed`として
正しく分離表示されることを確認した。

### UF-P8-001 — 最終Tool成功後のRun Completion Transition／Manual差

```yaml
source_finding: P8-CODEX-009
status: resolved_by_explicit_completion_gate_and_user_manual
severity: medium_usability_and_manual_alignment
priority: P1
closure_blocker: false
impact_scope: dev_agent_run_completion_ui_and_user_manual
deferral_target: none
reopen_condition: completion_transition_again_becomes_ambiguous_or_bypasses_completion_approval
```

Completion Gate導入後、最後のTool成功から`awaiting_completion_approval`へ遷移し、Userが`completion`を承認した後に
`completed`へ収束するFlowを実画面で確認した。Tool Gateの`external_write`とCompletion Gateの`completion`も分離表示される。
従って旧「追加Advanceの意味が不明」というFindingは解消し、明示的なCompletion Approval TransitionをCurrent Baselineとする。

### UF-P8-002 — Manual URL Conversation Testの実DNS依存

```yaml
source_finding: P8-CODEX-010
status: resolved_P8_MR7_MR8_controller_verified
severity: medium_verification_reproducibility
priority: P2
closure_blocker: false
impact_scope: manual_URL_conversation_test_isolation
deferral_target: opportunistic_test_hermeticity_or_phase_10_full_docs_and_validation
reopen_condition: canonical_test_must_run_under_network_restricted_environment_or_runtime_behavior_differs_from_fixture_environment
```

Manual URLのMain Model注入を確認するConversation Test 3件だけがSafe DNS Stubを持たず、Network制限環境では
`socket.getaddrinfo()`が`dns_resolution_failed`となりFailする。Claude実行環境では全SuiteがPASSしており、Product Runtimeの
Direct URL Fetch不成立を示すEvidenceではないが、`Network Authority 0で再現可能なCanonical Verification`というClaimは維持できない。

これはTest Isolation／再現性Debtであり、PoCのUser主経路、Evidence PersistenceまたはRuntime Security Boundaryを直接壊さない。
今回のBlocker限定Reworkでは修正せず、Acceptance上はP8-ACC-039をPASSへ捏造しない。将来修正時はTest内だけでSafe Public DNS
ResultをStubし、Production Validation Pathを迂回しない。

**P8-MR7-1 (P8-CODEX-013) Addressed**：`url_security.validate_url_before_connect()`へ
Constructor-level `resolver`（`WebKnowledgeService`／`HttpxWebFetchProvider`双方）を追加し、`tests/unit/conversation/
test_conversation_generation.py`の`_web_knowledge_service()`が実DNSを要求していた根本原因（このFinding自体が指す3 Test含む、
Controllerが2026-08-31 13:48実測した4 Test）を解消した。本Package実行環境での`uv run pytest -q`Full Suite実測は
`2186 passed, 7 deselected`（Deselectedは`model_smoke`のみ、DNS関連Failureは0件）——ただしこの実測はClaude実行環境のもので
あり、`reopen_condition`が要求する「Network制限環境での再現」はCodex Controller自身の次回実行でのみ確定できる。Controllerの
再実行でもDNS関連Failure 0件、P8-MR8後のBackend Full 2191件PASSをControllerが確認したため解決済みへ更新した。

### UF-P8-005 — Public Direct URL安定取得とFetch失敗後の非Grounded回答

```yaml
source_finding: phase_8_user_mac_manual_web_segment_1
status: resolved_minimum_MVP_path_P8_MR8_and_user_manual
severity: major
priority: resolved_former_P0
closure_blocker: false
impact_scope: manual_public_URL_fetch_and_current_turn_grounding
deferral_target: none_for_supported_UTF8_public_pages
reopen_condition: ordinary_public_URL_fetch_failure_or_fetch_zero_turn_generates_page_claims
minimum_fix_scope: bounded_retry_public_address_fallback_exact_failure_projection_fail_closed_grounding
estimated_resource_cost: small_to_medium_bounded_rework
```

P8-MR0〜MR8後のUser Mac再確認で、`https://example.org/`とHololive公式Pageの取得、本文抽出、Chat注入、Citation、
Reload／Restart復元が成立した。Hololive公式Pageは5回以上取得でき、Expressive Mode、Context Usage、両方有効の全条件で
Model回答へ接続した。Loopbackは`private_or_loopback_address`へ拒否され、取得失敗TurnはModel独自の人物説明を生成せず、
Typed Safe Failureへ収束した。

Manual URL Readerの中心Purposeは、Userが明示したURLを有界に取得し、成功したEvidenceだけをCurrent Turnへ渡すことである。
一時的なDNS／Connect失敗を即Permanent Rejectionへ扱うこと、またはFetch 0でもPage由来Factを生成することは中心経路へ影響する。

Bounded Retry、Injected Resolver、Exact Failure Reason、Evidence-only TurnのFail-closed GroundingおよびFinal Prompt-aware
BudgetをSource／Test／実画面で確認した。任意Charset Site互換は本件へ混ぜず、UF-P8-012へ分離する。

正本Evidence：

`docs/project/phases/phase_8/history/operations/phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_ja_20260831112449.md`

### UF-P8-006 — Raw HTML丸ごと注入によるContext Budget Failure

```yaml
source_finding: phase_8_user_mac_manual_web_segment_1_hololive_raw_HTML
status: minimum_MVP_resolved_full_ingestion_hardening_reserved
severity: major_usability_for_large_pages
priority: P1
closure_blocker: false_by_current_user_reservation
impact_scope: web_content_normalization_and_main_model_context_budget
deferral_target: phase_11_governed_web_ingestion_with_optional_phase_8_typed_failure
reopen_condition: manual_URL_rework_scope_includes_extraction_or_large_page_must_be_supported
```

初回実画面ではHololive公式Pageの約8.9万文字のRaw WordPress HTMLを8192 Contextへそのまま注入し、
`入力がModelのContext上限を超えました。`へ失敗した。P8-MR0〜MR8は最小HTML本文抽出、Character Cap、Final Prompt-aware
Token BudgetおよびTyped `content_budget_exceeded`を実装し、再確認では通常条件で5回以上成功、余地がない条件だけが
明示的なContext Budget警告へ収束した。

Phase 8の最小MVP経路は解決済みとする。Readability、Chunking、Relevance Selection、Hostile Content処理等の
Full Extractor／NormalizerはPhase 11以降へ維持する。

### UF-P8-007 — Web Fetch Specific Failure ReasonのChat投影消失

```yaml
source_finding: phase_8_user_mac_manual_web_segment_1_url_rejected_projection
status: resolved_P8_MR7_MR8_and_user_reload_restart_recheck
severity: moderate_observability
priority: P1
closure_blocker: false_standalone_fix_with_UF_P8_005
impact_scope: live_SSE_persistence_reload_restart_and_web_evidence_UI
deferral_target: same_bounded_rework_as_UF_P8_005
reopen_condition: Chat_displays_only_aggregate_url_rejected
```

P8-MR7までにAggregate／Specific ReasonをLive／Persistenceへ追加し、UserはAbe Hiroshi Siteの
`content_type_unsupported`とSafe FailureがReload／Server Restart後も同じTurnへ保持されることを確認した。
Model Call 0のUI可視化は別のObservability課題UF-P8-011へ分離する。

### UF-UI-007 — 通常Composer URL貼付と専用Manual URL欄のUX差

```yaml
status: reserved_user_scope_difference
severity: usability_scope
priority: P2
closure_blocker: false
impact_scope: message_composer_manual_URL_evidence_entry
deferral_target: phase_10_right_panel_or_phase_11_web_UI
reopen_condition: web_evidence_UI_redesign_start
```

Userが想定した最終UXは通常Message入力へURLを貼り、そのTurnで取得する方式である。Current実装は専用Manual URL欄を使う。
Reliability／Grounding修正とは分離し、Phase 10右Panel／Citation UIまたはPhase 11 Governed Web Runtimeで扱う。

### UF-P8-008 — Archive Sidebar／Panel State非同期

```yaml
source_finding: phase_8_user_mac_manual_segments_2_to_5
status: resolved_P8_MR_and_user_manual_pass
severity: major_feature_semantics
priority: resolved_former_P0
closure_blocker: false
impact_scope: archive_sidebar_data_controls_state_synchronization
deferral_target: none_for_minimum_archive_management
reopen_condition: archived_chat_remains_in_active_sidebar_or_archive_panel_requires_browser_reload
minimum_fix_scope: active_only_sidebar_archive_show_hide_refetch_unarchive_sync
estimated_resource_cost: one_short_frontend_dominant_rework
```

Archive／Unarchive／Open／Resume不要は成立したが、Archive後もChatがSidebarへ残り、Archive一覧は
Settings Reopenで再Fetchされない。SidebarはActiveだけ、Archive PanelはArchivedだけを表示し、相互遷移後に
即時同期する。Show／Close／Refetchも必須。

P8-MR後の実画面で、Archive後のSidebar除外、Archive一覧だけへの保持、Open、Close、Unarchive、Sidebar復帰、
Resume不要、Settings再表示時の更新およびBranch UI既定非表示をPASSした。

### UF-P8-009 — Web Citation必須Metadata／Actual Title欠落

```yaml
source_finding: phase_8_user_mac_manual_segments_2_to_5
status: resolved_P8_MR_and_user_manual_pass
severity: major_traceability_truthfulness
priority: resolved_former_P0
closure_blocker: false
impact_scope: web_evidence_live_persistence_reload_restart_UI
deferral_target: none_for_required_P8_metadata
reopen_condition: citation_omits_fetched_at_content_type_or_canonical_identity
minimum_fix_scope: contract_projection_persistence_UI_actual_title_copy_label_tests
estimated_resource_cost: small_to_medium_bounded_rework
```

Current Chat CitationはPublic Web／URL／Digest／Untrusted Labelを表示するが、P8-REQ-007のFetched At／Content Typeが欠け、
Canonical URLとCopy Labelも不明確である。TitleはHTML `<title>`ではなくURLとなる。Requested／Canonical URL、
Transformation、Source Authorityの有無をContractどおり投影し、P8-ACC-010をLive／Reload／Restartで再導出する。

P8-MR後の実画面で、Public Web、実Title、Canonical URL、Source Authority、Fetched At、Content Type、Transformation、
Document Digest、Untrusted LabelおよびCopyを確認し、Reload／Server Restart後も同じEvidenceを復元した。

### UF-P8-010 — Dev Agentの非追跡Memory Fixture／Blind Approval

```yaml
source_finding: phase_8_user_mac_manual_segments_2_to_5
status: resolved_P8_MR_and_user_real_file_manual_pass
severity: major_approval_and_evidence
priority: resolved_former_P0
closure_blocker: false
impact_scope: dev_agent_tool_result_approval_evidence_and_fixture_workspace
deferral_target: none_for_phase_8_foundation
reopen_condition: user_cannot_see_exact_action_input_output_or_persisted_fixture_result
minimum_fix_scope: runtime_data_fixed_workspace_path_safety_UI_input_output_digest_restart_tests
estimated_resource_cost: small_to_medium_bounded_rework
```

Current Demo RunはStep State／Gate／Cancelを表示するが、List／Read／WriteのInput／Output／Target／Contentを表示せず、
WriteはProcess Memoryだけに残る。Userは追跡不能なApprovalを拒否した。Configured `runtime_data/persistent/<scope>/dev_agent/`
内の固定`fixture_workspace`だけを扱う実File Toolへ限定変更し、Path／Content／Overwrite／Result／Digest／Run／Stepを表示・保存する。
Project File、任意User File、Network、Real MCPへAuthorityを拡張しない。

P8-MR後の実画面ではConfigured Runtime Data Root配下の実File Workspaceを使用し、`notes/readme.md`、
`notes/todo.md`、`notes/new.md`の実在を確認した。UIはList／Read／WriteのInput／Output／Digest／Overwrite／Written At、
Resource Scope、Tool Gateを表示し、`awaiting_approval`→`awaiting_completion_approval`→`completed`と遷移した。
Project SourceやNetworkへは接触していない。Completion Gateの表示ReasonだけはUF-P8-003として再Openした。

### UF-UI-008 — Archive Dedicated Manage Modal／Settings過密

```yaml
status: reserved_user_requested_UI_redesign
severity: usability
priority: P2
closure_blocker: false
impact_scope: data_controls_archive_management_information_architecture
deferral_target: phase_10_right_panel_and_settings_UI
reopen_condition: phase_10_UI_reorganization
```

Current Phase 8ではShow／Close／Refresh／State同期だけを直す。ChatGPT参考画像のような`管理する`専用Modal、
Table Layout、完全削除の将来UXはPhase 10へ送る。完全削除自体は未実装のまま保つ。

### UF-UI-009 — Constitution Preview Mode／Decision同一行

```yaml
status: resolved_P8_MR_and_user_manual_pass
severity: minor_to_moderate_readability
priority: P1
closure_blocker: false_standalone_but_fix_in_current_rework
impact_scope: constitution_preview_readability
deferral_target: current_phase_8_bounded_rework
reopen_condition: mode_name_and_decision_remain_on_same_line
```

Constitution SemanticsはPASSしたが、OFF／OBSERVE／ENFORCEとDecisionが同一行にある。Mode名の次行から
Decision／評価区分／Action許可／違反時表示を1行ずつ配置する。Backend Semanticsは変更しない。

P8-MR後の実画面で、OFF／OBSERVE／ENFORCE Headerと4比較行の改行を確認した。

### UF-UI-010 — Dev Agent Action Button Contrast

```yaml
status: resolved_primary_danger_controls_with_one_new_minor_exception
severity: accessibility_and_operability
priority: P1
closure_blocker: false_standalone_but_fix_in_current_rework
impact_scope: dev_agent_approval_advance_cancel_controls
deferral_target: current_phase_8_bounded_rework
reopen_condition: action_button_text_is_not_readable_in_light_or_dark_theme
```

Approval／Deny／Advance／Cancel ButtonはBackgroundとTextが白系でほぼ読めない。Primary／Secondary／Dangerの役割を与え、
Light／Dark両Themeで読めるContrastにする。

主要なApproval／Deny／Advance／Cancelは実画面で判読可能となった。Completed後の`新しいDemo Runを開始`だけが
他の関連Buttonと色不統一であるため、新規UF-UI-013として分離した。

### UF-P8-011 — Fail-closed Grounding時のMain Model Call 0をUIから確認できない

```yaml
status: open_user_reproduced_observability_gap
severity: moderate_research_observability
priority: P2
closure_blocker: false
impact_scope: manual_web_failure_inference_call_observability
deferral_target: Phase_9_observability_or_context_governance_trace_UI
reopen_condition: phase_9_observability_design_or_research_requires_live_model_call_count
```

Counting Fakeを使うBackend Testは、Manual URL取得失敗時にMain Model Call 0を証明している。しかしCurrent実画面は
赤いFailureまたはSafe Failure Presentationだけを示し、UserがModel Call 0を直接確認する欄を持たない。
Research Platformとしては、Provider Call／Main Model Call／Judge／Repair／Tool CallをTurn単位で区別して確認できる価値が高い。
Phase 8 Closureは止めず、Phase 9 ObservabilityでExecution Traceへ追加する。

### UF-P8-012 — Shift_JIS／x-sjis Pageを`content_type_unsupported`へ分類する

```yaml
status: open_user_reproduced_charset_compatibility_gap
severity: moderate_web_compatibility_and_failure_taxonomy
priority: P1
closure_blocker: false_for_phase_8_UTF8_MVP
impact_scope: manual_URL_charset_decode_and_exact_failure_reason
deferral_target: Phase_11_governed_web_ingestion
reopen_condition: charset_aware_fetch_normalizer_or_general_public_web_support
```

`https://abehiroshi.la.coocan.jp/`は3 Chatで同じ`content_type_unsupported`へ収束した。Source確認ではCurrent Fetch Adapterが
UTF-8 Decodeを前提とし、同SiteのShift_JIS／x-sjisをDecodeできない場合も`content_type_unsupported`へ分類する。
Security拒否やRetry失敗ではなくCharset互換とFailure Taxonomyの問題である。Phase 8のUTF-8 Public Page MVPは成立しているため、
Charset検出、明示Decode、NormalizerおよびTyped `charset_unsupported／decode_failed`はPhase 11へ送る。

### UF-UI-011 — 過去Web Failure警告がCurrent Composerへ残留する

```yaml
status: resolved_P8_MR9_user_final_manual_pass
severity: major_current_state_truthfulness
priority: resolved_former_P0
closure_blocker: false
impact_scope: composer_current_web_failure_presentation
deferral_target: none_for_current_micro_rework
reopen_condition: chat_switch_new_chat_or_successful_next_turn_keeps_old_web_failure_warning
```

Manual URL取得失敗後の警告が、Chat切替、新規Chatおよび後続Turnの状態と無関係にCurrent Composerへ残り続けた。
Historical Failure Turn自体は保持すべきだが、別Chat／別TurnのCurrent Composer Stateとして表示してはならない。
Chat切替、新規Chatおよび成功した次Turnで警告を消し、同じ失敗TurnのHistorical Evidenceは変更しない。

P8-MR9はSource調査で新規Chat／成功Turnが既に正しかったことを確認し、Chat切替だけのReset漏れを修正した。
UserはAbe Hiroshi SiteのFailure経路を使い、過去警告がCurrent Composerへ残らないことを実画面でPASSした。

### UF-UI-012 — `Untrusted External Content`の文字色不統一

```yaml
status: resolved_user_accepted_semantic_warning_color
severity: minor_UI_semantic_consistency
priority: resolved_by_user_visual_acceptance
closure_blocker: false_standalone_but_fix_in_current_rework
impact_scope: web_citation_untrusted_label_readability
deferral_target: current_phase_8_micro_rework
reopen_condition: untrusted_label_uses_unintended_text_color
```

Web Evidence Card内で`Untrusted External Content（信頼できない外部Content）`だけが周囲のMetadataと異なる文字色だった。
P8-MR9は既存`--gauge-warn`注意色を明示適用した。Controllerは一度、周囲と同色でないこととLight Themeの数値Contrastを理由に
再調整を提案したが、UserがWhite／Dark実画面を直接確認し、強調表示として「むしろよい」と判断した。

従って、色差は不統一BugではなくUntrustedを識別する意図的Semantic Emphasisとして採用する。Controller再調整案と
後続Micro HandoffはUser DecisionによりSuperseded／Not Authorizedとする。

### UF-UI-013 — `新しいDemo Runを開始`だけButton色が異なる

```yaml
status: resolved_P8_MR9_user_final_manual_pass
severity: minor_UI_consistency
priority: resolved_former_P1
closure_blocker: false_standalone_but_fix_in_current_rework
impact_scope: dev_agent_completed_state_restart_action
deferral_target: current_phase_8_micro_rework
reopen_condition: completed_run_restart_button_differs_from_equivalent_primary_action
```

主要なDev Agent Button Contrastは解決したが、Run Completed後の`新しいDemo Runを開始`だけが他のPrimary Actionと異なる。
既存Primary Styleを再利用して統一し、新しいButton Systemは作らない。

P8-MR9後のUser実画面で、`新しいDemo Runを開始`がPrimary Button色へ統一されたことを確認した。

### UF-UI-014 — Settings Manual URL結果がClose／Reopen後も残る

```yaml
status: open_deferred_UI_state_cleanup
severity: minor_usability
priority: P2
closure_blocker: false
impact_scope: settings_manual_URL_result_lifecycle
deferral_target: Phase_10_settings_and_right_panel_UI
reopen_condition: settings_web_panel_state_cleanup_or_right_panel_migration
```

SettingsのManual URL取得結果はSettingsを閉じて開き直しても残る。取得履歴の永続機能ではなくCurrent Utility Stateであり、
最終UIではClear／Close／Historyの意味を定義する必要がある。今回の4件Reworkには含めずPhase 10 UIへ送る。

### UF-UI-015 — Manual URL成功／失敗CardのTitle／URL表示不統一

```yaml
status: open_deferred_UI_consistency
severity: minor_usability
priority: P2
closure_blocker: false
impact_scope: settings_manual_URL_result_card_presentation
deferral_target: Phase_10_settings_and_right_panel_UI
reopen_condition: web_evidence_result_card_redesign
```

成功Cardは実TitleとURLを表示する一方、失敗CardはURLをTitle位置とURL位置へ重複表示し、Authorityも`unknown`となる。
Failure Reason自体は正直に表示できているためPhase 8 Closureは止めず、Phase 10のWeb Evidence／右Panel整理で扱う。

### UF-P8-013 — Dev Agent Capability選択がServer Restart後もONのまま

```yaml
status: open_user_reproduced_restart_state_followup
severity: minor_to_moderate_state_expectation
priority: P2
closure_blocker: false
impact_scope: dev_agent_capability_selection_restart_semantics
deferral_target: Phase_9_agent_harness_or_Phase_10_settings_state_policy
reopen_condition: dev_agent_capability_state_policy_design_or_default_restart_behavior_review
```

Server Restart後もSettingsの`Chat／Dev Agent`選択がDev Agent ONのまま復元された。Current Capability自体はFoundationであり、
任意Project File／Network Authorityは持たないため即時Safety Blockerではない。ただしCapability選択をUser Preferenceとして
永続化するか、Process RestartごとにChatへ戻すか、将来のLevel 1以降でApproval Profileと連動させるかを明示決定していない。
Phase 9 Agent HarnessまたはPhase 10 Settings State Policyで扱う。

### UF-P8-014 — Per-purpose ConsentがServer Restart後もONのまま

```yaml
status: open_user_reproduced_policy_ambiguity
severity: moderate_privacy_and_state_semantics
priority: P1
closure_blocker: false_for_current_no_general_provider_MVP
impact_scope: data_controls_consent_persistence_and_restart_defaults
deferral_target: Phase_10_data_controls_policy_and_UI
reopen_condition: consent_persistence_policy_review_or_real_external_provider_activation
```

UserがONへ保存した4つのPer-purpose ConsentはServer Restart後もONのまま復元された。一方、UIは`Default is all OFF`と表示する。
Phase 7 Manualでは個別Consentの保存とReload後PersistenceをPASSしており、単純にRestartでOFFへ戻すと既存要件と衝突する。

従って本件は、`初回Default OFF`、`User保存Preference`、`Process Restart`、`Session Consent`、`外部Provider Activation時の再確認`
を分離するPolicy課題として保持する。実Keyword Search Providerは未接続であるためPhase 8 Closureは止めない。Phase 10で
永続Consentを維持するか、外部送信ConsentだけをSession-bound／再確認必須にするか決定する。

### UF-UI-016 — English Data ControlsでRetention本文が日本語のまま

```yaml
status: open_user_reproduced_localization_gap
severity: minor_to_moderate_localization_truthfulness
priority: P2
closure_blocker: false
impact_scope: data_controls_retention_fact_localization
deferral_target: Phase_10_settings_localization_cleanup
reopen_condition: English_UI_localization_pass_or_data_controls_redesign
```

English UIではHeading、説明、Consent Labelは英語になる一方、Retention Fact本文は日本語のまま表示される。
Retention内容自体はCurrent Runtimeの事実を正しく示しており、Data Lossや虚偽CapabilityではないためPhase 8 Closureを止めない。
Phase 10のSettings／Localization整理で、Source別Retention Factの日本語／英語Projectionを分離する。

## 8. Phase 9 Closure前へ延期したUI／Observability

### UF-UI-001 — Advanced Mode Layout／表示整理

```yaml
source_finding: P6-DELTA-016
status: partially_resolved_four_subitems_remaining_deferred
severity: minor
priority: P2
closure_blocker: false
impact_scope: frontend_settings_advanced_mode
deferral_target: Phase_9_closure_before_final_docs
reopen_condition: phase_9_closure_ui_cleanup_start
```

含む項目：

- Judge OFF時はCurrentを`無効／実行なし`とし、前回結果をHistoricalへ分離。
- Model Status、Judge／Repair／Recording、Role Provider選択、Runtime設定制御の順序整理。
- Research・Developer ModeのOFF／ON Control非表示、内容常時表示、`research_developer_mode`項目非表示、3:3 Layout。
- SidebarでCurrent Modelに加えProfile／Device／Acceleration情報を失わない。
- 回答言語Dropdown幅だけを適正化し、他Controlをずらさない。
- OFF／OBSERVE／ENFORCEおよびOFF／METADATA／FULLのButton位置を揃える。
- Panel区切り線と縦余白。Governance Definitions／先頭Main Runtime Governanceは例外。
- Safe Fallback／Timeout／Malformed Output等を原因別・回答言語別の文面にする。
- Recordingへ最新Request ID、時刻、Mode、Outcomeを表示し、Current／Historical／Unmatchedを分離。
- Sidebarは`<model key> active`と`<profile> • <device> • <acceleration>`の2行とし、`Context 8192`を混入させない。
- Active Guardが`none`ならCurrent Guardrail Modelは単に`未設定`とし、Rule／Pattern BaseをCurrent Model表示へ混ぜない。
- Provider／Mode適用Failureは自動消去せず、Exact Failure Reasonを確認可能にする。
- Historical／Unmatched RecordingはTurnとJudge Evidenceを別Labelで表示し、同一IDの重複に見せない。

上記4項目は中心Reworkへ直接付随するため、最小変更に限りPhase 6最終差分へ前倒しする。その他はPhase 9へ維持する。

2026-08-29 UI-only Overrideで上記4項目を修正し、関連Frontend Test 54件とBuildがPASSした。Phase 6中心機能のFAILとは分離する。

User実画面で次を確認済みである。

```text
RESOLVED: Sidebar
  main.qwen3-4b-q4-k-m active
  local.macos-arm64 • gpu • metal

RESOLVED: Current Guardrail Model
  未設定

RESOLVED: Mode適用Failure
  Code／Reasonを保持し、再読込後も消えない

RESOLVED: Historical Recording
  過去／未照合のTurn記録
  過去／未照合のJudge Evidence記録
  を同一Request IDでも区別
```

上記解決済み4件を将来Reworkで元へ戻さない。UF-UI-001の残件はLayout、順序、Control幅、Button位置、区切り線、OFF時Current／Historical Presentationおよび原因別Fallback文面である。

### UF-UI-004 — Markdown／Raw HTML Presentation

```yaml
status: deferred_user_reproduced
severity: minor_to_moderate_presentation
priority: P2
closure_blocker: false
impact_scope: assistant_message_markdown_html_rendering
deferral_target: Phase_9_closure_before_or_Phase_10_ui
reopen_condition: markdown_presentation_cleanup_start
```

DeepSeek回答に含まれた`<ul><li>Mg²⁺</li></ul>`が期待するListとして表示されなかった。Raw HTMLを安全に許可するか、HTMLをTextとして扱いMarkdownへ変換するかをPresentation Policyと合わせて決める。Phase 6中心機能は止めない。

### UF-UI-005 — Local Corpus Operation Message残留

```yaml
status: deferred_user_reproduced
severity: trivial_ui
priority: P2
closure_blocker: false
impact_scope: local_corpus_settings_feedback_message
deferral_target: opportunistic_UI_cleanup_or_Phase_10_late_UI
reopen_condition: local_corpus_settings_ui_cleanup
```

`Documentを更新しました。`および`Documentを削除しました。`が設定画面を閉じても消えない。CRUD、Data、
CitationおよびPersistenceは正常であるためPhase 7 Closureを止めない。設定Close、次操作または適切なTTLで
Message StateをResetする候補とする。

### UF-UI-006 — Buffered回答のProgressive Presentation一般化

```yaml
status: deferred_user_reproduced
severity: usability
priority: P2
closure_blocker: false
impact_scope: no_hit_grounding_judge_repair_and_buffered_answer_presentation
deferral_target: Phase_9_progressive_presentation
reopen_condition: phase_9_streaming_and_enforce_presentation_work
```

NO_HIT等の一部経路が回答を一括表示する。UF-UI-003のENFORCEだけに限定せず、原則として回答生成、取得、
検証、Repairおよび確定をBlock／State単位で段階表示し、単純な一括表示をDefault UXにしない。
NO_HIT Citationは先に表示しても消さず、最終回答と共に保持する。

### UF-UI-002 — Context／Max New Tokens／Hardware Profile

```yaml
status: deferred
severity: moderate_usability
priority: P2
closure_blocker: false
impact_scope: runtime_context_configuration
deferral_target: Phase_9_closure_before_or_Phase_10_hardware_profiles
reopen_condition: profile_validation_or_phase_9_ui_contract_work
```

含む項目：

- Local Macで`Context 8192 / 16384`、`Max New Tokens 2048 / 8192`候補を実測してからProfile昇格。
- Model Native／Backend／Deployment Verified／Effective上限の意味を分離表示。
- Model別Context設定保持または切替時Default復帰を仕様化。
- Hardware自動検出はPhase 10以降。現状はHardware別Profile。
- Qwen 40960、DeepSeek 131072等の理論上限をLocalで無検証のまま選択可能にしない。

### UF-UI-003 — ENFORCE Progressive Presentation

```yaml
status: deferred
severity: usability
priority: P2
closure_blocker: false
impact_scope: streaming_judge_repair_presentation
deferral_target: Phase_9_start
reopen_condition: phase_9_progressive_enforce_presentation_work
```

Candidateを未検証の最終回答として見せず、生成中／確認中のProgressive表示を行い、検証後に確定、置換またはFallbackへ収束する。規定値はProgressive方式。単純な一括表示を最終UXにしない。

### UF-P9-001 — Internal Execution ObservabilityをCurrent UIから確認できない

```yaml
status: reserved_timing_unknown_mvp_non_blocking
severity: research_observability
priority: P2
closure_blocker: false
impact_scope: model_judge_guard_repair_tool_lifecycle_execution_trace
deferral_target: timing_unknown_after_mvp_or_future_research_trace_ui
reopen_condition: observability_ui_design_start_or_internal_execution_proof_is_needed_in_live_experiment
reservation: ../history/planned_work/phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_ja_20260901180418.md
```

Model／Artifact／Manifest Identity、Stage別Preflight〜Evidence Projection、Call 0、Worker Drain、Late Result 0、Exactly-once Release、Cancellation Token、Candidate Identity、Deadline／Budget／Repair回数等はSource／Automated Test上のAcceptanceであり、Current UIに専用表示がない。

研究用Platformとして将来表示価値はあるが、既存Settingsは既に情報量が多い。MVPを優先し、通常画面へ全件を直書きせず、将来のResearch Trace、詳細Drawer／右PanelまたはExportable Evidenceとして段階表示する。実装時期は未定とする。

### UF-P9-002 — Selene Activation後のJudge `unavailable`とMain-shared Lifecycle不安定

```yaml
status: open_user_reproduced_common_judge_substrate_first_hypothesis
severity: major_phase_9_1_core_runtime
priority: P0_for_phase_9_1_completion
closure_blocker: true_for_phase_9_1
impact_scope: selene_judge_main_shared_role_lifecycle_budget_deadline_cancellation
deferral_target: next_phase_9_1_bounded_rework
reopen_condition: immediate_next_phase_9_1_rework
reservation: ../history/planned_work/phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_ja_20260901180418.md
latest_evidence: ../../phases/phase_9/history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md
```

SeleneはUI上`Active／State active`へ到達するが、Judgeは`selected 32／evaluated 0／unknown 32／failure unavailable`となり、実用可能なJudge結果へ到達しない。さらにSelene使用後のMain-shared Qwenで`The model is not loaded`が生じ、Server Restartで回復する可能性が観測された。

これはPCスペックだけへ帰属しない。Seleneの実Inference／Decode／Result、Role切替、Unload、Lease、Cancellation、Batch、Whole-stage Budget／Deadlineを次のBounded Reworkで切り分ける。Seleneをいつでも実用できる状態はPhase 9-1成立条件のまま保持する。

2026-09-02の再確認では、Seleneを使用していないCleanなMain-shared QwenもOBSERVE／ENFORCE双方で`malformed_output`となり、Built-in Deterministicも`selected 32／evaluated 0／not_applicable 32／deferred 77`で確定判定を返せなかった。三Providerの直接Failureは異なるため同一Root Causeとは断定しないが、個別Model修正より先に共通Judge基盤を横断診断する。

### UF-P9-003 — Local Mac向け軽量LLM-as-a-Judge候補

```yaml
status: authorized_next_phase_9_1_entry_candidate_selection
severity: performance_and_research_usability
priority: P0_sequence_entry_for_next_phase_9_1_rework
closure_blocker: false_if_selene_and_main_shared_are_stable
impact_scope: local_judge_model_selection_latency_memory_structured_output
deferral_target: next_phase_9_1_package_if_resource_permits_or_later_model_research
reopen_condition: quota_recovery_and_next_phase_9_1_exact_authority
reservation: ../history/planned_work/phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_ja_20260901180418.md
```

Selene 8B Q5_K_MはUser Macで非常に重い。Seleneを修復して選択肢として残しつつ、より軽量な独立Judge候補を比較する。既存Judge Port／Lifecycle Contractを再利用できれば小〜中規模候補だが、Artifact取得、License、Prompt／Decoder差分およびReal Local Smokeは別途必要である。

2026-09-02 User Decisionにより、AI利用可能量回復後の次Packageは軽量Judge候補の選定／取得から開始する。軽量Judge追加だけでSelene、Main-shared、Built-inまたは共通Judge基盤を解決済みにせず、四Provider比較Matrixの一対象として使用する。

### UF-P9-004 — Main Runtime Governance Semantic ENFORCE未成立

```yaml
status: open_user_reproduced_phase_9_1_core_blocker
severity: critical_phase_objective
priority: P0_for_phase_9_1
closure_blocker: true_for_phase_9_1
impact_scope: ARGD_DAGD_semantic_109_main_runtime_governance_enforce
deferral_target: immediate_next_phase_9_1_bounded_rework
reopen_condition: immediate
manual_evidence: ../../phases/phase_9/history/operations/phase_9_1_user_mac_full_manual_result_unresolved_and_reservation_evidence_ja_20260901184023.md
```

User ManualではMain Runtime GovernanceをOBSERVEでのみ実行し、pre／postともSemantic 109件が全件Deferredのままだった。ARGD／DAGDを含むLive Criterion実評価、Supported Semantic ActionおよびMain Runtime Governance ENFORCE Golden Pathは成立も確認もしていない。

これはUI Polishまたは将来Hardeningではなく、MARGPA Runtime LLMのPhase 9-1中心目的である。Selene／Main-shared Judge安定化、Semantic実評価、Judge→Repair→RejudgeおよびMain ENFORCEを一つの中心経路として完了するまでPhase 9-1を閉じない。

### UF-P9-005 — Qwen3Guard ENFORCE Refusalの本文／Warning重複

```yaml
status: open_user_reproduced_minor_presentation_deferred
severity: minor_ui_presentation
priority: P2
closure_blocker: false
impact_scope: guardrail_enforce_refusal_and_warning_presentation
deferral_target: opportunistic_ui_cleanup_or_later_presentation_work
reopen_condition: guardrail_failure_presentation_cleanup
manual_evidence: ../../phases/phase_9/history/operations/phase_9_1_user_mac_full_manual_result_unresolved_and_reservation_evidence_ja_20260901184023.md
```

Qwen3Guard ENFORCEはPrompt InjectionをMatch 1／Action 1で拒否したが、同じRefusal文をAssistant回答とWarningへ二重表示した。Guard Enforcement自体は成立しているためPhase 9-1中心Blockerにせず、表示整理へ延期する。

### UF-P9-006 — Dev Agent Fixture一覧へ`.DS_Store`が現れる

```yaml
status: observed_hold_no_current_fix_request
severity: trivial_fixture_presentation
priority: P3
closure_blocker: false
impact_scope: dev_agent_fixture_workspace_list_files
deferral_target: opportunistic_fixture_cleanup
reopen_condition: fixture_listing_cleanup_or_hidden_file_policy_design
manual_evidence: ../../phases/phase_9/history/operations/phase_9_1_user_mac_full_manual_result_unresolved_and_reservation_evidence_ja_20260901184023.md
```

Dev Agent `list_files`は実File Fixture Workspaceから`.DS_Store`も返した。Userは修正要求ではなく保留観測とした。Hidden File PolicyまたはFixture Cleanupを行う時まで変更しない。

### UF-P9-007 — 全Judgeの実用判定不成立と共通Judge基盤回帰仮説

```yaml
status: open_user_reproduced_phase_9_1_p0_bounded_rework
severity: critical_phase_objective
priority: P0_for_phase_9_1
closure_blocker: true_for_phase_9_1
impact_scope: built_in_main_shared_selene_lightweight_judge_common_pipeline
deferral_target: immediate_after_ai_quota_recovery
reopen_condition: quota_recovery_and_exact_rework_handoff
evidence: ../../phases/phase_9/history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md
```

2026-09-02の実画面では、Main-shared QwenがOBSERVE／ENFORCE双方で`malformed_output`、Built-in Deterministicが`evaluated 0`となり、確定Judge結果を返さなかった。前日のSelene `unavailable／evaluated 0`と合わせ、現時点で利用可能なJudge経路はない。

直接Failure CodeはProviderごとに異なる。したがって「全Modelが同じ理由で壊れた」と断定せず、Criteria Selection、Semantic Snapshot、Prompt Build、Inference Result、Strict Decode、Result Projection、Recording、Role Lifecycle、Mode TransitionおよびCancellation／Deadlineを共有経路として先に比較する。

Guardrail ON／OFFで結果が変わらないため、Qwen3Guardは今回のJudge不成立原因から分離する。軽量Judge取得後、Built-in／Main-shared／Selene／軽量Judgeの同一条件Matrixを作り、共通層修復、Provider固有修復、Judge→Repair→Rejudge、Semantic実評価、Main Runtime Governance ENFORCEの順で完了する。

## 9. Phase 10以降のHardening／条件付き課題

### UF-HARD-001 — Hardware自動検出とContext自動昇格

```yaml
priority: P3
closure_blocker: false
deferral_target: Phase_10_or_later
reopen_condition: multi_hardware_deployment_profiles_begin
```

### UF-HARD-002 — Enterprise級Audit／Provenance／Anti-corruption

```yaml
priority: P3
closure_blocker: false
deferral_target: Phase_10_or_later
reopen_condition: productization_external_users_or_enterprise_deployment
```

Hash Chain、WORM、完全Provenance、破損Manifest耐性、長期運用のRace網羅等は、PoC主経路を止めない限りこの区分へ送る。

## 10. 2026-08-29 Phase 6 User Manual — Exact未解決Inventory

次はUser実画面で再現したまま、技術的には未解決である。Phase 7進行を選択したことによって解決済みへ変更しない。

| ID | 未解決内容 | 実画面Evidence | 影響 | 延期判断 |
|---|---|---|---|---|
| UF-P6-002-A | Selene実Activation | Configured Selene／Active none／`dedicated_model_authority_unavailable` | 独立Judge不能 | User Overrideで延期 |
| UF-P6-002-B | Qwen3Guard実Activation | Configured Qwen3Guard／Active none／Mode適用失敗 | Model Guard不能 | User Overrideで延期 |
| UF-P6-003-A | Semantic 109件の実評価 | Main pre／postともDeferred 109 | MARGPA GD意味Rule未実行 | User Overrideで延期 |
| UF-P6-003-B | Built-in Deterministicの能力不足 | selected 32／evaluated 0／not_applicable 32／deferred 77 | Semantic Judgeの代替不能 | User Overrideで延期 |
| UF-P6-004-A | Judge Golden Path | 判定unknown／confidence 0 | 回答品質判定不能 | User Overrideで延期 |
| UF-P6-004-B | Repair／Rejudge Golden Path | ENFORCEでもSafe Fallbackのみ | 修復回答を生成・採用できない | User Overrideで延期 |
| UF-P6-004-C | Main Governance意味ENFORCE | Semantic全件Deferred | 構造Rule以外を強制できない | User Overrideで延期 |
| UF-P6-004-D | 原因別Fallback文面 | Built-in能力不足でも`判定結果を確定できませんでした。` | 研究原因をUserが判別しにくい | Phase 9 UI／Observability |
| UF-P6-010-A | Qwen回答品質 | 天音かなた等で根拠なき誤答・訂正拒否 | Model品質／Grounding不足 | Phase 7 Web／RAG後に再評価 |
| UF-P6-010-B | DeepSeek回答品質 | 誤答、矛盾、過去に病的反復 | Model／量子化／Prompt切り分け未完 | Phase 7後または別Provider |
| UF-UI-001-A | Judge OFF時のCurrent／Historical Presentation | 表示意図がUserに分かりにくい | Observability UX | Phase 9 Closure手前 |
| UF-UI-001-B | Advanced Mode Layout残件 | 順序、幅、Button位置、区切り、Research Mode表示 | UI整合性 | Phase 9 Closure手前 |
| UF-UI-002 | Context／Max Token／Hardware Profile | 8192上限、8191表示、Model別保持等 | Local性能／設定UX | Phase 9／10 |
| UF-UI-003 | ENFORCE Progressive Streaming | ENFORCEで一括表示 | UX／待機体験 | Phase 9冒頭 |
| UF-UI-004 | Markdown／Raw HTML | `<ul><li>Mg²⁺</li></ul>`が期待表示にならない | Presentation | Phase 9／10 |

次は同じManual Cycleで確認済みのため未解決から除外する。

```text
RESOLVED: Sidebar 2行表示、Context混入除去
RESOLVED: Current Guardrail Model 未設定
RESOLVED: Mode適用Failure Code／Reason永続表示
RESOLVED: Historical Turn／Judge Evidence別Label
PASS: Main Qwen→DeepSeek→Qwen切替、再起動後Qwen
PASS: Conversation／Reload／別Tab継続
PASS: Recording Request相関
PASS: Stop後Cancelled、遅延回答／Evidence追加なし
```

## 11. Update Rule

Findingを追加・変更する場合：

1. Stable本書を現行判断へ更新する。
2. 重要なReclassification、Phase ClosureまたはPhase移行時に、`docs/project/shared/history/未解決/`へ新規Snapshotを作る。
3. Historical Snapshotは変更しない。
4. 解決したFindingは削除せず、Statusを`resolved`へ変更し、Resolution Evidenceを示す。
5. P0追加時は、再現経路、User影響、次Phaseへ送れない理由、最小修正Scope、概算Resource Costを必須とする。

## 12. Current Immediate Decision

- 2026-08-29 User ManualによるPhase 6中心機能の`FAIL／ADJUST`は隠蔽せず保持する。
- Userは影響を承知の上で、Selene、Qwen3Guard、Semantic 109、Judge／RepairのReworkを延期し、Phase 7へ進むことを明示決定した。
- 2026-08-29時点でPhase 6中心Debtを新Phase 10へ移管した判断はHistoryとして保持する。その後のUser再編により、Current移管先はPhase 9-1へ変更された。
- Dedicated Selene／Qwen3Guard、GD Semantic Live Evaluation、Judge／Repair Golden PathおよびMain Semantic ENFORCEは、解決済みとせずPhase 9-1で有界Reworkする。Phase 10はAll-Docs、Shared Constitution、PADG、Full Runtime ConstitutionおよびUI統合を担当する。
- Phase 6を技術的完全または中心Acceptance PASSとは主張しない。
- 指定された4件の小UI修正だけを完了し、新しいPhase 6 Hardening／機能Reworkを追加しない。
- P1以下は本Registryを保持したままPhase 6 Closure可能とする。
- 未解決0件や理論完全性はPhase 6 Closure条件ではない。
- Phase 7のLocal Corpus、Data Controls基礎およびWeb Security Portは成立済みBaselineとして保持する。
- 2026-08-29、Userは実Web Provider、External Network、Manual EvidenceのChat／Citation接続、Server Canonical OFF、外部送信Consent Enforcement、一般URL FetchおよびHostile-site処理をPhase 11以降へ延期した。
- Phase 7はGeneral Web SearchまたはWeb-grounded Chatの完成を主張しない。FixtureはTest／Research Scaffold、External Providerは`none`相当、Activationは`disabled／OFF`相当、External Network Callは0として扱う。
- P7-CODEX-001〜005は解決済みにせず、Phase 11以降の`Governed External Web Knowledge Runtime`で再開する既知Debtへ再分類する。
- 2026-08-30 User ManualでLocal Corpus CRUD、Current Retrieval、Revision更新、削除後NO_HIT、Citation Identity／Copy、Reload／Restart／別Tab、Project Docs CitationおよびData ControlsがPASSした。
- 削除済みFactのRAG OFF再出力はCurrent Retrieval残留ではなくConversation Context再利用であり、UF-P7-003としてPhase 9へ送る。
- 一時的なロシア語出力、Operation Message残留およびBuffered一括表示はUF-P7-004／UF-UI-005／UF-UI-006として記録し、Phase 7 Closureを止めない。
- Phase 7 MVPはUser Manual Acceptance PASSとしてFormal Closure可能である。
- Phase 7 Closure前に、Docs、UI Claim、Acceptance Dispositionおよび未解決Registryが実Web未実装を正直に表現していることを確認する。
- Automatic Trigger、Enterprise Hardening、汎用Attachment、Phase 6 Debtまたは実WebProvider選定をPhase 7へ再混入させない。
- P8-RW7でConstitution Previewの3軸比較を実装し、P8-CODEX-012はController Targeted Review PASS、P8-ACC-021はPASSへ戻した。
- P8-CODEX-012を理由とする追加Rework／追加Full Review Cycleは開始せず、Phase 8 User Manual Acceptanceへ進む。
- P8-CODEX-011はFrozen Envelope表示の非Blocking Truthfulness Gapとして保持し、Phase 8 Closureを止めない。
- P8-CODEX-009はCompletion Transition／Manual差、P8-CODEX-010はTest Hermeticity Debtとして保持し、独立したPhase 8 Closure Blockerにはしない。
- P8-CODEX-009はCompletion Gate Rework後のUser Manualで再判定し、P8-CODEX-010はP8-ACC-039をPASSへ捏造せず既知FAILとして開示する。
- Phase 8 User Mac Manual Web Segment 1では、Example Domain、Citation PersistenceおよびLoopback拒否はPASSした。
- 同Segmentで、通常Public URLの取得失敗、Specific Reasonの`url_rejected`集約およびFetch失敗後の非Grounded回答を再現した。
- UF-P8-005をManual URL MVPのP0候補として保持し、Bounded FixまたはUserによる明示的なScope再分類なしにPhase 8 Closureへ進まない。
- Raw HTML Context Budget FailureはUF-P8-006、専用URL欄と通常ComposerのUX差はUF-UI-007としてPhase 11／Phase 10へ予約する。
- Phase 8 User Mac Manual Segments 2〜5でArchive State非同期、Web Citation必須Field不足、Dev Agentの非追跡ApprovalとButton Contrastを再現した。
- UF-P8-008／009／010をBounded ReworkとUser再確認までClosure Blockerとする。
- Constitution SemanticsはPASSのまま保持し、UF-UI-009の改行だけを同Reworkで直す。
- General Keyword SearchはFixtureのままとし、実Search API／SearXNG／Automatic SearchをPhase 8へ戻さない。
- Dev Agentは任意File Toolへ拡張せず、Configured Runtime Data Root内の固定Fixture Workspaceだけを実File化する。
- P8-MR0〜MR8後のUser再確認で、Manual URL UTF-8 Public Page、Fail-closed Grounding、Context Budget、Web Citation、Archive、Constitution LayoutおよびDev Agent実File Fixtureの中心経路はPASSした。
- P8-MR9後のUser実画面で、Completion Gate Reason、Composer Web Failure警告Lifecycle、Untrusted Label注意色およびCompleted後Demo Run Button色の4件を全てPASSした。
- Untrusted Labelの注意色はUserがWhite／Dark双方で採用を決定したため、Controllerの同色化提案を実行しない。
- Model Call 0のUI Observability、Shift_JIS／x-sjis、Settings結果残留、Manual URL Card整理およびFalse-positive RAG Groundingは解決済みとせず、それぞれPhase 9／10／11へ送る。
- Dev Agent Capability Restart State、Per-purpose Consent Restart PolicyおよびEnglish Retention Localizationは新規未解決として保持し、Phase 8 Closureを止めない。
- Phase 8最終Dispositionは`39 PASS／1 PARTIAL／40 TOTAL`である。P8-ACC-038のGD／Guard相関だけをFoundation境界の既知PARTIALとしてPhase 9へ渡す。
- Phase 8は2026-08-31 User判断により`COMPLETE／ACCEPTED／CLOSED`とする。未解決0件、正式Agent Level 1、General Search、Generic MCPまたはProduct HardeningをClosure条件へ追加しない。
- Phase 9は9-1／9-2／9-3の3 Program設計をFreezeし、`READY／NOT STARTED`とする。User Backup後にPreflightへ進む。
- 2026-09-01 Phase 9-1 User Mac Manualは実行完了したが、結果は`FAIL／ADJUST`でありPhase 9-1を閉じない。
- Qwen3Guardの基本OBSERVE／ENFORCE／OFFはUser-visible中心経路でPASSした。
- SeleneはUI上Activeへ到達したがJudge `unavailable／evaluated 0`であり、実用成立していない。
- Main-shared Qwen Judgeは`malformed_output`、Selene／Role切替後は`The model is not loaded`を再現し、Server Restartで回復したためLifecycle Reworkを必要とする。
- Semantic 109はMain pre／postとも全件Deferredを継続し、Main Runtime Governance ENFORCEはManualから脱落して未成立である。UF-P9-004をPhase 9-1 P0として扱う。
- 2026-09-02再確認ではMain-shared QwenがOBSERVE／ENFORCEとも`malformed_output`、Built-in Deterministicが`evaluated 0／not_applicable 32／deferred 77`となり、JudgeはProvider横断で実用不成立だった。
- Selene、Main-shared、Built-inの直接原因が同一とは断定しない。Provider別修正前に共通Judge基盤を第一仮説として横断診断する。
- AI利用可能量回復後は軽量独立Judge候補を選定／取得し、Built-in／Main-shared／Selene／軽量Judgeの比較Matrixを作る。
- 修復順序は、共通Judge基盤、Provider固有差分、Judge OBSERVE／ENFORCE、Repair／Rejudge、Semantic実評価、ARGD／DAGDを含むMain Runtime Governance ENFORCEとする。
- 現時点でUserの追加Manual Actionはない。Quota回復前に新しいModel取得、Source ReworkまたはGD系ENFORCE試験へ進まない。
