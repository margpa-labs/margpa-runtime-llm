# Phase 2-A Implementation Handoff

```yaml
handoff_id: phase_2_a_implementation_handoff
revision: exact_1
status: active
created_at: 2026-08-12 01:51:52 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2実装者役
work_unit: P2-A-WU-002
```

## 1. Objective

Frozen Requirements／Architecture／ADRに従い、既存Phase 1 Runtimeを変更せず、Conversation DomainとStorage Portを新規Packageとして実装する。

## 2. Required Inputs

- [Requirements](../requirements/phase_2_a_conversation_domain_requirements_ja.md)
- [Architecture](../architecture/phase_2_a_conversation_domain_architecture_ja.md)
- [ADR](../adr/phase_2_a_conversation_domain_adr_ja.md)
- [Authorization Envelope](../governance/phase_2_a_implementation_authorization_envelope_ja.md)
- [Execution Plan](../operations/phase_2_a_execution_plan_ja.md)

## 3. Exact Source Scope

新規作成だけを行う。

```text
src/margpa_runtime_llm/modules/conversation/domain/__init__.py
src/margpa_runtime_llm/modules/conversation/domain/errors.py
src/margpa_runtime_llm/modules/conversation/domain/identity.py
src/margpa_runtime_llm/modules/conversation/domain/models.py
src/margpa_runtime_llm/modules/conversation/ports/__init__.py
src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
tests/unit/conversation/test_conversation_domain.py
tests/unit/conversation/test_conversation_store_contract.py
```

## 4. Existing Source Deny

`conversation/contracts.py`、`conversation/public.py`、`conversation_generation.py`、Web、Bootstrap、Static UI、Config、DependencyおよびLockfileを変更しない。

## 5. Implementation Requirements

- Opaque typed Identity。
- UTC-aware Timestamp。
- Immutable Message／Session／Turn／Snapshot。
- Aggregate-wide invariants。
- 1 Turn = 1 User + 0/1 Assistant。
- Retry／Regenerateは新Turn。
- Completed BranchだけのGeneration Projection。
- Store-owned CAS Revision／Operation Idempotency。
- Typed Domain／Storage FailureとMutation Outcome。
- Repository／Maintenance Protocol。
- Concrete Storage I/O 0。
- Public／Basic Preview Binding 0。

## 6. Test Requirements

- Identity／Timestamp／Unknown Field。
- Aggregate／Branch／Transition全境界。
- Projection／Privacy非保存境界。
- CAS／Idempotency／Unknown Outcome／Scope Isolation。
- Schema／Corruption／Migration Fail-closed。
- Existing Conversation／Web Regression。
- Ruff／Mypy／Full Pytest。

## 7. Stop／Escalation

既存Source変更、Dependency変更、Concrete I/O、Root外、Git／External／Secret／Destructive、Phase 2-B実装またはFrozen Decisionの意味変更が必要なら停止する。Exact Scope内の実装・Test修正は実装者が自律解決する。

## 8. Status Contract

完了時に新規Append-only Statusへ次を記録する。

```text
Source Files Created
Existing Files Modified
Tests Added
Target Test Result
Regression Result
Static Result
Concrete I/O Count
Scope Deviations
Technical Blockers
Next Exact Action
```
