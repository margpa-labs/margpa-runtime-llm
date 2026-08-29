# Phase 6 Current Claude Task — Package R15 Final Recovery（Request-ID Observability／Recording Correlation）

```yaml
document_id: phase_6_current_claude_task_r15_final_recovery_20260828231301
package: P6-RR-R15
status: PACKAGE_COMPLETE
created_at: 2026-08-28 23:13:01 JST
active_contract: phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_ja_20260828221510.md
predecessor: phase_6_current_claude_task_r14_final_recovery_ja_20260828225852.md
git_action: 0（本Package中の新規発生 0。累計はP6-RR-R-INC-001の1のまま）
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-077: Recording CorrelationがJudge依存で、Judge OFF時のTurn Recordingが
              Current TurnではなくHistorical／Unmatchedに誤分類される -> RESOLVED（本Package）
```

## 調査（実装前）

Current Source（本Claude Task内でR13〜R14として先行完了済み）を確認したところ、Backend側の
実装（`_recording_snapshot()`のCurrent-Turn Anchor変更、`JudgeCompletionContext.recording_mode`の
Frozen優先化）は既に前Turnで実装済みであることを確認した。一方、以下2点が未完了のまま残っていた。

1. 上記Backend実装を直接検証するTestが存在しなかった（既存Suiteが1697/1697 Passしていたのは
   「既存の何も壊していない」ことの証明であって、「新しい正しい挙動」自体を直接検証してはいない）。
2. Frontend（`FeatureModesPanel.tsx`）がBackend由来の`correlation`Fieldを実際に消費しているか、
   Judge OFF時にServer側`correlation`を正しく優先しているかが未検証だった。

Frontendを読んだ結果、Copilot（R9〜R12）が`status.recording.correlation`を優先的に読み、
`correlation`がNull（Unbound Runtimeのみ）の場合に限りClient側Heuristic（Judge発の
`current_request_id`から逆算する旧方式相当のFallback）へ落ちる実装を既に行っていたことを確認した。
つまりFrontend自体は本Findingを正しく解決できるよう既に配線されており、今回のBackend修正
（本Claude Task内で先行実装済み）が有効になるだけで正しく動作する状態だった。UI Summaryが要求する
Request ID／時刻／Frozen Modes／Configured・Active・Executed／Budget／Judge Outcome／
Final Disposition／Failureは`renderJudgeStatus()`に、Turn Recording／Judge Evidence Recordingは
`renderRecordingCorrelation()`に、既に個別Blockとして表示済みであることも確認し、Field欠落は
なかった（1つの統合Blockに再構成する追加要求はFinding本文・Handoff本文いずれにも根拠がないため
対象外とした）。

## 実装

### Changed Files

```text
[Test新規]
tests/unit/bootstrap/test_recording_live_integration.py（2 tests追加）
  - test_frozen_recording_mode_off_suppresses_write_despite_live_full
    Turn開始時Frozen=OFF、Hook実行時点でLive=FULLへ変化 -> 書き込まれないことを直接検証。
  - test_frozen_recording_mode_full_writes_despite_live_off
    Turn開始時Frozen=FULL、Hook実行時点でLive=OFFへ変化 -> 書き込まれることを直接検証。
    （両者でFrozen値がLive再読より優先されることをP6-CODEX-077の後半分について直接証明）

tests/integration/web/test_feature_modes_routes.py（1 test追加）
  - test_recording_correlation_anchors_on_its_own_turn_when_judge_never_ran
    Judge Compositionを一切設定せず（Judge未実行 = judge.current_request_idはNoneのまま）、
    Recording Compositionのみreq-99でrecord_ok -> correlation.current_turnがreq-99として
    正しく現在Turn扱いになり、historical_or_unmatchedへ落ちないことをHTTP Route経由で直接検証。
    （P6-CODEX-077の前半分＝Current-Turn AnchorのJudge非依存化を直接証明）

frontend/src/components/FeatureModesPanel.test.tsx（1 test追加）
  - "P6-CODEX-077: uses the server-computed correlation as the current Turn even when
    Judge never ran"
    judge.current_mode="off"／current_request_id=null、recording.correlationを
    Backend契約どおりのShapeで直接供給 -> Frontendがそれをそのまま採用し
    #feature-modes-recording-correlation-requestにreq-77を表示、
    #feature-modes-recording-unmatchedへ落とさないことを検証。
    （Frontendの既存Fallback Heuristicではなく、Server供給のcorrelationが優先される経路を直接証明）
```

Source側（`feature_modes_routes.py`／`conversation_generation.py`／`recording_live_integration.py`）に
本Packageでの追加変更なし（実装は本Claude Task内で先行完了済み、本Packageの担当はその検証Testの
補完とFrontend配線の確認のみ）。

## Focused／Full Evidence

```text
Command: ./.venv/bin/pytest tests/unit/bootstrap/test_recording_live_integration.py \
         tests/integration/web/test_feature_modes_routes.py -q
Result : 23 passed（新規3件を含む）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/ -q
Result : 1700 passed, 7 deselected（R14終了時1697 + 新規3件 = 1700、Regression 0）

Command: ./.venv/bin/mypy tests/unit/bootstrap/test_recording_live_integration.py \
         tests/integration/web/test_feature_modes_routes.py
Result : Success: no issues found in 2 source files

Command: ./.venv/bin/ruff check <同上2 File>
Result : All checks passed!
Note   : ruff format --check は同2 File中、本Packageで触れていない既存行（Copilot由来の
         Pre-existing Format）でのみ差分を報告した（新規追加行は対象外）。当該行は本Packageの
         変更範囲外のため無変更のまま維持し、次回Full Formatting Passの対象として記録するに留める。

Command（Frontend）: npm test（= NODE_OPTIONS=--no-webstorage vitest run）
Result : Test Files 25 passed (25) / Tests 231 passed (231)（新規1件を含む、Regression 0）
Note   : 初回`npx vitest run`（Canonical Scriptの`NODE_OPTIONS=--no-webstorage`を付けない実行）
         では無関係な2 File・34 testsがlocalStorage Polyfill差で失敗したが、これは実行方法の誤り
         （Canonical Script不使用）によるものであり、Source起因のRegressionではないことを
         `npm test`再実行で確認した。

Command（Frontend）: npm run typecheck（tsc --noEmit）
Result : No errors

Command（Frontend）: npx eslint src/components/FeatureModesPanel.test.tsx
Result : No errors
```

## Scope Boundary（意図的に対象外とした部分、理由付き）

```text
Recording Correlation Blockを1つの統合UI Componentへ再構成すること: 対象外。Request ID／時刻／
  Frozen Modes／Configured・Active・Executed／Budget／Judge Outcome／Final Disposition／Failure
  はrenderJudgeStatus()に、Turn Recording／Judge Evidence RecordingはrenderRecordingCorrelation()
  に、既に別Blockとして表示済みでField欠落がないため、表示位置の再構成は本Findingの解決に
  必須ではないと判断した。

usePreference.test.tsxのlocalStorage関連Failure: 本Package変更（Recording Live Integration／
  Feature Modes Routes／FeatureModesPanel）のいずれとも無関係なFileであり（Git Status相当の
  変更・未追跡File一覧に含まれず）、Canonical Test Script（npm test）で再現しないことを確認済み。
  実行方法の誤りであり、本PackageのFindingとも新規Regressionとも判断せず、対象外とした。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-077はRESOLVED。078・079は引き続きOpen、R16で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま。本Package中の新規発生 0）
Git Mutation      : 0
Network Action     : 0
Provider Memory    : 0
User runtime_data  : 0
Root外Persistent Write: 0 known
```

## Task-owned Temporary／Active Process／Loaded Model

```text
Active Process : 0
Loaded Model   : 0（全てFixture／Fake Service、Frontend Testはmocked fetch）
```

## Exact Next Action

```text
next_exact_work_unit: P6-RR-R16-WU-001（Focused Backend/Frontend再実行、S1〜S17再構成、
                       Acceptance 66件個別再導出、Full-Path Changed File Inventory、
                       Internal Review Cycle 1〜2、Final Recovery + Exact Return Handoff、
                       Codex Independent Review待ちで停止）
```
