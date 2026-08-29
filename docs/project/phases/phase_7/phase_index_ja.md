# MARGPA Runtime LLM Phase 7 Index

```yaml
document_id: phase_7_index
document_state: active_handoff_ready
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
authority_owner: Nazuna Research
milestone: Traceable Grounded Knowledge Runtime
design: accepted_frozen
implementation: start_authorized_waiting_executor
automation: bounded_handoff_active
```

## Current Decision

Phase 6は中心未解決をStable Registryへ保持する特殊最小Closureを採用した。Phase 7はPhase 6 Debtを解決済みとせず、RAG、Web検索、Citation EvidenceおよびData Controlsの中心経路をPoC／MVP停止線まで実装する。

Phase境界Commit／Push、ユーザー側BackupおよびPreflightは完了した。ユーザーの実装開始AuthorityによりClaude Exact HandoffはActiveであり、Current状態は`start_authorized_waiting_executor`である。

## Canonical Design

- [Requirements](requirements/phase_7_requirements_ja.md)
- [Architecture](architecture/phase_7_architecture_ja.md)
- [ADR](adr/phase_7_adr_ja.md)
- [Execution Plan](operations/phase_7_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_7_acceptance_matrix_ja.md)
- [Preflight／Start Activation Receipt](history/operations/phase_7_preflight_and_start_activation_receipt_ja_20260829173428.md)
- [Claude Exact Handoff](handoffs/phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md)

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

詳細は`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`を正本とする。

## Stop Line

Phase 7 Executorの最大Claimは`COMPLETE_CANDIDATE`。Phase 7 Closure、Git、Backup、RoadmapまたはPhase 8へ自動進行しない。
