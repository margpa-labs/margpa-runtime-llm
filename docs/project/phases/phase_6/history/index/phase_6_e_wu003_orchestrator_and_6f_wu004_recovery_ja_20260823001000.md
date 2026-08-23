# Phase 6-E-WU-003（Repair Orchestrator）／6-F-WU-004（User Feedback） Recovery Entry

```yaml
document_id: phase_6_e_wu003_orchestrator_and_6f_wu004_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_e_and_6_f
work_unit: p6_e_wu003_domain_level_complete_p6_f_wu004_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:10:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/repair/ports.py（RepairAttemptGeneratorPort）
  src/margpa_runtime_llm/modules/repair/application/repair_orchestrator.py（execute_repair_plan）
  src/margpa_runtime_llm/modules/runtime_observability/domain/feedback.py
    （UserFeedback／FeedbackRating／FeedbackRequestedAction／should_trigger_action）
  tests/unit/repair/test_repair_orchestrator.py（3 Test）
  tests/unit/runtime_observability/test_feedback.py（5 Test）
Modified: なし
Git Mutation: 0
```

## Work Unit対応

```text
P6-E-WU-003（Repair Orchestrator） : Domain／Application層完了。New Attempt生成→Rejudge→
                                     Accept／Reject の状態遷移をState Machineで強制。
                                     Before／After Evaluation Run Refを区別して保持。
                                     未実施: Phase 4／5全Governance／Guardrail Pointの
                                     実再通過（P6-ACC-029）。これは実ConversationGeneration
                                     Serviceのpre/post hookへの配線が必要な、6-B-WU-006と
                                     同種のProduction統合Riskであり、明示的に別Scopeとして
                                     Docstringへ記録した（未実測をPASSと主張しない）。
P6-F-WU-004（User Feedback）       : 完了。should_trigger_action()でRatingのみでは
                                     Action Triggerされないことを直接Test（P6-ACC-044A）。
                                     No-auto-trainingはTraining Pipeline自体を実装しない
                                     （不在による保証）ことで満たす。
```

## Validation

```text
New Unit Test  : 8 passed（Orchestrator 3、Feedback 5）
Full Backend   : 1374 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（405 source files）
```

## Next Exact Route

Phase 6-G-WU-001（Sidebar Current Model、実API Route配線）、または6-H（Comparative Experiment、
既存の6-B〜6-Fが安定した現時点で着手可能）へ進む。DeepSeek依存項目は引き続きNOT EXECUTEDのまま。
