# MARGPA Runtime LLM Phase 7 Index

```yaml
document_id: phase_7_index
document_state: complete_accepted_closed
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
authority_owner: Nazuna Research
milestone: Traceable Local Knowledge Runtime and External Web Foundation
design: accepted_frozen
implementation: bounded_mvp_complete_external_web_deferred_to_phase_11_plus
automation: complete_user_manual_pass_closed
```

## Current Decision

Phase 6は中心未解決をStable Registryへ保持する特殊最小Closureを採用した。Phase 7はPhase 6 Debtを解決済みとせず、Local Corpus、Local Evidence Grounding、Citation、Data Controlsおよび将来のExternal Web Runtimeへ接続するPort／Security ScaffoldをPoC／MVP停止線まで実装した。

Phase境界Commit／Push、ユーザー側BackupおよびPreflightは完了した。ClaudeはP7-0〜P7-IのComplete Candidateを返却し、Controller Bounded Independent ReviewでLocal Corpus／Data Controls／Web Portの成立範囲と、実Web利用経路の未成立5件を確認した。

Userは2026-08-29、Account、Credential、Cost、Privacy、Server運用、公開Demo、SSRF、Prompt Injection、Data PoisoningおよびParser Isolationを総合し、実General Web Search、一般URL Fetch、Web EvidenceのChat／Citation接続および外部送信EnforcementをPhase 11以降へ延期した。

Local Corpus、Data Controls基礎、Web Search／Fetch Port、Fixture TestおよびWeb Security Scaffoldは成立済みBaselineとして保持する。Phase 7は実Web検索またはWeb-grounded Chatの完成を主張せず、External Provider `none`相当、Activation `disabled／OFF`相当、External Network Call 0を安全な境界とする。Phase 7 Claim／Acceptance／Docsはこの境界へ整合済みである。

Claude Non-Web Closure Alignment後、P7-RW2〜RW5-EでCitation投影、Current Evidence Freshness、Manual Resume除去、NO_HIT Persistent Citation、Local Corpus Title／実保存Pathおよび配信Static Artifactを是正した。User Mac Final Manual Acceptanceでは登録／更新／削除、Current／Historical分離、Citation Identity／Copy、NO_HIT、Reload／Restart／別Tab、Data ControlsおよびArchive解除後の即時送信を確認した。

General Web Search、Automatic SearchおよびHostile-site対応はPhase 11以降へ延期する。過去Conversation Context由来の古いFact再出力、Qwen言語Drift、軽微UIおよびProgressive PresentationはStable未解決Registryへ保持する。これらを解決済みと偽らず、Phase 7は`COMPLETE／ACCEPTED／CLOSED`、Phase 8は`READY／NOT STARTED`である。

## Canonical Design

- [Requirements](requirements/phase_7_requirements_ja.md)
- [Architecture](architecture/phase_7_architecture_ja.md)
- [ADR](adr/phase_7_adr_ja.md)
- [Execution Plan](operations/phase_7_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_7_acceptance_matrix_ja.md)
- [Preflight／Start Activation Receipt](history/operations/phase_7_preflight_and_start_activation_receipt_ja_20260829173428.md)
- [Claude Exact Handoff](handoffs/phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md)
- [Claude Exact Return Handoff](handoffs/phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md)
- [Controller Bounded Independent Review](history/operations/phase_7_codex_controller_bounded_independent_review_adjust_ja_20260829215534.md)
- [External Web Runtime Phase 11以降延期Decision](history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md)
- [Claude Non-Web Closure Alignment Exact Handoff](handoffs/phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md)
- [Claude Non-Web Closure Alignment Exact Return](handoffs/phase_7_claude_non_web_closure_alignment_exact_return_handoff_ja_20260829230500.md)
- [Non-Web Scope／Acceptance Addendum](history/operations/phase_7_non_web_scope_and_acceptance_addendum_ja_20260829225200.md)
- [Controller Revised User Manual Test Sheet](history/operations/phase_7_local_corpus_data_controls_user_manual_test_sheet_controller_revision_ja_20260829230354.md)
- [Controller Non-Web Closure Alignment Review](history/operations/phase_7_codex_controller_non_web_closure_alignment_review_ja_20260829230354.md)
- [P7-RW5-E Controller Review](history/operations/phase_7_p7_rw5_e_controller_bounded_independent_review_ja_20260830181559.md)
- [User Mac Final Manual Acceptance](history/operations/phase_7_user_mac_final_rag_citation_context_freshness_manual_acceptance_ja_20260830190930.md)
- [Phase 7 Minimal Final Closure](history/operations/phase_7_minimal_final_closure_ja_20260830191806.md)
- [Phase 7 Closure／Phase 8 READY Recovery](history/index/phase_7_final_closure_and_phase_8_ready_recovery_ja_20260830191806.md)
- [Closure／READY Canonical Verification](history/operations/phase_7_closure_phase_8_ready_canonical_verification_receipt_ja_20260830191806.md)

## Entry Sequence

1. Phase 6 Special／Minimal Closure。
2. Roadmap 2種とCurrent Index更新。
3. Clean／Commit／Push、Local／Origin一致。
4. Backup。
5. Phase 7 Preflight。
6. Userの本Turnによる開始Authority確認。
7. Claude Exact HandoffでP7-0から実装開始。

## Known Inherited Debt

- Selene実Activationなし。
- Qwen3Guard実Activationなし。
- Semantic 109件Deferred。
- Built-in Judge evaluated 0。
- Judge／Repair Golden Path未成立。
- Qwen／DeepSeek回答品質未合格。
- 実General Web Search Provider未接続。
- Web EvidenceのChat／Citation接続未成立。
- Server Canonical Web OFF／Consent／PII Enforcement未成立。
- 一般URL Fetch／Hostile-site Sandbox未成立。

詳細は`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`を正本とする。

## Stop Line

Phase 7はClosedである。今後Phase 7 Sourceを再Openする場合は、User Manualで新しいCritical／Major／MVP Blockerが確認された場合に限定し、軽微なUIまたは後続研究をPhase 7へ戻さない。

P7-CODEX-001〜005は解決済みではないが、明示User Scope ReductionによりPhase 7 Closure Blockerではない。Phase 11以降の`Governed External Web Knowledge Runtime`で再開する。
