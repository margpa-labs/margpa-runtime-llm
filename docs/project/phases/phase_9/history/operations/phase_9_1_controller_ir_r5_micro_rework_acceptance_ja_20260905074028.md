# Phase 9-1 — IR-R5 Micro Rework Controller受理

```yaml
document_id: phase_9_1_controller_ir_r5_micro_rework_acceptance_20260905074028
document_type: controller_independent_review_acceptance
document_state: accepted_incomplete
recorded_at: 2026-09-05 07:40:28 JST
language: ja
reviewer_role: codex_controller
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
phase_9_1_closure: false
real_model_action: none
source_test_mutation: none
git_mutation: none
append_only: true
```

対象：[IR-R5 Exact Return](../../handoffs/phase_9_claude_p9_1_controller_ir_r5_micro_rework_exact_return_ja_20260905073900.md)。比較基準は[IR-R4 Controller Review](phase_9_1_controller_ir_r4_return_review_and_final_micro_rework_ja_20260905071833.md)。

## 1. 判定

**IR-R5-01／02をACCEPTする。今回対象の追加Reworkは不要。Phase 9-1全体は未完了のまま。**

- Plannerは、Counter失敗、Token／Context不足、Worker Registry shutdown拒否を別のOutcomeとして保持し、呼出し元で`repair_rejudge_counter_failed`、`repair_rejudge_budget_insufficient`、`repair_rejudge_worker_registry_unavailable`へ写像する。Deadline／Cancelの先行判定も維持されている。
- Judge起点Gemma Repair Testは、Deviation成立後に`repair_outcome=improved`、`repair_accepted=true`、`presentation_outcome=repair_accepted`、非空で元回答と異なる提示内容をHard Assertする。safe fallbackではPASSしない。
- Main Governance起点Testは、実態に合わせて永続保存ではなく改善回答の採用を表す名称へ訂正され、Fixtureによる通常Turn保存Testとの二層Evidenceも明示された。

## 2. Controller確認

- Unit／非実機対象：**45 passed／5 deselected（0.80s）**。
- 対象4 File Ruff：PASS。
- Sourceと既存Testから、Counter例外とRegistry shutdown拒否のTyped分類、およびRejudge Call 0を確認。
- Claude報告のBackend Full **2317 passed／29 deselected**、Mypy **43 errors／4 files**（既存Baseline）、Oracle強化後の実機Gemma **1 passed**を保持する。Controllerは実モデルを再実行していない。

Controllerによる実Model、Network、Browser、User永続データ、Git、Source／Test変更は0。本受理文書とPhase Index追記のみ。

## 3. 継続する未完了事項

1. 通常32 Criterion Rejudgeは、暫定見積りだけでも`32×75=2400`となり、Repair Candidateを含む現行総Token予算2000へ入らない。予算方針のUser判断が必要。
2. Gemmaは1 Criterionの実機Golden Pathが成立。通常32件およびUser Mac実画面は未確認。
3. Seleneは未解決のまま延期候補。Gemmaの実画面成立後にCurrent Registryへ反映する。
4. Gemma不正JSONの確定的根本原因、既存Mypy 43件、Frontend未再検証は従来どおり残す。

JSON限定リトライは別予約のまま実装しない。次は予算方針を確定し、その結果を反映してからUser Mac Manualへ進む。Phase Closure／Phase 9-2へは進まない。
