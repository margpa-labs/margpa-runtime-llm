# Phase 9-1 IR-R3-02 — Rejudge Token実測校正と32件Criterion未成立の定量化 未解決Snapshot

```yaml
document_id: phase_9_1_rejudge_token_calibration_and_32_criterion_infeasibility_snapshot_20260905000817
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-05 00:08:17 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Codex Controller独立Review(`../../../phases/phase_9/history/operations/phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md`)IR-R3-02の指摘: `_REJUDGE_TOKENS_PER_CRITERION=150`は「実測校正済み」というEvidenceがなく、Runtimeの既定選択上限(`bootstrap/runtime_governance.py`の`SemanticRuntimeBindingContext.max_criteria`既定値32)に対し`150×32=4800`は総予算2000 Tokenを常に超過するため、通常選択集合でのRepair成立を証明したことにはならない、という指摘への対応。

## 2. 実測(Task所有隔離Process、実生成なし、実Tokenizerのみ)

対象Script: `p1_rejudge_token_calibration/measure_realistic_32_criteria_rejudge_tokens.py`(Scratchpad)。実ARGD/DAGD Compiled Corpusから実Criterion ID 32件を抽出し、このTaskの実Gemma出力Sample(`wu03_gemma_repro/run_diagnostic.log`、`run_accept_case.log`)を直接参考にした現実的な`criterion_results`Entry(各Criterionへ`reason_code`と実長の`evidence_refs`引用を含む、最小限ではない形)で全32件のRejudge応答を構成し、実Qwen Tokenizer(`InferenceService.count_chat_prompt_tokens()`、実Generateは呼んでいない)で測定した。

```text
[FACT] all-pass(最良Case): 応答7898文字、1771 Token、55.3 Token/Criterion
[FACT] all-deviation(最悪Case): 応答8320文字、1901 Token、59.4 Token/Criterion
```

従来の150 Token/Criterionという見積りは、SeleneのBatched Judge Dispatch(別のPrompt形状、`max_new_tokens=1000`/`max_criteria_per_call=8`≈125 Token/Criterion)からの「大まかな」流用であり、Repair自身のRejudge応答形状に対する実測ではなかった(Controllerの指摘どおり)。今回の実測により、実際の必要量は55〜60 Token/Criterion程度であることが判明した。

## 3. 対応(実装済み)

`src/margpa_runtime_llm/bootstrap/repair_live_integration.py`の`_REJUDGE_TOKENS_PER_CRITERION`を`150`から`75`(実測最悪値59.4 Tokenへ約25%の安全余裕を加えた値)へ再校正した。Budget上限(`LIVE_REPAIR_BUDGET.max_additional_tokens=2000`)、Call上限(`max_total_model_calls`)、Decoderの厳密性はいずれも変更していない——Criterion 1件あたりの出力見積り(上限として`generate()`へ渡す`max_new_tokens`の計算根拠)のみを、実測Evidenceに基づき訂正した。

## 4. 結果(定量化、32件は今回も未成立)

再校正後も、実際のRuntime既定選択上限(32件)はEXISTING Budget内では成立しない:

```text
[FACT] 26 Criteria: 75×26=1950 <= 2000-5=1995 (候補Call消費5 Token時) — 成立
[FACT] 27 Criteria: 75×27=2025 > 1995 — 不成立(境界)
[FACT] 32 Criteria(Runtime既定選択上限): 75×32=2400 > 2000(候補Call消費ゼロでも超過) — 不成立
```

すなわち、実測に基づく再校正によって、EXISTING制約内で成立する選択規模は「5件」から「26件」へ大幅に拡大した(Fixtureの縮小やCriterion脱落ではなく、実測Evidenceに基づく訂正)。ただし、Runtimeの真の既定選択上限である32件は、再校正後もなお成立しない——これは今回の再校正で解消できない、genuine な既存制約である。

## 5. 制約の性質と最小変更案(未実装、提示のみ)

32件が成立しない根本原因は2点の組合せである:

1. `LIVE_REPAIR_BUDGET.max_additional_tokens=2000`という既存の総Token上限自体が、Frozen Criterion引継ぎ(IR-02修正)以前の「非構造化・単一判定」Shape(200 Token固定)を前提に設定されたものであり、多数Criterionを伴うRejudgeを十分に想定していない。
2. RepairのRejudgeには、Judgeの初回Dispatch(`SeleneSemanticEvaluator._plan_batches()`)のような自前のBatching機構がなく、常に単一の非分割Callである。

最小変更案(いずれも未実装、User／Codex判断待ち):

- (a) `LIVE_REPAIR_BUDGET.max_additional_tokens`を、Frozen Criterion Rejudgeの実態に合わせて引き上げる(例: 候補400+Rejudge 2400+余裕分 ≈ 3000)。実質的なBudget Policy変更であり、明示的な承認が必要。
- (b) Rejudgeに`SeleneSemanticEvaluator._plan_batches()`と同様の複数Call分割機構を持たせる。Architectural変更であり「最小」ではない。

いずれも今回実装していない。「予算の無断拡大、Criterion脱落、Decoderの厳密性緩和...禁止」という指示に従い、32件の成立は未成立のまま維持する。

## 6. Registry反映(提案、正本編集はしない)

- 既存UF-P9-003または新規Findingへ、「Rejudge Token見積りは実測校正済み(75 Token/Criterion、2026-09-05)。EXISTING Budget内で26件まで成立確認、Runtime既定の32件は依然未成立(Budget拡大またはBatching機構追加が必要、いずれも未実装)」を追記候補とする。
- Registry本体は直接編集しない。

## 7. Status

```text
Current Point            : Rejudge Token見積りを実測(Task所有隔離Process、
                            実Tokenizerのみ、実生成なし)に基づき150→75へ
                            再校正。EXISTING Budget内で26件Criterionまで
                            成立を実証(5件から大幅拡大)。Runtime既定の
                            32件は再校正後もなお不成立、定量的に確認済み。
Files Created／Modified   : 本File(新規作成)、
                            src/margpa_runtime_llm/bootstrap/repair_live_integration.py
                            (`_REJUDGE_TOKENS_PER_CRITERION`再校正)、
                            tests/unit/bootstrap/test_repair_live_integration.py
                            (新規Test4件、既存Test1件のHardcode値修正)。
                            Scratchpad実測Script・Log 1組。
Validation                : 実Tokenizer測定1回(32件×2 Case)、Unit Test
                            全35件PASS、Mypy新規Error0件(既存43件Baseline
                            維持)。
Open Current Blocker      : 32件Criterion未成立(Budget拡大またはBatching
                            機構追加のいずれかが必要、未実装・未承認)。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
```
