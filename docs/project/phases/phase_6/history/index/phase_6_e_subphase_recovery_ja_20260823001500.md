# Phase 6-E Subphase Recovery（Bounded Repair）

```yaml
document_id: phase_6_e_subphase_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_e
work_unit: p6_e_wu001_wu002_wu004_wu005_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:15:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/repair/**
    （domain: identifiers.py, budget.py, plan.py, result.py, errors.py, state_machine.py／
      application: repair_eligibility_resolver.py, repair_success_evaluator.py）
  tests/unit/repair/**（Domain 2、State Machine/Budget 8、Eligibility 5、Success Evaluator 4）
Modified: なし
Git Mutation: 0
```

## Work Unit対応

```text
P6-E-WU-001（Domain／Registry）      : 完了。RepairPlan／Attempt／Budget／Result、
                                        4種Strategy名（Core Hard-code回避、Adapter Registry
                                        委譲を前提としたNameのみ）。
P6-E-WU-002（Eligibility／Authority） : 完了。resolve_repair_eligibility()でGuardrail Deny
                                        が常に最優先（Mode／Recommendation／Budgetに関係なく
                                        NOT_ELIGIBLE）を保証。
P6-E-WU-003（Repair Orchestrator）    : 未実施。実Conversation Generation Flowへの統合
                                        （New Attempt生成、Phase 4/5全Point再通過、Rejudge、
                                        Presented Answer選択）が必要で、6-B-WU-006と同種の
                                        Production配線Risk。Runtime Model Control／Evaluation
                                        両方が安定した現時点で着手可能だが、本Batchでは
                                        Domain側を優先し後続へ回した。
P6-E-WU-004（Loop／Budget Prevention）: 完了（check_repair_budget()、State Machineに統合済み）。
P6-E-WU-005（Success／Degradation）   : 完了。evaluate_repair_success()でWorse／Unknownを
                                        Improvedへ捏造しないことをTestで直接検証。
P6-E-WU-006（Terminal／Persistence）  : 未実施。実Persistence層（Conversation Store）との
                                        統合Testが必要、WU-003と合わせて後続実施。
```

## Validation

```text
New Unit Test  : 19 passed（Repair Domain 2、State Machine/Budget 8、Eligibility 5、
                  Success Evaluator 4）
Full Backend   : 1341 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（382 source files）
```

## Next Exact Route

Phase 6-E-WU-003（Repair Orchestrator、実Conversation Generation Flow統合）または
Phase 6-F（Observability／Presentation／Recording）のいずれかへ進む。Runtime Model
Control（6-B）、Evaluation（6-C/6-D）、Repair Domain（6-E）が全て安定した現時点で、
実際のConversation Generation Serviceへの統合作業（6-E-WU-003、6-F全体）を優先する。
