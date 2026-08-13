# Phase 2-A Conversation Domain Foundation Execution Plan

```yaml
document_id: phase_2_a_execution_plan
status: active
phase: phase_2
subphase: phase_2_a
created_at: 2026-08-12 01:51:52 JST
owner: プロジェクト責任者兼設計統括者役
automation_level: bounded_unit_chained
completion_line: phase_2_a_closure_recommendation
```

## 1. Goal

Conversation Domain／Storage Boundaryを実装・検証し、Phase 2-Bが曖昧なIdentity、State、Projection、CAS、SchemaまたはFailureへ依存しない状態を作る。

## 2. Work Units

### P2-A-WU-001 — Design Freeze

- Existing v1 As-built／TestのCompatibility Review
- Requirements／Architecture／ADR Freeze
- Storage／Failure／Migration Contract Freeze
- Exact Envelope／Implementation Handoff作成
- Index／Checkpoint更新

Exit: `DESIGN_FROZEN／IMPLEMENTATION_READY`

### P2-A-WU-002 — Domain／Port Implementation

- New Domain／Port Packageだけを追加
- Identity／Aggregate／Transition／Projection Contract実装
- Repository／Maintenance Protocol／Failure型実装
- Unit／Contract Test実装
- Target Test／Static Check
- Implementer Status／Controller Review作成

Exit: `IMPLEMENTED／TARGET_VALIDATED`

### P2-A-WU-003 — Compatibility／Closure

- Existing Conversation／Web Regression
- Full Test／Static Check
- Source Scope／Git Diff／Artifact Check
- Phase Index／Roadmap／Handoff同期
- Phase 2-B Entry Handoff
- Closure Recommendation `GO／ADJUST／STOP`

Exit: `USER_FINAL_ACCEPTANCE_PENDING`

## 3. Checkpoint Rule

各Work Unit完了時に次を更新する。

- `phase_index_ja.md`のCurrent State／Restart Point
- Append-only Operation Receipt
- Documentation Index Snapshot
- Source／Test／Git Mutation Summary
- 次のExact Work Unit

利用可能量等で中断する場合、最後に合格したTest、未実施Check、変更File、次CommandおよびTechnical BlockerをStatusへ残す。

## 4. Review Rule

Findingは次で処理する。

```text
Current Transitionへ直接必要
and 今未解決
and Controller権限内で解消不能
and 放置するとSafety／Integrity／Authority／Reversibilityを破壊
  -> CURRENT_BLOCKER

Controller責任内で次工程に処理可能
  -> CONTROLLER_OWNED_NEXT_WORK

Trigger未到来の将来検証
  -> DEFERRED_EVIDENCE
```

Accepted／Closed Workを新EvidenceなしにBlockerへ戻さない。Controller職務をHuman Decisionへ返さない。

## 5. Final Output Contract

```text
Closure Recommendation: GO | ADJUST | STOP
Technical Blockers: NONE | exact list
Controller-owned unfinished work: NONE | exact list
Deferred evidence: count／current impact
Validation: exact results
Mutation boundary: exact results
User action required:
  1. Phase 2-A Final Acceptance
  2. Backup／Checkpoint
  3. Phase 2-B Start Authorization
```

## 6. Related Documents

- [Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- [Authorization Envelope](../governance/phase_2_a_implementation_authorization_envelope_ja.md)
- [Implementation Handoff](../handoffs/phase_2_a_implementation_handoff_ja.md)
