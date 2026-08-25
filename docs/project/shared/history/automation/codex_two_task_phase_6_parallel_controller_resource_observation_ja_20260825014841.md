# Codex Two-Task Phase 6 — Parallel Controller Resource Observation

```yaml
document_id: codex_two_task_phase_6_parallel_controller_resource_observation_20260825014841
status: recorded
classification: automation_operational_evidence
created_at: 2026-08-25 01:48:41 JST
scope: phase_6_rework_codex_two_task_operation
result: technically_effective_but_resource_inefficient
```

## 1. 対象

Phase 6後半Reworkで、別Codex Taskの設計者兼実装者役が実装／Test／Recoveryを担当し、プロジェクト責任者兼設計統括者役TaskがHandoff、途中Review、Independent Test、Finding、Resume AuthorityおよびRework Routingを担当した試行を記録する。

## 2. 成立したこと

- Task間の直接Handoff／報告は成立した。
- Executorによる実装とControllerによる独立Reviewの役割分離は成立した。
- Controllerは複数の重大Concurrency／Evidence Lifecycle Findingを検出した。
- Reworkを別Taskへ返し、再検証するLoopは成立した。
- Userによる手動Copy Relayを主要経路から除去できた。

技術面では、Codex 2タスクによるLong Run／Review／Rework運用が実行可能であることを確認した。

## 3. 問題

ControllerがExecutorの完了を待たず、途中Source確認、独立Test、先回りReviewおよび追加指示を並走した。この方式には次の問題があった。

1. User報告では、当該一連工程だけでCodex利用可能量が約70〜80%減少した。
2. ExecutorとController双方の消費が重なり、Userが残Resourceを予測しにくかった。
3. Controller Turnが長時間継続し、Userが別の確認や予約事項を差し込みにくかった。
4. Wall Time短縮と引き換えに、ControllerをPhase境界へ温存する本来目的を弱めた。

利用可能量の70〜80%はUserが製品表示から観測した概算であり、Controllerによる独立Telemetryではない。開始・終了のExact Token量、Task別内訳および課金換算は`UNVERIFIED`である。

## 4. 評価

```text
Technical Feasibility        : PASS
Direct Task Coordination     : PASS
Independent Review Utility   : PASS
Resource Efficiency          : FAIL / ADJUST
Resource Predictability      : FAIL / ADJUST
Controller User Availability : FAIL / ADJUST
Overall                      : CONTINUE WITH OPERATING MODEL CORRECTION
```

失敗原因は2タスク分離そのものではなく、Executor Running中にもControllerが常時並走したSchedulingである。

## 5. Corrective Decision

以後のDefaultを次へ変更する。

```text
Dispatch Executor
  -> Controller WAITING / UserへTurnを返す
  -> Executor Complete Candidate Return
  -> Controller集中Review
  -> Exact Rework Dispatch
  -> Controller WAITING
```

正本Correction：

`docs/project/shared/history/automation/codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md` §13

## 6. 次回Acceptance

- Executor Return前のController Polling／Source Review／Testは原則0。
- ControllerはExecutor稼働中もUserから別件を受けられる。
- ReviewはComplete Candidate単位へ集約する。
- True StopまたはUser割込みだけを例外とする。
- 利用可能量の開始／終了をUser観測値として記録する。

本書はProvider一般の恒久的特性ではなく、このPhase 6実測から得たScheduling Evidenceである。後続試行の結果により更新評価できる。
