# MARGPA Runtime LLM 未解決課題Registry — 2026-08-29 10:51:39 JST時点Snapshot

```yaml
document_id: current_unresolved_findings_registry_snapshot_20260829105139
document_type: shared_history_append_only_unresolved_findings_snapshot
document_state: frozen_snapshot
language: ja
created_at: 2026-08-29 10:51:39 JST
last_reclassified_at: 2026-08-29 10:51:39 JST
decision_authority: user
authority_owner: Nazuna Research
maintainer_role: プロジェクト責任者兼設計統括者役
current_project_stage: individual_poc_mvp_portfolio
current_delivery_target: phase_9_mvp_then_phase_10_portable_autonomous_development_governance_package
stable_source: ../../未解決/current_unresolved_findings_registry_ja.md
snapshot_semantics: exact_content_snapshot_at_creation_except_snapshot_metadata
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

## 4. Phase 6 — Current Closure Blockers

### UF-P6-001 — Mode OFF／Provider切替後の新規Role Lease拒否

```yaml
source_finding: P6-CODEX-089
status: rework_in_progress_R25_to_R28
severity: major
priority: P0
closure_blocker: true
impact_scope: Judge_Guard_role_provider_lifecycle
deferral_target: none_current_phase
reopen_condition: OFF_or_pending_unload_state_can_still_start_new_role_turn
```

Mode OFF、Provider切替、DrainまたはUnload待ちの状態でも新しいLeaseを発行できる場合、画面上のMode／Provider状態と実実行が一致しない。研究結果の誤認とUnload競合を起こすためPhase 6で閉じる。

Acceptance条件：OFF／Degraded／Pending Unload／Failed Adapterでは新規実行を拒否し、既存Turnだけが有界にDrainする。

### UF-P6-002 — Selene／Qwen3GuardのConfigured／Active／Executed一致

```yaml
source_findings:
  - P6-CODEX-046
  - P6-CODEX-048
  - P6-CODEX-062_to_068
status: implementation_advanced_real_artifact_gate_open
severity: major
priority: P0
closure_blocker: true
impact_scope: dedicated_judge_and_guard_provider_runtime
deferral_target: none_for_truthful_activation_path
reopen_condition: configured_provider_is_reported_or_used_without_matching_active_and_executed_provider
```

Selene／Qwen3Guardを選択した時、実際にLoad／Inferenceされるか、利用不能ならModeを有効化せずExact Failureへ収束する必要がある。`Active none`のままConfigured名をExecuted Evidenceへ記録してはならない。

Real Artifact品質の高度評価は延期可能だが、選択、起動、実行Identityまたは正直な失敗はPhase 6の中心機能である。

### UF-P6-003 — ARGD／DAGD Semantic 109件のLive Turn実評価

```yaml
source_findings:
  - P6-GOV-015
  - P6-CODEX-057
status: implementation_advanced_user_manual_recheck_required
severity: major
priority: P0
closure_blocker: true
impact_scope: main_runtime_governance_semantic_evaluation
deferral_target: none_current_phase
reopen_condition: live_UI_remains_Deferred_109_or_selected_criteria_have_zero_evaluated_results
```

MARGPAの中心であるGD Semantic RuleがCompile／Selected表示だけで実評価されない状態は、Phase 6の目的を満たさない。Budgetで一部Deferredになることは許容するが、実行結果とDeferred理由を正しく区別する。

### UF-P6-004 — Judge／Repair Golden PathとFail-safe

```yaml
source_findings:
  - P6-GOV-010
  - P6-GOV-017
  - P6-GOV-018
status: implementation_advanced_user_manual_recheck_required
severity: major
priority: P0
closure_blocker: true
impact_scope: live_judge_repair_presentation
deferral_target: none_current_phase
reopen_condition: obvious_evidence_contradiction_is_accepted_or_repair_path_cannot_complete_truthfully
```

実画面でJudgeが誤答を自己承認する、選択していないProviderへ誤帰属する、Repairが成立しない、Failure時にRaw Candidateを不正に通す状態はPhase 6で閉じる。

Modelが全事実を正答することはAcceptanceにしない。検証不能時に正確なFailureへ収束し、Repair成功時はCandidate／Repair／Rejudge／Presentationが相関することを求める。

### UF-P6-005 — User Mac Real Browser最終Manual Acceptance

```yaml
status: user_gate_pending_after_current_rework
severity: gate
priority: P0
closure_blocker: true
impact_scope: real_browser_real_runtime
deferral_target: none_before_phase_6_closure
reopen_condition: any_frozen_core_manual_scenario_fails
```

Source／Fixture／TestだけでPhase 6 Closureへ昇格しない。Current Rework後、Userが実画面でProvider、Semantic、Judge／Repair、Recording、Stop、継続性を確認する。

## 5. Phase 6 — Recorded but Non-blocking Findings

### UF-P6-006 — Tracked Worker Admission／Shutdown TOCTOU

```yaml
source_finding: P6-CODEX-088
status: rework_already_in_progress_R25
severity: major_if_triggered
priority: P2
closure_blocker: false_unless_current_production_path_reproduces_material_effect
impact_scope: shutdown_hardening
deferral_target: Phase_10_hardening
reopen_condition: production_shutdown_returns_clean_while_live_worker_can_mutate_or_block_unload
```

Negative ProbeでRaceは成立したためFinding自体は保持する。ただし、Current WebRuntimeの外側Drain順とUser主経路でMaterial Effectが再現しない限り、PoC Closureを止めない。

R25で既に修正中のため成果は保持するが、これを起点に追加Concurrency Hardeningを無制限に派生させない。

### UF-P6-007 — Qwen3Guard ManifestのAnti-corruption Validation

```yaml
source_finding: P6-CODEX-090
status: current_manifest_matches_pinned_official_sources
severity: major_if_manifest_corrupted
priority: P2
closure_blocker: false
impact_scope: future_contract_integrity_hardening
deferral_target: Phase_10_hardening
reopen_condition: current_manifest_or_binding_differs_from_pinned_official_contract
```

Current Checked-in ManifestはPinned Qwen公式Sourceと一致している。偽Provider、偽Protocol、偽Categoryを将来注入した場合の拒否強化は価値があるが、現PoC主経路を止めない。

### UF-P6-008 — Qwen3Guard Provider IdentityのEvidence Round-trip

```yaml
source_finding: P6-CODEX-091
status: partial
severity: evidence_major
priority: P1
closure_blocker: false_if_executed_provider_is_truthful_else_reclassify_P0
impact_scope: observability_audit_evidence
deferral_target: Phase_9_observability_or_Phase_10_hardening
reopen_condition: UI_or_evidence_misattributed_executed_provider
```

Artifact SHA、Revision、Manifest Digest等の完全Round-tripは延期可能。ただし、どのProviderを実行したかという最低限のIdentityまで誤る場合はUF-P6-002へ統合してP0とする。

### UF-P6-009 — Unload Exception後のAdapter残留

```yaml
source_finding: IR-R24-001
status: observed
severity: moderate_to_major_if_reused
priority: P1
closure_blocker: false_if_failed_adapter_cannot_receive_new_lease
impact_scope: lifecycle_failure_recovery
deferral_target: Phase_9_or_Phase_10_hardening
reopen_condition: failed_or_degraded_adapter_can_execute_new_turn
```

Adapter Mapへの残留自体は即Blockerにしない。新規Leaseが拒否され、表示がFailureを正しく示すなら延期する。再実行できる場合はUF-P6-001としてP0。

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

## 6. Phase 9 Closure前へ延期したUI／Observability

### UF-UI-001 — Advanced Mode Layout／表示整理

```yaml
source_finding: P6-DELTA-016
status: deferred
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

## 7. Phase 10以降のHardening／条件付き課題

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

## 8. Update Rule

Findingを追加・変更する場合：

1. Stable本書を現行判断へ更新する。
2. 重要なReclassification、Phase ClosureまたはPhase移行時に、`docs/project/shared/history/未解決/`へ新規Snapshotを作る。
3. Historical Snapshotは変更しない。
4. 解決したFindingは削除せず、Statusを`resolved`へ変更し、Resolution Evidenceを示す。
5. P0追加時は、再現経路、User影響、次Phaseへ送れない理由、最小修正Scope、概算Resource Costを必須とする。

## 9. Current Immediate Decision

- R25〜R28は既に開始済みのため完了まで継続する。
- その後、Controllerは新しいHardening観点を探索してReworkを連鎖させない。
- P0の機能的本丸とUser Manual Acceptanceだけを確認する。
- P1以下は本Registryを保持したままPhase 6 Closure可能とする。
- 未解決0件はPhase 6 Closure条件ではない。
