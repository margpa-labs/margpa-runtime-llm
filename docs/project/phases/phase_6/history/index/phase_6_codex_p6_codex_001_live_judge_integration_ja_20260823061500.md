# P6-CODEX-001 Live Evaluation／Judge Integration — Rework Complete

```yaml
document_id: phase_6_codex_p6_codex_001_live_judge_integration
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_001_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 06:15:00 JST
```

## 設計判断（着手前の調査結果）

```text
既存judge_prompt_builder.build_judge_prompt()はEvaluationCase.reference
（Optional）が既にNoneをサポートし、Prompt内で"unknown"扱いを明示する
設計だった（Phase 6-D-WU-003時点で既に実装済み）——Dataset Evaluation用に
設計されたPhase 6-C/D Domain層が、Ground Truthを持たないLive Conversation
Judgingにもそのまま再利用可能であることを確認し、新規Domain Contractの
追加は行わなかった（既存Testに触れず、既存Contractへの信頼を維持）。

Hook挿入位置: ConversationGenerationSession._completed_event()内、
Governance Post-check・Guardrail Post-check両方がAllowした直後（Reject時は
Judgeを一切呼ばない）。この1箇所への追加により、Ephemeral／Persistent
Chat両方（共通のConversationGenerationSessionを使う）へ同時に配線される。

非同期実行: Judge本体（Prompt構築→実Model Call→Decode→Budget Gate）は
Hook内でBackground Daemon Threadとして起動する。ConversationGeneration
Session側は`yield`前にHookを呼ぶが、Hook自体は即座にReturnする（Thread
起動のみ）ため、SSE `completed` Eventの送信TimingにJudge推論時間が
一切加算されない——「Judge OBSERVEでSSEを変更しない」を内容だけでなく
Timingについても実質的に満たす設計とした。

Independence Class: 本環境に独立Judge Artifactが存在しないため、
JudgeIndependenceClass.MAIN_SELFを直接指定（resolve_judge_independence()
はRuntimeModelSnapshotを要求しRuntime Model Control機能への結合を生む
ため、Judge Live Integration自体はRuntime Model Control Feature Flagと
独立させるためにここでは使用しない）。
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
    （JudgeGovernanceComposition、build_judge_completion_hook）
  tests/unit/bootstrap/test_judge_live_integration.py（3 Test）
  tests/unit/conversation/test_conversation_generation_judge_hook.py（4 Test）
Modified:
  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
    + JudgeCompletionContext（Dataclass）、JudgeCompletionHook（型Alias）
    + ConversationGenerationSession／ConversationGenerationServiceへ
      judge_completion_hook引数追加
    + _completed_event()内で両Post-check通過後にのみ
      _invoke_judge_completion_hook()を呼ぶ
  src/margpa_runtime_llm/bootstrap/web_application.py
    + build_judge_completion_hook()呼び出し、feature_modes_enabled時のみ
      構築、ConversationGenerationServiceへ配線
  src/margpa_runtime_llm/web/contracts.py
    + WebRuntime.judge_governance_composition（Optional、TYPE_CHECKING
      Forward Reference）
  src/margpa_runtime_llm/web/feature_modes_routes.py
    + JudgeLastResultResponse／JudgeModeSnapshotResponse追加
    + judge.last_resultとして最新のLive Judge結果を投影
Modified（Test）:
  tests/integration/web/test_feature_modes_routes.py
    （既存Exact-dict Assertionへlast_result: None追加）
```

## Judge OFF／OBSERVE／ENFORCE 契約

```text
OFF   : build_judge_completion_hook()が返すHook自体がMode確認を最初に行い、
        OFFならThread起動どころかEvaluationCase構築すら一切行わない
        （test_judge_off_never_calls_the_model、実Fake Service呼び出し0を
        直接検証）。
OBSERVE: 実Model Call（Fakeで検証、実Hardwareは既存test_real_local_judge_smoke.py
        で別途検証済み）が走り、Canonical Answer／SSE Eventは一切変更
        されない（test_judge_hook_receives_the_correlated_request_user_input_and_answer
        で、Hook呼び出し後もcompleted Eventのassistant_message内容が
        不変であることを直接検証）。
ENFORCE: 同じくModel Callは走るが、TypedRecommendationがCanonical
        Completion／Safety／Authorityのいずれも決定しない（Hookの戻り値
        自体が使われない設計のため、影響する経路が構造的に存在しない）。
        Repair Eligibilityへの受け渡しはP6-CODEX-002側の統合対象として
        残る（下記Deferred参照）。
```

## Validation

```text
Backend Full: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1417 passed, 5 deselected in 62.92s（新規7 Test含む、回帰0）
Ruff: All checks passed!
Mypy: Success: no issues found in 427 source files
```

## Acceptance Cross-check

```text
P6-ACC-016（Judge OFFで追加Call／Mutation 0）: PASS
P6-ACC-017（Judge OBSERVEでCanonical Answer不変）: PASS
P6-ACC-018（Judge ENFORCEがAuthorityを直接生成0）: PASS（Hook戻り値不使用、
  構造的に不可能）
P6-ACC-019（LLM Judge Typed Decode／Unknown Fail-closed）: PASS
  （test_judge_enforce_also_runs_and_malformed_output_fails_closedで
  Malformed Output→failed／malformed_outputを直接検証、既存Decoder再利用）
P6-ACC-020（Same Artifact JudgeをIndependentと表示0）: PASS
  （MAIN_SELFを直接指定、既存resolve_judge_independence()のUNAVAILABLE
  Fallback経路を回避する設計だが、表示は一貫してMAIN_SELF）
P6-ACC-035（Request／Turn／Generation／Evaluation Run相関）: PASS
  （JudgeCompletionContext.request_id == session.request_id、
  ConversationTurn.request_idと同一値のため、既存の
  Turn.request_id永続化経路を通じてTurnとも相関可能）
```

## Deferred（P6-CODEX-002へ引き継ぎ）

```text
Typed RecommendationをRepair Eligibilityへ実際に渡す経路（resolve_repair_
eligibility()の実呼び出し）、および実New Attempt生成・Phase 4/5全Point
再通過・Rejudge・Presented Answer選択は、P6-CODEX-002固有の作業として
本Entryには含まない。JudgeGovernanceCompositionが保持するLast Resultは
現状Read-only（Status表示専用）であり、Repair Orchestratorからの実消費は
未接続。
```

## Next Exact Route

P6-CODEX-002（Bounded Repair Live Orchestration）へ進む。
