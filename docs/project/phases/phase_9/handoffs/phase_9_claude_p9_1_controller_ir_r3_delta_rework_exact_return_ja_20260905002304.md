# Phase 9-1 Judge／Governance — Controller独立Review(23:54版) IR-R3差分Rework Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../history/operations/phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 00:23:04 JST
```

## 1. Maximum Claim

`P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`

**主張しないこと(明示的除外)**:
- 32件Criterionの通常選択規模でのRejudge成立は主張しない(実測校正後も2400>2000で未成立、定量的に確認・維持)。
- Gemmaの実機ENFORCE Golden Path成立(OBSERVE/ENFORCE/Repair→Rejudge→採用/Main Governance ENFORCE)は主張しない。局所修復(Prompt Rule追加)を有界2回試行したが効果なし(否定的結果)。
- Seleneの延期(先送り)は成立していない。Gemmaの局所修復試行がUser承認済み延期条件を満たさなかったため、今回も延期は行わない。
- Phase Closureは主張しない。次Phaseへも進まない。

## 2. 対象

[Controller独立Review(2026-09-04 23:54:34 JST)](../history/operations/phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md)のIR-R3-01〜05、5項目全て。前回受理済みのDecoder／Frozen Criterion引継ぎ／UI更新は再実装していない。

## 3. Files Changed

| File | 対応Finding | 変更内容 |
|---|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | IR-R3-01, IR-R3-02 | `_plan_rejudge()`内の`count_chat_prompt_tokens()`呼出しをtry/exceptで包み、例外時はNone(Typed pre-call failure)を返す。呼出し元で、Planning完了後(Counter自体の消費時間を含む)に`_budget_exceeded()`を再チェックし、全体Wall-time Deadline超過時はRejudge Call 0で`repair_budget_exceeded_before_rejudge`を返す(Cancellation有無で共通)。`_REJUDGE_TOKENS_PER_CRITERION`を実測(実Tokenizer、32件×2 Case)に基づき150→75へ再校正。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | IR-R3-01, IR-R3-02, IR-R3-05 | Controller Probe(Counter例外、Counter 50ms/予算20ms)の正確な再現Test 2件追加。実測校正の正確性を検証するTest 4件追加(26件成立/27件境界/32件依然未成立/既存Hardcode値の動的化)。新規`_plan_rejudge()`直接呼出し4箇所へ`# type: ignore[arg-type]`追加(新規Mypy Error解消)。 |
| `tests/unit/bootstrap/test_judge_repair_rejudge_normal_enforce_save_path.py` | IR-R3-03 | 既存Judge起点Test(2件)は無変更のまま保持。新規`_build_generation_service_main_origin()`(実`RuntimeGovernanceComposition`/`SemanticRuntimeCoordinator`配線、Judge側`repair_mode="off"`)を追加し、Main起点ENFORCE Test 2件(成功/失敗)を追加。`repair_requested_by == "main_governance"`を実`JudgeGovernanceComposition`から直接検証。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | IR-R3-04 | 全面書換え。Skip判定を`is_the_tracked_gemma_evidence_refs_json_defect()`(`provider_state=FAILED`かつ`failure_reason`が`malformed_output:`始まりの場合のみ真)へ厳密化。Controllerの`-3`注入Probeを実Dispatch Engine経由で再現するFixture負例Test(`model_smoke`Marker外、通常実行)を含む6件のOracle Test追加。実機Testは1件のみ`model_smoke`維持。 |
| `config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt` | §7④ | Rules末尾へ第5項(配列の閉じ括弧を数えて確認する指示)を追加(局所修復の有界試行)。 |
| `config/judge_templates/gemma_4_e2b/manifest.json` | §7④ | Template文言変更に伴う`derived_template_sha512`/`project_contract_digest_sha512`の再計算・更新(`SelenePromptAdapter`と同一算出手順、`preflight_contract()`で検証済み)。 |

## 4. Files Deliberately Not Changed

- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py` — 今回未編集。IR-R3の指摘4件(P1/P2/P3対応)はいずれもこのFileへの変更を要さなかった。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md` — Stable文書のため直接編集していない。
- `docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。
- Frontend一式 — 今回未編集。
- 既存Handoff/Return/History File — いずれも上書きしていない(新規File作成のみ)。

## 5. Real Evidence

### 5.1 IR-R3-01 — Plannerの例外・Deadline境界(Controller Probe再現)

- Counter例外Probe: `_CounterRaisingRepairService`(Context=8192、`count_chat_prompt_tokens()`が`RuntimeError('controller_counter_failure')`を送出)を使い`attempt_live_repair()`を呼出したところ、修正前は例外がFunction外へ伝播していたはずの状況で、修正後は`result is not None`かつ`rejected_reason == "repair_rejudge_budget_insufficient"`、Candidate Call 1件のみ実行(Rejudge Call 0件)を実測確認(`test_a_counter_exception_returns_a_typed_result_never_an_uncaught_exception`)。
- Deadline Probe: `_SlowCounterRepairService`(Counter 50ms Sleep)+`RepairBudget(max_wall_time_ms=20)`で、Cancellation有無両方について`rejected_reason == "repair_budget_exceeded_before_rejudge"`、Rejudge Call 0件を実測確認(`test_a_slow_counter_exhausting_the_overall_deadline_blocks_the_rejudge_call`)。

### 5.2 IR-R3-02 — Token実測校正と32件未成立の定量化

Task所有隔離Process、実Qwen Tokenizerによる実測(実生成なし):

```text
32件Criteria、現実的な`criterion_results`応答(実ARGD/DAGD ID使用、
reason_code+evidence_refs含む): all-pass 55.3 Token/Criterion、
all-deviation 59.4 Token/Criterion。
```

`_REJUDGE_TOKENS_PER_CRITERION`を150→75(実測最悪値+約25%余裕)へ再校正。結果、EXISTING Budget(2000 Token)内で26件Criterionまで成立(`75×26=1950<=1995`)することを実証(`test_a_realistic_26_criterion_selection_succeeds_within_the_existing_budget`)。27件で境界超過(`test_a_27_criterion_selection_is_exactly_where_the_existing_budget_stops_admitting_more`)。Runtime既定の32件は再校正後も未成立(`75×32=2400>2000`、`test_the_true_default_selection_size_of_32_still_does_not_fit_even_after_recalibration`)——予算拡大・Batching機構追加のいずれも実装せず、未成立のまま維持。詳細は[新規Snapshot](../../../shared/history/unresolved_work/phase_9_1_rejudge_token_calibration_and_32_criterion_infeasibility_snapshot_ja_20260905000817.md)。

### 5.3 IR-R3-03 — Main起点の保存証明

新規Test 2件で、Judge側`repair_mode="off"`(Judge起点は構造的に不可能)の状態で、実`RuntimeGovernanceComposition.record_semantic_response()`が`REPAIR_REQUESTED`を返し、`hook_composition.last_result().repair_requested_by == "main_governance"`を直接実測確認。同一Frozen Criterion、改善回答の唯一のNormal Turnへの保存(成功時)、失敗時の旧回答非保存をいずれも実証。既存Judge起点Test 2件は無変更のまま保持(計4件、全PASS)。

### 5.4 IR-R3-04 — Gemma Smoke OracleのFixture負例検証と実機再実行

- Controllerの`-3`注入Probeを、実`SeleneSemanticEvaluator.evaluate()`経由(Model Loadのみ`RuntimeError('llama_decode returned -3')`を送出するFixtureへ置換、Dispatch/Decode Codeは無変更)で再現。結果`provider_state=UNAVAILABLE`(`FAILED`ではない)を確認し、新Oracleがこれを`False`(Skip対象外)と正しく判定することを実測(`test_a_native_crash_shaped_unavailable_response_never_matches_the_oracle`)。
- 実機Testを1回再実行(合計5回目の実機試行): 同一の`malformed_output`欠陥を再現、Nativeクラッシュは0/5のまま。生Log絶対Pathと因果Scope訂正を[新規Snapshot](../../../shared/history/unresolved_work/phase_9_1_gemma_evidence_refs_json_defect_absolute_log_paths_and_causal_scope_correction_snapshot_ja_20260905001646.md)へ記録。

### 5.5 §7④ — Gemma不正JSONの局所修復試行(有界、否定的結果)

仮説(Prompt Rule追加で閉じ括弧欠落が減る)を立て、成功条件(誤答/正答それぞれ`provider_state=ACTIVE`到達)を試行前に定義し、有界2回(誤答1回・正答1回)で実施。結果は両Caseとも生出力Textが修正前と1文字も変わらず、成功条件は不成立(否定的結果)。詳細は[新規Snapshot](../../../shared/history/unresolved_work/phase_9_1_gemma_local_prompt_repair_attempt_bounded_negative_result_snapshot_ja_20260905002008.md)。「Gemmaの能力限界」とは断定していない——今回検証したのは1つの狭い仮説のみであり、他のPrompt改善仮説は未検証のまま残る。

## 6. Focused／Static Verification

- Backend Full Suite: `uv run pytest -q` → **2311 passed, 25 deselected (78.11s)**(前回2298から+13、新規Test追加分)。
- Backend Ruff: `uv run ruff check .` → **All checks passed**。
- Backend Mypy: `./.venv/bin/mypy src tests`(Controllerと同一Command) → **43 errors, 4 files**(前回Controller指摘の47件/5 Filesから、今回編集Testの新規4件を解消し、既存43件Baselineへ復帰。既存43件は今回のScope外につき無断修復していない)。
- 実機Model Smoke(Gemma): `uv run pytest tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py -m model_smoke` → **1 skipped**(既知のTracked Defectとの一致を確認した上でのSkip、Oracle Test 6件は別途通常実行でPASS済み)。
- Frontend: 今回未変更のため再実行していない。
- Gemma/Selene関連既存Test(Manifest/Template変更の影響確認): `uv run pytest -k "gemma or selene"` → **45 passed**。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Controllerの5指摘それぞれへの適合性

- [OK] IR-R3-01: Counter例外・Deadline境界とも、Controllerの正確な合成Probe(Context=8192のRuntimeError、50ms/20ms)で再現・修正を実測確認。
- [OK] IR-R3-02: 実測に基づく校正(Fixture縮小・Criterion脱落なし)。32件は依然未成立と正直に維持、予算拡大は未実装のまま最小変更案のみ提示。
- [OK] IR-R3-03: 既存Judge起点Testを保持しつつ、Main起点固有の`repair_requested_by`検証を実配線で追加。
- [OK] IR-R3-04: Fixture負例(Controllerの`-3`Probeを実Dispatch Engine経由で再現)でOracleを先に検証、実機Testはその後。絶対Log Path・因果Scope訂正も反映。
- [OK] IR-R3-05: Controllerと同一Command(`mypy src tests`)で比較、新規4件のみ解消、既存43件は無断修復せず。

### Review B — 手続き・Append-only・Evidence整合

- [OK] Git: `git status`のRead-only確認のみ。変更操作なし。
- [OK] Append-only: 新規File(Test 2件は既存File編集、Docs 3件・Manifest/Template変更)は全て新規作成または直接のConfig編集であり、既存Handoff/Return/History Fileの上書きはない。
- [OK] Stable文書境界: Registry本体は編集せず、提案は新規Snapshotへ記録。
- [OK] Scratchpad: 全ての実行Log・診断Scriptを既定のScratchpad配下へ保存、絶対Pathを新規Docsへ記録。
- [OK] Model Load/Unload: 全実機試行で`finally`によるUnloadを確認、残存Load・稼働Processなし。
- [FIXED-DURING-REVIEW] Manifest.json変更後、`SelenePromptAdapter.preflight_contract()`のDigest検証が通ることを個別に確認(見落としていれば全Gemma関連機能が壊れていたリスクを事前に検出・確認)。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **32件Criterion Rejudge未成立**: 実測校正後も予算不足(2400>2000)。最小変更案(予算拡大またはBatching機構追加)は提示のみ、未実装・未承認。
2. **Gemma `evidence_refs` JSON欠陥**: 局所修復(Prompt Rule追加)を有界試行したが否定的結果。真因(Model/Prompt/Backend)は未確定のまま。UF-P9-010提案は継続。
3. **Selene**: 未解決のまま継続。今回のTaskでは新規実機実行なし(前Round予算を使い切っている)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外につき未着手。
5. **Frontend再検証**: 今回変更なしのため未実施。

## 9. Action Inventory

**実行した**:
- IR-R3-01〜05全項目の実装・Test追加・実行・全PASS確認。
- Gemma Prompt Templateの局所修復有界試行(2回、否定的結果)、実機再実行1回(合計5回目)。
- 新規History Snapshot 3件作成。
- Backend Full Suite・Ruff・CanonicalなMypy Commandの最終実行。
- 本Return Handoffの新規File作成。

**実行しなかった**:
- 32件Criterion成立のための予算拡大・Batching機構追加(未承認)。
- Gemma不正JSONの追加Prompt改善試行(有界Budget使用済み)。
- Seleneの新規実機実行。
- 既存Mypy 43件の無断修復。
- Git Add/Commit/Push等の変更操作。

**Temporary Artifact／Active Process／Model Load**: 全実機Trialで`finally`Unloadを確認、残存Load・稼働Processなし。Scratchpad配下のScript/Logは保持(絶対Pathを新規Docsへ記録済み)。

## 10. Exact Next Action for Codex Controller

1. IR-R3-01(Planner境界)の修正・Test(§3, §5.1, §7 Review A)を、Controller自身のProbe(Counter例外・50ms/20ms)で独立再現し、Typed Pre-call Failureとして正しく処理されることを確認する。
2. IR-R3-02(Token実測校正)を確認し、26件成立/32件未成立という定量結果、および予算拡大・Batching機構追加のいずれも未実装のまま維持している判断に同意するか判断する。
3. IR-R3-03(Main起点保存Test)を確認し、`repair_requested_by == "main_governance"`の実配線検証が十分かを判断する。
4. IR-R3-04(Gemma Smoke Oracle)を確認し、Fixture負例(`-3`Probe)によるOracle検証・絶対Log Path・因果Scope訂正が十分かを判断する。
5. §7④(Gemma局所修復の有界試行、否定的結果)を確認し、Gemma延期不成立の判断・UF-P9-010継続に同意するか判断する。
6. 上記1-5を踏まえ、本Rework全体をACCEPTするか、追加のCHANGES REQUIREDを発行するか判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
