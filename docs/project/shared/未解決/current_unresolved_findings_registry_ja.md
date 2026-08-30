# MARGPA Runtime LLM 現行未解決課題Registry

```yaml
document_id: current_unresolved_findings_registry
document_type: shared_stable_current_unresolved_findings_source
document_state: current
language: ja
created_at: 2026-08-29 10:51:39 JST
last_reclassified_at: 2026-08-30 19:09:30 JST
decision_authority: user
authority_owner: Nazuna Research
maintainer_role: プロジェクト責任者兼設計統括者役
current_project_stage: individual_poc_mvp_portfolio
current_delivery_target: phase_9_mvp_then_phase_10_portable_autonomous_development_governance_package
history_snapshot: ../history/未解決/phase_7_final_rag_context_and_ui_deferred_findings_snapshot_ja_20260830190930.md
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

## 7. Phase 9 Closure前へ延期したUI／Observability

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

## 8. Phase 10以降のHardening／条件付き課題

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

## 9. 2026-08-29 Phase 6 User Manual — Exact未解決Inventory

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

## 10. Update Rule

Findingを追加・変更する場合：

1. Stable本書を現行判断へ更新する。
2. 重要なReclassification、Phase ClosureまたはPhase移行時に、`docs/project/shared/history/未解決/`へ新規Snapshotを作る。
3. Historical Snapshotは変更しない。
4. 解決したFindingは削除せず、Statusを`resolved`へ変更し、Resolution Evidenceを示す。
5. P0追加時は、再現経路、User影響、次Phaseへ送れない理由、最小修正Scope、概算Resource Costを必須とする。

## 11. Current Immediate Decision

- 2026-08-29 User ManualによるPhase 6中心機能の`FAIL／ADJUST`は隠蔽せず保持する。
- Userは影響を承知の上で、Selene、Qwen3Guard、Semantic 109、Judge／RepairのReworkを延期し、Phase 7へ進むことを明示決定した。
- 2026-08-29、Userはこれらを新Phase 10の`Governance Semantic Runtime Completion Program`へ正式移管した。Phase 7〜9はGuardrailのBuilt-in Rule／Pattern BaseとJudgeのBuilt-in DeterministicまたはNone／OFFを暫定Baselineとする。
- Dedicated Selene／Qwen3Guard、GD Semantic Live Evaluation、Judge／Repair Golden PathおよびMain Semantic ENFORCEは、解決済みとせず新Phase 10で再開する。
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
