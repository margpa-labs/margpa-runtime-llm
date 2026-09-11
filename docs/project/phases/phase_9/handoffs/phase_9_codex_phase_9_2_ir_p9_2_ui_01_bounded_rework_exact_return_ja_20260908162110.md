---
document_type: exact_return_handoff
language: ja
title: Phase 9-2 IR-P9-2-UI-01 Bounded Rework Exact Return
created_at: 2026-09-08T16:21:10+09:00
author_role: 設計者兼実装者役
from_role: 設計者兼実装者役
to_role: プロジェクト責任者兼設計統括者役
target_thread_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
recording_policy: append_only
status: awaiting_controller_independent_re_review
maximum_claim: P9_2_USER_MANUAL_CANDIDATE
supersedes_for_rework_result: phase_9_codex_phase_9_2_pre_user_manual_ui_blocker_major_rework_exact_return_ja_20260908155658.md
---

# Phase 9-2 IR-P9-2-UI-01 Bounded Rework Exact Return

## 0. Maximum Claim

`P9_2_USER_MANUAL_CANDIDATE`

User Mac実画面PASS、Phase 9-2 Complete、Phase 9-3開始、ClosureはClaimしない。

## 1. Finding Disposition

`IR-P9-2-UI-01`（MAJOR）をFrontend限定で修正した。

Findingの根因は、自動Pollingの上限が120秒である一方、成立済みReal Production Evidenceには155〜160秒級の正常Runがあるのに、上限後の同一Run回収経路がなかったことである。先行Reworkは「timeoutはRun Failureではない」と表示を改善したが、Userが同じRunを再取得してTerminalへ収束させる操作を提供していなかった。

## 2. Corrected Lifecycle

```text
POST Run（1回のみ）
  → bounded auto tracking
  → Terminalなら通常収束
  → 120秒境界
      → GET-only final refresh
      → TerminalならErrorなしで収束
      → 非Terminal／取得不能ならsame run_idを保持してRecheck表示
          → GET same run
          → TerminalならError／Recheckを消して収束
          → 非Terminalならsame run_idを保持して再確認可能
```

Recheckは新しいRunを作らない。呼ぶMutation APIは0件である。

## 3. Implementation Delta

### Same-run explicit recovery

- timeoutした `run_id` を `recheckRunId` に保持する。
- 「同じRunの状態を再確認」Buttonを表示する。
- `fetchExperimentRun(recheckRunId)` のGETだけで状態を再取得する。
- Terminal時に `runError`／`recheckRunId` をclearする。
- 非Terminal時は「同じRunはまだ実行中」と表示し、同じRecheckを維持する。

### Timeout-boundary final reconciliation

- timeout直後に既存のRun list／Comparison GET refreshを1回実施する。
- そのrefreshでTerminalが既に成立していれば、timeout Error／Recheckを表示しない。

### Monotonic state merge

- `upsertRun()` はより古いGenerationを拒否する。
- 同GenerationでTerminalを観測済みなら、後着した `planned`／`running` responseを拒否する。
- Run list refreshは配列全置換ではなくmonotonic mergeを使う。

これにより、direct Run GETが `completed` を返した後、先に発行されていたlist GETの `running` responseが後着しても、画面は `running` へ戻らない。

## 4. Exact API Accounting

| Event | API | Method | Count constraint |
|---|---|---|---|
| Initial Run | `/api/v7/experiment/runs` | POST | 1 |
| Auto tracking | `/api/v7/experiment/runs/{run_id}` | GET | bounded |
| Timeout final refresh | Run list／Comparison | GET | 1 set |
| Explicit Recheck | `/api/v7/experiment/runs/{same_run_id}` | GET | 1 per click |
| Recheck terminal refresh | Run list／Comparison | GET | 1 set |
| Recheckによる新規Run | `/api/v7/experiment/runs` | POST | 0 |

## 5. Changed Delta Paths

- `frontend/src/components/ExperimentPanel.tsx`
- `frontend/src/components/ExperimentPanel.test.tsx`
- `frontend/src/i18n/translations.ts`
- `src/margpa_runtime_llm/web/static/app.js`

先行Reworkから保持したPath:

- `frontend/src/components/TopBar.tsx`
- `frontend/src/App.test.tsx`

Backend Python Source、Data Controls、Phase 9-1 Main／Judge／Guard／Repair、Provider Identity、Call 0、Recordingには変更がない。

## 6. Validation

### Focused

- `ExperimentPanel.test.tsx`＋`App.test.tsx`: 2 files／47 tests PASS

### Canonical Frontend

- Full: 34 files／337 tests PASS
- Typecheck: PASS
- Lint: PASS
- Build: PASS（60 modules transformed）
- Built static asset route: 1 test PASS
- `git diff --check`: PASS

### New Acceptance Assertions

1. auto tracking timeout後にsame-run Recheckが表示される。
2. Recheck前後のRun POST回数は1のまま。
3. Recheck GETがTerminalを返すとtracking Errorが消える。
4. Recheck Buttonが消え、Terminal rowが残る。
5. Recheck後のstale `running` list responseはTerminalを巻き戻さない。
6. timeout境界のfinal list refreshがTerminalを返せば、ErrorもRecheckも表示しない。

Backend Source変更がないため、先行Reworkで成立済みの53 focused／242 expandedは反復していない。

## 7. Self Review

### API safety view

- `handleRecheck()` から `startExperimentRun()` は到達不能。
- Recheck pathはGET wrappersだけを呼ぶ。
- Run IDを再生成しない。

### Race／truthfulness view

- Terminalは同Generationのnon-terminal responseで巻き戻らない。
- timeoutはRun Failureと表示しない。
- final refreshでTerminalが確認できた場合、古いtracking Errorを残さない。
- 非TerminalをTerminalへ捏造しない。

### Scope／regression view

- Finding以外のBackend、Model、Provider、Data Controlsへ拡張していない。
- Real Model／Browser／Network／User `runtime_data`へ接触していない。
- User ManualをTestで代替していない。
- Git writeを行っていない。

これは同一Task内自己Reviewであり、Controller Independent Re-reviewではない。

## 8. Open Boundary

- 155〜160秒級の実RunでのButton出現とTerminal収束はUser Mac Manual Gateに残る。
- Browser console／実HTTP timingは本Reworkでは未取得。
- R5既知のnon-blocking Evidence制約は変更しない。

## 9. Exact Next Action

1. Controllerが本4-Path deltaと2つの新規回帰TestをIndependent Re-reviewする。
2. 受理後、User MacでProduction Runを実施する。
3. 120秒を超えた場合、「同じRunの状態を再確認」を使ってsame runがTerminalへ収束することを確認する。
4. User Manual PASS／Phase 9-2 Closure判断はController／Userだけが行う。

ここで停止し、Controller Independent Re-reviewを待つ。
