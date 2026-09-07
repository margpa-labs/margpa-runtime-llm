# Phase 9-1 Package 2 残Open Findingの処遇決定と、再開前提条件

```yaml
document_id: phase_9_1_package_2_open_finding_disposition_and_resume_precondition_20260902182320
document_type: user_decision_and_resume_gate
language: ja
recorded_at: 2026-09-02 18:23:20 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
decision_author: user
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 1. 位置づけ

本Docは、[Package 2 Exact Return](../../handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_ja_20260902160000.md)で正直に引き継いだOpen Finding OF-P2-001〜004のうち、001〜003の処遇についてUserが下した決定と、その着手前にClaudeが満たすべき前提条件を記録する。あわせて、直前に発生した[Failure記録](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_authority_boundary_violation_and_origin_misattribution_ja_20260902182320.md)（未承認実行、検証不能な前提での正当化）を踏まえ、本Docの決定に基づく再開は、**本Doc自体がUserの明示的な実行許可を兼ねるものではない**——実際の作業再開には、本Docを踏まえた上で、Userからの改めての明示指示が必要である。

## 2. Open Finding別の処遇

```text
OF-P2-003（Main＋Selene同時Load時のMain破壊防止）: 実施する。
  Codex Handoff（Package 2 Exact Handoff §4 P2-WU-03）に元々明記済みの
  要求であり、Claude自身の裁量で追加・削除できる項目ではない。

OF-P2-001（Semantic 109のTurn間Rotation）: 実施する（当然の扱い）。
  同じくCodex Handoff（Package 2 Exact Handoff §4 P2-WU-06、
  「Batching、Token Accounting、Deferred ReasonおよびFinal Aggregationを
  正直に設計する」）に元々明記済みの要求であり、「新規機能・権限外」として
  Claudeが対象外にしたのは誤りだった。

OF-P2-002（Gemma 4 E2Bの構造化出力／JSON配列閉じ括弧欠落の弱点）: 保留。
  User自身が実画面でGemmaを実際に触ってみて、あまりにも使い物にならない
  水準であれば、その時点で改めて対応方針を検討する。現時点でClaude側から
  Decoder設計変更等を先行して行わない。
```

## 3. 再開前提条件（Exact Next Route）

上記OF-P2-003・OF-P2-001への着手を再開する前に、Claudeは次を完了させる。

1. 本Project内でCodexが作成した、現行Phase 9-1に関連するHandoff群を、要約や記憶に頼らず**もう一度実際に読み直す**。対象は少なくとも次を含む。

```text
docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_continuation_exact_handoff_ja_20260831234357.md
docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_exact_return_handoff_ja_20260831234930.md
docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_maximum_claim_micro_rework_exact_handoff_ja_20260901000347.md
docs/project/phases/phase_9/handoffs/phase_9_codex_designer_implementer_p9_1_maximum_claim_corrected_exact_return_handoff_ja_20260901000630.md
docs/project/phases/phase_9/handoffs/phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_ja_20260902121740.md
docs/project/phases/phase_9/handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md
  （§9 User Scope Correctionを含め、全文を再読すること — 見落としの
  実例が既に本Package内で発生している）
docs/project/phases/phase_9/handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_handoff_ja_20260902150815.md
  （Package 3自体はまだ着手しないが、Package 2との境界を正確に理解する
  ために読む）
```

2. 再読の結果、本Docの§2記載内容（処遇決定）と矛盾する記述がHandoff内に見つかった場合は、実装を再開する前に、その矛盾をUserへ明示的に提起する。**自己判断で解釈を埋めない**（[直前のFailure記録](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_authority_boundary_violation_and_origin_misattribution_ja_20260902182320.md)第4節の恒久Rule）。
3. 上記1・2が完了し、かつUserから改めて明示的な実行指示があった時点で、OF-P2-003・OF-P2-001の実装に着手する。

## 4. Status

```text
Current Point            : OF-P2-001／003は実施、OF-P2-002は保留（User実機
                            確認待ち）と決定。再開前提としてCodex Handoff
                            群の再読を必須化した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（決定記録）
Open Current Blocker      : Userからの明示的な作業再開指示待ち。
Controller-owned Next Work: なし。
Exact Next Route          : 本Doc§3の前提条件を満たした後、Userの明示指示
                            を受けてOF-P2-003→OF-P2-001の順で再開する。
```
