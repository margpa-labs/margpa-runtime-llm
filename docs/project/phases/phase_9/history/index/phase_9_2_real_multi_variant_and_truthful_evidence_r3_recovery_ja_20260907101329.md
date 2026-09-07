# Phase 9-2 Real Multi-Variant / Truthful Evidence R3 Recovery

```yaml
document_id: phase_9_2_real_multi_variant_and_truthful_evidence_r3_recovery_20260907101329
document_state: partial_recovery
language: ja
created_at: 2026-09-07T10:13:29+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller R2 Return Independent Review
（`phase_9_2_controller_r2_return_independent_review_and_r3_rework_
decision_ja_20260907090620.md`、判定`CHANGES_REQUIRED`）を受け、同時に
発行されたR3 Exact Handoff
（`phase_9_controller_phase_9_2_real_multi_variant_and_truthful_evidence_
r3_exact_handoff_ja_20260907090620.md`）のR3-WU-01〜05を依存順に実施
した。IR-P9-2-R2-01〜07の7件のConfirmed Findingのうち6件（01/03/04/
05/06/07）をFixture/Integration段階でHard Assert付きで解消し、残る1件
（02、実Model GateがTop-level経路でない）はTop-level経路自体の実装・
Fake検証までは完了させたが、実Model 3 Scenario実行はMemory Pressure
実測（System-wide Free約5.5%、Swap使用量約71%）によるResource Gateで
今Round見送った。Exact Returnを新規Fileとして提出、Codex Controller
Independent Review待ち。

## 2. What Changed

- **Multi-Variant Production実行（R3-WU-01、IR-P9-2-R2-01 CRITICAL修正）**:
  Plan作成時のDesired Configuration計算を`overlay_variant_onto_snapshot()`
  でVariantごとに独立実行するよう変更（従来はLive Snapshotを1回だけ読み
  全Variantへ同一Digestを複製していた）。Run開始時のCall-0 GateをPlan
  全体Digest一致比較から、そのVariant自身が宣言するSlotのみを見る
  `find_mismatched_slots()`単独へ変更。各Runは自分の開始時点でLive
  Snapshotを新規取得し、それをそのRun自身のFrozen Configとして全内容
  保存する（Digestだけでなく）。同一Plan内でMain-onlyとJudge/Repair-
  ENFORCEを異なるLive設定下で順次実行し比較できることを新規Integration
  Testで実証。
- **Configuration Lease（R3-WU-01、IR-P9-2-R2-05 MAJOR修正）**:
  `ExperimentConfigurationLease`新設。実Actor呼出し中のみAcquire/Release
  される軽量Mutex。`web/app.py`の既存Middlewareへ、Judge/Repair/
  Recording Mode変更、Runtime Model Context/Tokens/Switch、Provider
  Selection、Guard/Main Governance Mode変更（Configuration Apply CAS
  経由）を対象とした409 Rejectを追加。いずれのControllerの契約も変更
  していない。
- **execution_mode Freeze（R3-WU-01、IR-P9-2-R2-07 MAJOR修正）**:
  `ExperimentPlan.execution_mode`を新設しPlan Digestへ組込み。
  `StartRunRequest`から`execution_mode` Fieldを削除、Run開始時は常に
  Plan自身の値を参照する。Frontendの実行Mode選択もPlan作成前のFormへ
  移動。
- **Tri-state Evidence（R3-WU-02、IR-P9-2-R2-04 MAJOR修正）**:
  `ActorInvocationRecord.called`を`bool | None`化（Mutation/Evidence/
  Authorityも連動する三状態Validatorを追加）。Guard相関不能、5つの
  未観測Component、main_called曖昧Error Code分岐を全て`None`
  （genuinely unknown）へ変更。Metricの`call_count`をConfirmed-True
  のみの下限値とし、`unknown_component_count`を新設して分離。
- **Queue Cancel/Deadline Call 0（R3-WU-03、IR-P9-2-R2-06 MAJOR修正）**:
  `ExperimentRunWorker._task()`が実行開始の瞬間にRunの現在状態をFresh
  再読し、既にTerminalなら`invoke()`を一切呼ばず短絡。Cancel/Deadline
  時に`Future.cancel()`もBest-effort追加。
- **UI Truthfulness（R3-WU-05）**: 「Frozen Config」Labelを「宣言
  Component」へ改名し、Desired Config Digest（Plan時点）とFrozen
  Config Digest（Run時点実測）を別Label・別列で表示。Comparison Table
  へExecution Mode列とFrozen Config Digest列を追加。Tri-state
  `called`の表示Bug（`null`を`"false"`と誤表示）を修正。
- **Top-level実Model Gate（R3-WU-04）**: 未実施（Resource Gate）。
  Fixture/Integration段階の前提は成立、実装方針はException Return
  第15節に記載。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_20260907101329.md`（本Roundの正本Return）
- 本File（Recovery Index）

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_20260907101329.md](../../handoffs/phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_20260907101329.md)

Maximum Claim: `P9_2_R3_PARTIAL_READY_FOR_USER_REAL_GATE`

## 5. Verification Summary

- Focused Unit（`tests/unit/experiment/` + `tests/unit/bootstrap/test_experiment_production_turn_adapter.py`）: 全Pass。
- Integration（`tests/integration/web/test_experiment_routes.py`）: 18件、全Pass（新規2件含む）。
- Queue Cancel/Deadline（`tests/unit/experiment/test_run_worker.py`）: 12件、全Pass（新規4件含む）。
- Backend Non-model Full Suite: `2629 passed, 40 deselected`（82.42秒）。R2時点`2627 passed, 40 deselected`から純増2件、Deselect数不変。
- Ruff（Whole Repo）: `All checks passed!`。
- Canonical Mypy（Whole Repo、`pyproject.toml`既定設定）: `43 errors/4 files`（既存Baseline完全一致）。
- Frontend: `npm test`（34 files/331 tests全Pass）、`tsc --noEmit`/`eslint .`/`npm run build`いずれも成功。
- Sabotage-regression 3件（Multi-Variant同一Digest化、Unknown→False、Queue Terminal Check除去）全て検出力確認・Byte-identical復元確認済み。
- 実Model Gate: **今Round0回実行**（Memory Pressure Resource Gate、Exact Return第9節）。

## 6. Open Items at This Point

- Top-level実Model Gate（R3-WU-04）が最大の未解決点。設計・Top-level
  経路自体の実装はFake Adapterで完了・検証済み。実Model 3 Scenario
  実行はResource Gate（Memory Pressure）で見送り。実装方針はException
  Return第15節に具体的に記載（`build_phase1_web_runtime()`を
  Monkeypatchせず利用する既存前例あり）。
- Definition Set/RAG/Presentation 3 Component SlotはLive Controllerが
  Codebaseに存在せず、R2から引き続き対象外。
- Guard Evidence相関は`unavailable_correlation`（`called=None`へ格上げ
  済みだが、真の相関機構自体は依然として存在しない）。
- main_called曖昧Error Code問題は`None`へ格上げ済み、Phase 9-1側での
  Code一意化改修は引き続きOpen（Phase 9-1 Scopeのため今Round対象外）。
- Guard Variantを含む3-way Multi-Variant Hard AssertはFixture/
  Integration段階でも今Round未実施（2 Variantでの実証に留めた）。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3
着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では
行わない。次の指示を待つ。
