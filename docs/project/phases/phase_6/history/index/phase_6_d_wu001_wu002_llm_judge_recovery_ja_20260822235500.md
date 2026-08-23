# Phase 6-D-WU-001／WU-002 Typed Judge Adapter／Role-separated Binding Recovery Entry

```yaml
document_id: phase_6_d_wu001_wu002_llm_judge_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_d
work_unit: p6_d_wu001_wu002_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-22 23:55:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/evaluation/domain/llm_judge.py
    （JudgeIndependenceClass／JudgeFailureReason／LlmJudgeRequest／LlmJudgeResponse）
  src/margpa_runtime_llm/modules/evaluation/application/judge_role_resolver.py
    （resolve_judge_independence()：runtime_model_controlのRuntimeModelSnapshotから
      Judge Independence Stateを投影、捏造防止）
  tests/unit/evaluation/test_llm_judge_contracts.py
  tests/unit/evaluation/test_judge_role_resolver.py
Modified:
  src/margpa_runtime_llm/modules/evaluation/ports.py（LlmJudgePort追加）
```

## 設計判断

```text
Raw Prompt非保存    : LlmJudgeRequestはprompt_digest（SHA-512）のみを持ち、実Prompt文字列
                       Fieldを持たない（6-D-WU-003要件を型で先取り強制）。
Independence判定    : Judge Binding不在／Unbound→UNAVAILABLE、Main同一Artifact→MAIN_SELF
                       （Independentと誤表示しない、P6-ACC-020）、それ以外はBinding自身の
                       independence_classに従いSHARED_ARTIFACT／INDEPENDENT_ARTIFACTを区別。
Core非依存Port      : LlmJudgePortはjudge()一つだけを要求し、Selene-1-Mini-Llama-3.1-8B等の
                       将来Dedicated Judge AdapterがCore変更なしで追加できる形を維持。
Module間依存方向     : evaluation → runtime_model_control（Read-only、Domain Contract参照のみ）。
                       逆方向依存は作らない。
```

## Validation

```text
New Unit Test  : 8 passed（LLM Judge Contract 3、Judge Role Resolver 5）
Full Backend   : 1299 passed／3 deselected（回帰0）
Ruff／Mypy      : Clean（361 source files）
```

## 未実施（後続WU）

```text
P6-D-WU-003 Rubric／Prompt／Output Decoder : 未実施（Strict Decoder、Fail-closed Malformed）
P6-D-WU-004 Calibration／Bias Matrix        : 未実施
P6-D-WU-005 Real Local Judge Experiment     : 未実施（実Qwen LoadでのReal Judge Run、
                                               model_smoke Class、6-I Real Browser前後で実施）
P6-D-WU-006 Failure／Cost Gate              : 未実施
```

## Next Exact Route

Phase 6-D-WU-003（Rubric／Prompt／Output Decoder）へ進む。
