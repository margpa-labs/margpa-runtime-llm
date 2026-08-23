# Phase 6 Third Rework — Acceptance再判定 追補（Append-only）

```yaml
document_id: phase_6_third_rework_acceptance_rederivation_addendum
status: append_only_evidence
phase: phase_6
work_unit: required_rework_sequence_step_8_addendum
role: Claude側設計統括者役
created_at: 2026-08-23 18:45:00 JST
corrects_by_reference:
  - phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md
```

先行文書（`phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md`）
提出後、P6-ACC-056とP6-ACC-038の2件についてさらに作業・検討を行ったため、
本追補で更新する（先行文書は書き換えず、本文書で判定を差し替える）。

## P6-ACC-056（None／Unavailable／Invalid／Loading／Degraded／Active区別）

```text
判定: [C] STILL_OPEN → [A] CLOSED（新規）

実施内容:
  4 Identity（Main／Guard／Governance Layer／Judge）それぞれについて、
  project_*_identity()のSource実装を直接Traceし、各Identityが実際に
  到達可能なComponentIdentityStateを特定した。

  発見（Third Reviewの「4×6=24組み合わせ」という前提を訂正する）:
    Main Model      : NONE／LOADING／ACTIVE／DEGRADED／UNAVAILABLE（5）
                      ——INVALIDはMain Modelには存在しない概念。
    Guard Model     : NONE／INVALID／ACTIVE（3）
                      ——LOADING／DEGRADED／UNAVAILABLEは、Optional[str]
                      3値だけを引数に取る現行関数Signatureでは構造的に
                      到達不能。
    Governance Layer: NONE／INVALID／ACTIVE（3）——Guard Modelと同じ理由。
    Judge Model     : NONE／ACTIVE（2）
                      ——`project_judge_model_identity()`内の
                      `binding_state is not BOUND`分岐は、実際には
                      到達不能なDead Codeであることを特定した
                      （`resolve_judge_independence()`が同一条件で
                      一行前に既にUNAVAILABLE［→ComponentIdentityState.
                      NONE］へ短絡するため）。

  実到達可能な組み合わせは4 Identity合計13通り（24通りではない）。
  Third Reviewが前提とした「6状態×4 Identity」という一様な枠組み自体が、
  現行Architectureの実際のCode Pathと一致しないことを、推測ではなく
  Source Trace結果として提示する。

  この13通りすべてを網羅するTestを新規追加した:
  tests/unit/runtime_observability/test_component_identity_projection.py
  （5件新規: Main Model NONE／LOADING［3 RuntimeState variant一括］／
  DEGRADED、およびJudge ModelのDead Code到達不能性を直接証明するTest）。
  既存10件と合わせ、計15件で13通りの実到達可能な組み合わせ全てを
  Covering済み（一部組み合わせは複数Testで重複確認）。

Evidence: tests/unit/runtime_observability/
  test_component_identity_projection.py（15件、全PASS）。
```

## P6-ACC-038（State遷移とTerminal一意）

```text
判定: [A] PARTIAL → [A] CLOSED（訂正）

再検討理由: 先行文書はP6-ACC-038を、Third Review本文が挙げた実装例
（Chat Bubble自体でのjudging/repairing/rejudishingの個別粒度可視化）
と混同してPARTIALとしていた。しかしAcceptance Matrix
（phase_6_acceptance_matrix_ja.md）が定義する本来のContractは
「State遷移とTerminal一意」であり、Chat Bubble上の視覚粒度は含まない。

本来のContract（Terminal Stateの一意性、Stale Runningを残さないこと）は、
P6-CODEX-020対応（judge_live_integration.pyの全体Try/Except化、
JudgeRunState拡張、mark_skipped()のRequest Identity相関化）により
達成済みであり、対応するTest
（test_unhandled_exception_anywhere_in_the_run_still_reaches_a_terminal_state
等）で確認済みである。

Chat Bubble上の細分State可視化（judging/repairing/rejudishing個別表示）
は、Third Reviewが例示した実装Ideaであって、Acceptance Matrix上の
独立した必須ID化はされていない。本Third Reworkでは、running／
improved／degradedの3状態をChat Surfaceへ表示し、Feature Modes Panelで
全State（idle/queued_or_skipped/running/completed/failed/cancelled/
degraded）を表示する、という意図的なScope分割を採用した
（MessageBubble.tsxのCommentで明示済み）。これはP6-ACC-038という
既存Acceptance IDのCLOSURE要件ではなく、UI設計上の裁量判断として
記録する。
```

## 更新後の総括

```text
[C] STILL_OPEN（本追補後）: P6-ACC-022の一部（独立Judge Model・第三者
  Corpus依存部分）のみ。これはThird Review Return Contract §7が
  明示的に許容する「外部Modelを必要とする将来Calibration Variant」の
  Deferred扱いに正確に合致する（Owner／Target Phase／Re-entry Trigger
  はphase_6_calibration_harness_results_ja_20260823180000.md §7に
  記載済み）。

  それ以外の必須Acceptance（P6-ACC-022の基本部分、038、056含む）に
  PARTIAL／NOT_EXECUTED／UNVERIFIEDは残っていない。
```
