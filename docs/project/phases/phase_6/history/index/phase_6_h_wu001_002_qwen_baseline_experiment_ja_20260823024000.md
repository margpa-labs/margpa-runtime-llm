# Phase 6-H-WU-001／002 Qwen OFF-mode Baseline Experiment（実Hardware実測）

```yaml
document_id: phase_6_h_wu001_002_qwen_baseline_experiment
status: current_recovery_entry
phase: phase_6
subphase: phase_6_h
work_unit: p6_h_wu001_wu002_partial_qwen_off_baseline_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 02:40:00 JST
```

## Experiment Freeze（WU-001、最小限）

```text
Dataset   : qwen_known_failure_modes（tests/unit/evaluation/fixtures/、6 Case、
            SHA-512は本Dataset自体のLoad時Digest記録済み、Phase 6-C-WU-002参照）
Model     : main.qwen3-4b-q4-k-m（実Load、Context Size 4096、GPU全Layer Offload）
Mode      : Governance／Guardrail／Judge／Repair、全てOFF相当（本Session時点で
            これらが実Generation経路へ未配線のため、実質的にOFF Baseline）
Evaluator : Deterministic Registry（ExactReferenceMatch／ContradictionMarker／
            UnsupportedClaimCandidate／FormatCompliance）
```

## 実測結果（実Qwen3-4B、6 Case、実Generation×6）

| Case | Tags | Recommendation | Latency(ms) | Tokens |
|---|---|---|---|---|
| overconfidence_001 | overconfidence | **accept**（要検討、下記参照） | 2939 | 152 |
| definition_confusion_001 | definition_confusion | needs_repair | 12161 | 539 |
| insufficient_grounding_001 | insufficient_grounding | needs_repair | 11103 | 497 |
| contradiction_001 | contradiction | accept | 3851 | 195 |
| format_deviation_001 | format_deviation | accept | 156 | 32 |
| uncertainty_expression_001 | uncertainty_expression | unknown | 12178 | 539 |

## 発見事項（捏造せず正直に記録）

```text
overconfidence_001の実際のQwen回答は「2023年10月時点のParisの人口は
2,195,685人」という、質問の性質上そもそも不可能な精度・確度を伴う
架空の数値を提示した——これは正しくOverconfidence失敗として検出される
べき事例だったが、本SessionのUnsupportedClaimCandidateEvaluatorの
Marker Set（"always","definitely","exactly"）が実際の出力文言と
一致しなかったため、Falseに"accept"と判定された。

これはP6-ACC-072「False Positive／Negative不明値を0で捏造0」に対し、
本Result自体が示す実際のFalse Negative事例である。Marker-based
Deterministic Evaluatorの原理的限界（意味理解を伴わない）を実データで
実証した——Architecture 6.2が最初から想定していた「Deterministic単独では
意味的Failureを完全には捕捉できず、LLM-as-a-Judgeでの補完が必要」
という設計判断を裏付けるEvidenceである。
```

## Validation

```text
実Generation: 6回成功（Crash 0、Timeout 0）
実Evaluator適用: 6/6 Case、Model Call 0（Deterministic Evaluatorは全てModel非依存）
Total実行時間: 約42秒（6回のGeneration、Context 4096、GPU Offload全Layer）
```

## Scope外・未実施

```text
OBSERVE／ENFORCE Modeとの比較: 未実施。Governance／Guardrail／Judge／Repairの
  実Generation経路への配線が本Session時点で未完了のため、Mode間比較自体が
  成立しない。6-B-WU-006同様のProduction配線が先に必要。
DeepSeek比較: CURRENT_TOOLCHAIN_UNSUPPORTED継続、対象外。
LLM-as-a-Judgeとの併用比較: Phase 6-D-WU-005で個別に実証済み（本Experimentとは
  別Run）。両者を同一Runで統合した比較はWU-004として後続実施。
```

## Next Exact Route

Phase 6-I（Integrated Verification）へ進む準備として、Full Backend／Frontend
Regression、Static Check、既存Recovery Entry群の棚卸しを行う。
