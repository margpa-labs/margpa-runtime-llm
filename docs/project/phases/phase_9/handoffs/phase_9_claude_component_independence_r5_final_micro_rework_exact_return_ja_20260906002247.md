# Phase 9-1 — Component完全疎結合 R5 Final Micro-rework Exact Return

```yaml
document_type: exact_implementation_return
document_state: ready_for_controller_review
recorded_at: 2026-09-06 00:22:47 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_component_independence_r5_final_micro_rework_exact_handoff_ja_20260906000248.md
review_target_of_this_document: docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r4_return_controller_review_ja_20260906000248.md
maximum_claim: P9_1_R5_WU01_WU02_WU03_RESOLVED_LATEST_POINTER_REWIND_ELIMINATED_GOLDEN_PATH_ORACLE_HARDENED_REAL_TRIAL_PASSED
phase_9_1_closure: false
git_mutation: none
append_only: true
```

## 1. 最大Claim

`P9_1_R5_WU01_WU02_WU03_RESOLVED_LATEST_POINTER_REWIND_ELIMINATED_GOLDEN_PATH_ORACLE_HARDENED_REAL_TRIAL_PASSED`

Codex ControllerによるR4 Return Reviewが指摘した2件の狭い残差(Latest Current Pointer再巻き戻り競合、Golden Path Oracleの薄さ)に対応した。R5-WU-01からR5-WU-03までの3件すべてを解決した。R4の解決済み実装(Request-local Ledger、Judge Identity 3経路Matrix、Cancellation Arbitration限定、Gemma Compact Schema、`context_size=8192`)は一切Rollbackしていない。

**明示的除外**: Phase 9-1 Closureは主張しない。Selene実機実行、Retry、Decoder緩和、Context/Budget/Criterion上限/Sampling/Schemaの追加変更、Phase 9-2／9-3、Phase 10、全面Rollbackには一切進んでいない。Git操作は一切行っていない。Current Registry／Phase Indexは編集していない。

## 2. 対象

- R4 Return Controller Review: `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r4_return_controller_review_ja_20260906000248.md`(Handoff冒頭で指定されたPathをそのまま参照。本Round自体はHandoffの指示どおり、Exact Handoff 1件のみを読み実施した)
- R5 Exact Handoff: `docs/project/phases/phase_9/handoffs/phase_9_controller_component_independence_r5_final_micro_rework_exact_handoff_ja_20260906000248.md`
- R5-WU-01からR5-WU-03までを順序どおり実施。

## 3. Files Changed

### Source

| File | WU | 変更内容 |
|---|---|---|
| [semantic_runtime.py](../../../../../src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py) | R5-WU-01 | `SemanticRuntimeCoordinator.begin()`の既存Entry再Hit Branchから、`self._latest_request_id = request_id`と`self._turns.move_to_end(request_id)`の2行を削除。既存`request_id`が見つかった場合は`existing.snapshot`をそのまま返すのみで、Latest Current Pointer・Ledger FIFO順序・Generation・Digest・Rotation Cursorのいずれにも一切触れない。新規`request_id`の初回`begin()`のみがLatest Current Pointerを更新する経路(既存の`self._generation += 1`以降のBlock)は無変更。Class Docstring/該当Method内Commentを、この訂正された契約(A→B→A再入はB上のCurrentを一切動かさない)を正確に記述するよう更新。 |

### Tests(新規/変更)

| File | WU | 内容 |
|---|---|---|
| [test_semantic_runtime.py](../../../../../tests/unit/runtime_governance/test_semantic_runtime.py) | R5-WU-01 | 新規Test 2件を追加。(1) `test_a_begin_b_begin_a_reentry_never_rewinds_the_latest_current_pointer`: Handoffの literal Probe(A begin → B begin → A begin再入)をそのままRegression化——Aの再入Snapshotが元と同一Generation/Digestであること、再入前後を通じてCurrentが一貫してBのままであること、Aの遅延Evidence記録後もCurrent/Latest EvidenceがBへ誤混入しないことを確認する。(2) `test_129_distinct_requests_evict_the_oldest_and_keep_latest_pointer_on_the_newest`: 129個の真に異なる`request_id`をBeginし、Ledgerが`_MAX_TRACKED_TURNS=128`を超えないこと、最古Entry(`req-0`)がFIFOでEvictされること、Latest Current Pointerが最新の新規Request(`req-128`)を指し続けることを確認する。 |
| [test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py) | R5-WU-02 | 既存Fixture Golden Path Testへ、Handoffが列挙したHard Assertを全項目追加: `repair_outcome == "improved"`、`presentation_outcome == "repair_accepted"`、`candidate_withheld is True`、`repair_rejudge_provider == GEMMA_E2B_JUDGE`、`criteria_evaluated + criteria_unknown + criteria_not_applicable == 32`、`criteria_evaluated + criteria_unknown + criteria_not_applicable + criteria_deferred == 109`(`repair_accepted is True`/`repair_requested_by == "main_governance"`/`criteria_selected == 32`は既存Assertのまま維持)。加えて、初回Judge Dispatch(`SeleneSemanticEvaluator`によるBatch分割Call群、`:repair`/`:rejudge`いずれのSuffixでもない全Call)とRepair Rejudge(単一Call)がそれぞれ独立に`known_ids`と一致するだけでなく、両者が互いに完全一致すること(同一32 Criterion ID集合)を直接Cross-check する。 |
| [test_real_local_main_gemma_concurrent_dispatch_smoke.py](../../../../../tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py) | R5-WU-02/WU-03 | 実機Golden Path Test(`test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`)へ同一のHard Assertを追加(公開Resultのみ、Production SourceへTest専用Fieldは一切追加していない)。`criteria_evaluated`単体では32に届かない既知の未調査Anomaly(R4での`31`、今回の`30`)を追いかける代わりに、Count保存則(`evaluated+unknown+not_applicable==32`、`+deferred==109`)を新規Findingの判定基準として明示的に採用。Docstringへ、R5-WU-02/WU-03の実Trial結果(`criteria_evaluated=30 criteria_unknown=2` で保存則が厳密に成立、よってR5-WU-03の指示どおり正常挙動として記録)を追記。 |

## 4. Files Deliberately Not Changed

- Selene(`config/judge_templates/selene/*`、共有Decoder、Main-shared Prompt Builder): 一切触れていない。
- `_MAX_TRACKED_TURNS`/`_MAX_TRACKED_FREEZE_FAILURES`(128 Bound)とEviction時のHistory/Criterion-key同時Cleanup: 無変更で維持。
- `SemanticRuntimeCoordinator.begin()`の新規`request_id`初回Freeze経路(Generation採番、`freeze_semantic_turn()`呼び出し、Rotation Cursor更新、Eviction呼び出し): 無変更。
- `context_size=8192`、`max_criteria=32`、`LIVE_REPAIR_BUDGET`/`_REJUDGE_TOKENS_PER_CRITERION`: 無変更。
- Retry機構: 追加していない。
- Phase Index / Current Registry: 編集していない。
- 既存Handoff / Return / Review / History: 上書き・直編集していない。

## 5. Real Evidence

### 5.1 R5-WU-01(Fixture-only、実Model不使用)

新規2 Test、全Pass。Sabotage-regression実施(復元後再Diff一致を確認済み):

- `begin()`の既存Entry再Hit Branchへ`self._latest_request_id = request_id`/`self._turns.move_to_end(request_id)`を戻す(訂正前の挙動へ戻す)と、`test_a_begin_b_begin_a_reentry_never_rewinds_the_latest_current_pointer`が確実に失敗(`current_after_a_reentry.request_id`が`'req-b'`ではなく`'req-a'`になる——`AssertionError: assert 'req-a' == 'req-b'`)することを確認した。

### 5.2 R5-WU-02(Fixture-only + 実機1 Trial)

**Fixture**: 新規Hard Assert全項目、既存Assertとあわせて全Pass。Sabotage-regression実施(復元後再Diff一致を確認済み): `_semantic_criterion_counts()`内の`deferred=deferred + snapshot.deferred_criteria_count`から`+ snapshot.deferred_criteria_count`を削除する(Rotation-deferredの77件を計上しない訂正前相当のBug)と、新規のCount保存則Assert(`...+ criteria_deferred == 109`)が確実に失敗(`assert (((32 + 0) + 0) + 0) == 109`が成立せず`32 != 109`)することを確認した。

**実機(1 Trial、Handoffの上限どおり)**: `test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`実行。事前/事後Process残存チェック(`ps`/`lsof`)ともにClean。

実結果: `execution_state='completed' failure_reason=None criteria_selected=32 criteria_evaluated=30 criteria_deviated=10 criteria_unknown=2 criteria_not_applicable=0 criteria_deferred=77 repair_requested_by='main_governance' repair_outcome='improved' repair_accepted=True presentation_outcome='repair_accepted' candidate_withheld=True repair_rejudge_provider='judge.gemma-4-e2b-it-q4-0'`。

新規Hard Assert全項目(`repair_outcome`/`presentation_outcome`/`candidate_withheld`/`repair_rejudge_provider`/両Count保存則)が実機水準で成立することを確認した。Count保存則: `30 + 2 + 0 == 32`(成立)、`32 + 77 == 109`(成立)。

### 5.3 R5-WU-03(Claim訂正の確認)

`criteria_evaluated=30`(32ではない)は、Count保存則(`evaluated+unknown+not_applicable==32`)が厳密に成立している(不足分2件は`criteria_unknown`として正しく計上されている)ため、Handoffの指示どおり正常挙動として記録した——新規Findingとして停止する条件(保存則の不成立)には該当しない。本Return自身の`maximum_claim`も、Gemma一般のJSON Defect根絶という広いClaimではなく、「Compact Criterion Schemaを使う既知の32 CriterionのAll-Accept／Deviation／Production Golden Pathで、既知のMalformed再現経路が解消した」というHandoffのBounded Claimの範囲に限定して記述している。

## 6. Focused/Static Verification

- 全体非Model Suite: **2384 passed, 37 deselected**(R4収束Rework後の2382 passedから、新規Test純増2件)。
- Ruff(`.`全体): All checks passed。
- Canonical Mypy(`src tests`): **43 errors / 4 files**——Session通じて完全不変(本Roundの新規/変更Fileは0 error)。
- 実機Trial回数: R5-WU-02が1回(Handoffの上限どおり)。事前/事後のProcess残存チェック(`ps`/`lsof`)はClean。

## 7. Internal Review

### Review A: A→B→A再入 / FIFO Bound / Late Evidence / Latest Pointer

- [OK] A begin → B begin → A begin再入で、Aの再入Snapshotは元と同一Generation/Digestであり、Latest Current PointerはB開始後一貫してBのままである(再入によって一切巻き戻らない)ことを確認した(R5-WU-01、Sabotage-regression済み)。
- [OK] Aの遅延Evidence記録(再入後)は、Aの`evidence_for()`には正しく記録される一方、Bの`evidence_for()`/`current_snapshot()`/`latest_evidence()`には一切影響しないことを確認した(R4-WU-01のRequest-local Ledger契約と整合)。
- [OK] 129個の異なるRequestをBeginしても、LedgerはBound 128を超えず、最古Entry(`req-0`)がFIFOでEvictされ、Latest Current Pointerは最新の新規Request(`req-128`)を維持することを確認した。
- [OK] 既存のBound 128とEvidence/Criterion-key同時Evictionのロジック(`_evict_oldest_locked()`)は本Roundで一切変更していない。

### Review B: Repair Outcome / Presentation / 同一32 Criterion / Count保存則 / Persistence / Evidence

- [OK] Fixture Golden Path・実機Golden Path双方で、`repair_outcome=='improved'`、`presentation_outcome=='repair_accepted'`、`candidate_withheld is True`、`repair_rejudge_provider==GEMMA_E2B_JUDGE`を直接Hard Assertする形に強化した。
- [OK] Fixture側で、初回Judge Dispatch(全Batch)とRepair Rejudge(単一Call)が独立に既知の32 IDと一致するだけでなく、互いに完全一致することを直接Cross-checkする形に強化した。
- [OK] Count保存則(`evaluated+unknown+not_applicable==32`、`+deferred==109`)をFixture・実機の両方でHard Assertし、実機で成立(`30+2+0==32`、`32+77==109`)することを確認した——Sabotageで`deferred`計算からRotation-deferred分を欠落させると`+deferred==109`側が確実に失敗することも確認済み。
- [OK] `criteria_evaluated=30`(実機、32ではない)は、Count保存則が厳密に成立しているため正常挙動として記録し、新規Findingとして停止していない(R5-WU-03の指示どおり)。
- [OK] Persistence(同一Turn保存、`Tenon`が最終出力に含まれない)・Judge Evidence File(実`model_identity`/`evaluated_model_identity`/`repair_accepted`/Artifact Digest/`backend_key`)の既存Hard Assertは無変更で維持され、実機でも成立を確認した。

観点入れ替え後の再確認でも新規Findingなし。

## 8. Open Findings / True Stop

1. **`criteria_evaluated`単体の未調査Anomaly(R4での31、本Roundでの30)**: Count保存則(`evaluated+unknown+not_applicable==32`)が実機で厳密に成立していることを本Roundで確認した(R5-WU-03の指示どおり正常挙動として記録)。ただし`criteria_evaluated`が32に届かず一部が`unknown`側へ回る根本原因(Gemma自身の応答内容によるものか、Decode/Batch境界の挙動によるものか)自体は本RoundでもDepthは追っていない——Count保存則を満たす限り新規Findingではないが、原因自体は依然Open。
2. **R5-WU-02実機Golden Path Trialは1回のみ(Handoffの上限どおり)**: 再現性(同一条件での複数回一致)は未検証。
3. **R2-WU-05のGuardは本Roundで再確認していない**(Scope外、無変更)。

未達項目をScope外へ事後的に変更したものは無い。

## 9. Action Inventory

- R5-WU-01: 解決(resolved)——Latest Current Pointer再巻き戻り競合を除去。
- R5-WU-02: 解決(resolved)——Fixture/実機双方でGolden Path OracleへRepair/Presentation/同一32 Criterion/Count保存則のHard Assertを完備し、実機1 Trialで全項目成立を確認。
- R5-WU-03: 解決(resolved)——Claimを既知の32 Criterion/Compact Schema条件下のBounded Claimへ限定し、`criteria_evaluated=30`をCount保存則成立に基づき正常挙動として記録した。

## 10. Exact Next Action for Codex Controller

1. R5-WU-01(Latest Current Pointer再巻き戻り除去)の解決を受理するか判断する。
2. R5-WU-02の実機Golden Path Trial(1回、Hard Assert全項目成立)を受理するか、追加Trialを要求するか判断する。
3. R5-WU-03のBounded Claim訂正、および`criteria_evaluated`未調査Anomaly(Open Finding 1)を、追加調査の要求対象とするか、現状のまま受理するかを判断する。
4. Phase 9-1 Closureを主張するか、さらなるRoundを要求するかを判断する。
5. 本ReturnとRecoveryの内容を踏まえ、次のExact Handoffを発行する(必要な場合)。

新規PathのExact ReturnとRecoveryを提出し、Codex Controller Independent Review待ちで停止する。Phase Index／Current Registryは編集していない。既存Handoff／Return／Review／Historyの上書きは行っていない。
