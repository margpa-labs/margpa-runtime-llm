# P6-CODEX-002 Bounded Repair Live Orchestration — Partial（Eligibility Live-wired）

```yaml
document_id: phase_6_codex_p6_codex_002_repair_eligibility_partial
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_002_partial_eligibility_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 06:25:00 JST
```

## Scope判断（正直な記録）

```text
P6-CODEX-002が要求する全項目のうち、本Entryで実施したのは
「Typed RecommendationをRepair Eligibilityへ渡せる」の実配線
（resolve_repair_eligibility()を実際のJudge Recommendation・実RepairMode
Controller状態で毎回呼び出す）のみである。

未実施（Controller-owned Followupとして明示）:
  - 実New Attempt生成（execute_repair_plan()の実Conversation Generation
    Flowへの接続）
  - CandidateのPhase 4 Main Governance／Phase 5 Guardrail全対象Point再通過
  - Rejudge、Before／After比較、Presented Answer選択
  - Attempt／Depth／Call／Token／Wall Time／Cancelの実運用Bound（Eligibility
    のBudget Checkは常にZero-usageの仮想値で評価しており、実際の消費追跡は
    行っていない）
  - Commit-before-completed、Terminal一意性、Ghost Completion 0の実証

理由: execute_repair_plan()を実際にTriggerするには、現在Background Daemon
Threadとして走っているJudge Hookから、Persistent Conversation Serviceの
Store Mutation（新規Turn作成・Commit）へ逆方向に手を伸ばす必要がある。
これは本Codebaseに前例のない新しいConcurrency Riskクラス（Fire-and-forget
Background ThreadからCanonical Storeへの書き込み）であり、時間的制約下で
拙速に実装するとCommit-before-completed／Terminal一意性／Ghost Completion
といったAcceptance Matrix自体が警告する不具合を誘発するRiskが高いと判断し、
本Reworkでは実装しなかった。Rushed and incorrectよりHonest and partialを
選択した。
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
    + LiveJudgeResult.repair_eligibility（Optional）
    + build_judge_completion_hook()へrepair_mode_controller引数追加
    + Judge実行後、execution_state=COMPLETEDの場合のみ実際に
      resolve_repair_eligibility()を呼び出し、結果を記録
  src/margpa_runtime_llm/bootstrap/web_application.py
    + repair_mode_controlをbuild_judge_completion_hook()へ実際に渡す
  src/margpa_runtime_llm/web/feature_modes_routes.py
    + JudgeLastResultResponse.repair_eligibility追加
Modified（Test）:
  tests/unit/bootstrap/test_judge_live_integration.py
    + 3 Test（needs_repair×Repair Enforce→eligible、
      needs_repair×Repair Off→not_eligible_mode_off、
      accept→not_eligible_no_repair_recommendation）
```

## Validation

```text
Backend Full: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1420 passed, 5 deselected in 63.80s（新規3 Test含む、回帰0）
Ruff: All checks passed!
Mypy: Success: no issues found in 427 source files
```

## Acceptance Cross-check

```text
「Typed RecommendationをRepair Eligibilityへ渡せる」: PASS（実際に毎Live
  Judge Runで呼ばれることをTestで直接検証、Structural可能性ではなく実行証跡）
P6-ACC-025（Judge ModeとRepair Mode独立）: PASS（両ControllerとModeが完全に
  別Instance、Test 3件で相互作用パターンを直接確認）
P6-ACC-027（Repair ENFORCEはRegistry／Authority／Budget内だけ）: NOT YET
  LIVE-VERIFIED（Eligibility ResolutionはBudget Checkを含むが、実Attempt
  実行自体が無いため、この保証の「実行時」検証は依然として不可能）
```

## 追記（自己発見・修正 20260823064000 JST）

```text
本Entry初版のresolve_repair_eligibility()呼び出し条件は
repair_mode_controller is not Noneのみで、Judge自身のMode（OBSERVE／
ENFORCE）を確認していなかった——OBSERVEでもneeds_repair Recommendation
がEligibility Resolutionへ渡ってしまう実Bugだった。「Judge ENFORCE:
Typed RecommendationをRepair Eligibilityへ渡せる」という要件文言はENFORCE
限定であり、OBSERVEはDownstreamへの影響0を維持すべきという原則
（Judge OBSERVEでCanonical Answer、SSE、Conversation Persistenceを変更
しない、の趣旨を Eligibility Resolutionという副作用にも適用）に反していた。

修正: judge_mode_controller.mode_snapshot().current_mode is
EvaluationMode.ENFORCEを追加条件とし、OBSERVE時はrepair_eligibility=None
のまま（Resolution自体を実行しない）ことを
test_judge_observe_never_resolves_repair_eligibility_even_with_needs_repairで
直接検証した。Full Suite 1431 passed、Ruff／Mypy Clean。
```

## Next Exact Route

P6-CODEX-004（Local Recording Adapter／Git Boundary）へ進む。実New Attempt
生成の完全実装は、Persistent Store Mutation Threading Modelの設計検討を
要する大規模Followupとして、最終Candidate Handoffで明示的にController-owned
Workへ計上する。
