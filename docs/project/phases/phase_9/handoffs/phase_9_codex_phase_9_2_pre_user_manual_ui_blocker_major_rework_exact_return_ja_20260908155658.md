---
document_type: exact_return_handoff
language: ja
title: Phase 9-2 User Manual前 UI Blocker／Major Rework Exact Return
created_at: 2026-09-08T15:56:58+09:00
author_role: 設計者兼実装者役
from_role: 設計者兼実装者役
to_role: プロジェクト責任者兼設計統括者役
target_thread_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
recording_policy: append_only
status: awaiting_controller_independent_review
maximum_claim: P9_2_USER_MANUAL_CANDIDATE
---

# Phase 9-2 User Manual前 UI Blocker／Major Rework Exact Return

## 0. Maximum Claim

`P9_2_USER_MANUAL_CANDIDATE`

これはFrozen Designが許す最大Claim以下である。次をClaimしない。

- User Mac実画面PASS
- Phase 9-2 Complete
- Phase 9-3開始
- Phase 9 Closure
- Real Browser／Real Modelの本Rework内再実施

## 1. Executive Return

昨日の実画面症状に直接関係する2件のFrontend Blocker／MajorをBounded修正した。

1. Experiment操作Buttonが無分類Buttonのままで、Global CSSの白系文字だけを受け、背景を明示しなかった。このためBrowser既定の灰色Button背景上で低Contrastになった。
2. Run開始後、最初のstatus GETが一度でも失敗するとPromise chainが即終了し、Backend Workerが継続していてもFrontendは最初の `running` 行とGeneric Errorのまま進展しなかった。

あわせて、Plan作成直後のComparison未取得状態を赤いFailureとして表示していた誤分類を除去した。

BackendのPlan／Frozen Config／Lease／Worker／Persistence／Comparison／Typed Reject経路は非モデルTestで成立しており、Backend Source変更は不要と判断した。実画面障害時の正確なHTTP Failureイベントは取得していないため、上記2はSourceと再現Testで確認した構造欠陥であり、昨日の実イベントの唯一原因とまではClaimしない。

## 2. Actual Phase 9-2 UI Surface Identification

Read-only Git確認:

- HEAD: `abbdafa12a735b1a90c7038f2d8f2347eb912c0d`
- Commit: `feat: advance phase 9 governance and experiment runtime`
- Phase 9-2固有Frontend面:
  - `frontend/src/components/ExperimentPanel.tsx`
  - `frontend/src/components/TopBar.tsx` のExperiment入口
  - `frontend/src/App.tsx` のOpen state／composition
  - `frontend/src/api/client.ts` の `/api/v7/experiment` Client
  - `frontend/src/types.ts` のExperiment DTO
  - `frontend/src/i18n/translations.ts`
  - `frontend/src/styles/app.css` のExperiment layout

Data ControlsはPhase 7由来で、`DataControlsPanel.tsx` 自体はPhase 8準備以前の履歴に存在する。最新Phase 9-2 CommitのData Controls名を持つ追加はPlanned Work文書であり、Data Controls UI本体を本Reworkの修正対象としていない。

## 3. Root Cause and Before／After

### 3.1 Button Contrast

Before:

- Global `button` は `color: var(--button-text)` を持つがbackgroundを持たない。
- Experiment入口、Plan作成、Run、Detail、Cancel、Closeが該当Semantic Classなしだった。
- Light Themeでは白系文字とBrowser既定灰色背景の組合せになり得た。

After:

- Experiment入口／Plan作成／Run: `primary`
- Detail／Close: `secondary`
- Cancel: `danger`
- DisabledはHTML `disabled` を保持し、実行中Runには `aria-busy` とVisible `Running` statusを追加した。
- Dangerは赤色だけでなく、既存の「Cancel／中止」というAction labelを保持する。

### 3.2 First Row then Error／No Progress

Before:

- `pollUntilTerminal()` 内の単発 `fetchExperimentRun()` Failureがそのままrejectした。
- `handleRun()` のcatchがGeneric Errorを出し、finallyでPollingを終了した。
- Backend Worker／Persistenceが後からTerminalへ進んでもFrontendは追跡を再開しなかった。
- Plan作成直後も `comparisonStatus="unavailable"` で、まだ要求していないComparisonを赤いErrorとして表示した。

After:

- status GETの一時Failureを120秒の既存Bounded deadline内でretryする。
- 成功した各Pollで当該Run行をupsertし、状態変化を画面へ反映する。
- retry中は「Backend実行は継続中」と明示し、Run Failureへ誤分類しない。
- deadline超過は「Run失敗」ではなく「状態を確認できない」と表示する。
- Run list／Comparison refreshは `Promise.allSettled()` で独立回収し、片方のFailureをUnhandled rejectionにしない。
- ComparisonはPlan作成時 `idle`、実際の取得失敗時だけ `unavailable`、既存表示後の取得失敗は `stale` とする。
- UIから同時に複数Variantをenqueueしないよう、1 Run追跡中は全Run Buttonをdisabledとした。BackendのFrozen Plan／single workerは変更していない。

## 4. End-to-End Trace Result

| Layer | Disposition | Evidence |
|---|---|---|
| Top-level Experiment入口 | FIXED | `TopBar.tsx` explicit `primary`; App test |
| Plan／Preset UI | PASS | Focused Frontend lifecycle／2 Variant tests |
| `/api/v7/experiment` Plan／Run／List／Comparison | PASS | Backend 53 focused／242 expanded |
| Frozen per-Variant config | PASS | same Production Plan 2 Variant integration test |
| Live Configuration Typed Reject | PASS（non-model） | `live_config_mismatch`, 409, adapter call 0; UI typed-message test |
| Configuration Lease／Worker | PASS | focused route／worker tests |
| Persistence／Comparison 2 rows | PASS（Fixture/non-model） | Backend comparison＋Frontend 2-row checklist test |
| Error presentation／Polling recovery | FIXED | transient status-read failure regression test |
| User Mac visual/interaction | NOT RUN | User Manual Gate |

## 5. Changed Paths

### Source

- `frontend/src/components/ExperimentPanel.tsx`
- `frontend/src/components/TopBar.tsx`
- `frontend/src/i18n/translations.ts`

### Tests

- `frontend/src/components/ExperimentPanel.test.tsx`
- `frontend/src/App.test.tsx`

### Generated canonical static asset

- `src/margpa_runtime_llm/web/static/app.js`

`frontend/src/styles/app.css` は既存Semantic Classで要件を満たすため変更していない。Build後のstatic `app.css`／`index.html`も内容差分なし。

## 6. Validation

### Before-fix diagnostic baseline

- Backend checklist representatives: 3 passed
- Frontend existing `ExperimentPanel`: 4 passed

既存Testには、Frontend 2 Variant連続実行、transient status-read failure recovery、typed reject表示の検証がなかった。

### After-fix focused

- `ExperimentPanel.test.tsx`＋`App.test.tsx`: 2 files／45 tests PASS
- Experiment routes／worker／live config／production adapter: 53 tests PASS

### Expanded／canonical

- Frontend Full: 34 files／335 tests PASS
- TypeScript typecheck: PASS
- ESLint: PASS
- Vite canonical build: PASS（60 modules transformed）
- Experiment unit suite＋route integration＋static route: 242 tests PASS
- `git diff --check`: PASS

Temp／CacheはProject内 `.venv/.t/phase_9_2_pre_manual_20260908/` に限定した。

## 7. Preservation

次を保持した。

- Phase 9-1 Main／Judge／Guard／Repair Component decoupling
- Provider identity、Call 0、Recording／Evidence truthfulness
- per-Variant Desired Configとper-Run Frozen Configの分離
- Configuration Lease内のfinal Live match
- single-threaded Tracked WorkerとPersistence
- R5成立済みReal Model Evidence（反復なし）

Network、Real Browser、Real Model Artifact、User `runtime_data`、Root外Model探索は実施していない。

## 8. Three-angle Self Review

### Angle A: Async Lifecycle／Race

- transient GET Failure後もBounded retryされる。
- terminal stateはsuccessful Pollとfinal refreshの両方から回収される。
- Run listとComparisonの片側Failureはもう片側の更新を妨げない。
- TimeoutをRun本体Failureと誤表示しない。

### Angle B: UI Semantics／Truthfulness

- primary／secondary／dangerのAction意味と可読背景を明示した。
- disabled attribute、`aria-busy`、Visible running statusで色だけに依存しない。
- never-requested／unavailable／stale Comparisonを分離した。
- Typed Backend messageをGeneric Errorへ潰さない。

### Angle C: Authority／Regression Boundary

- Backend Compositionは変更しない。
- Data Controlsへ触れない。
- Phase 9-1 Provider／Governance Authorityを変更しない。
- Browser／Real Model／User ManualをTest doubleでPASS扱いしない。
- Git write／Closure／Phase 9-3を行わない。

これは同一Task内の観点入替自己Reviewであり、Controller Independent Reviewではない。

## 9. Open Findings／Deferred Non-blockers

1. 昨日の実画面Failureの正確なAction、HTTP status、Browser consoleは未取得。User `runtime_data` 非接触Boundaryのため、構造欠陥と実イベントの一意な因果同定は未完了。
2. R5既知Finding（actual provider request correlation unavailable、`main_called` ambiguity、definition/RAG/presentation live not observed、各Real scenario 1 trial、identity API非公開）は本Rework外で継続する。
3. Cancel／Detail個別fetchの追加retry hardeningは昨日症状の確定Blockerではないため拡張しない。
4. 実Theme／実Browserの最終視認はUser Manual Gateに残る。

## 10. Incident／Concurrent Artifact Accounting

### Erroneous Worktree collision check

- 誤Task Worktree: `/Users/yukitakagi/.codex/worktrees/6279/margpa-runtime-llm`
- 現Project Rootとは別Worktree、同一HEAD detached。
- Tracked／Untracked Source Mutation: 0
- Build Artifact上書き: なし
- 更新確認: `.pytest_cache` のみ
- Related Listen Port: 検出なし
- Process list: Sandbox拒否により未確認
- 誤WorktreeへのMutation／削除／Git操作: なし

### Controller-owned concurrent document

次は本Task外で作成され、本Taskは変更していない。

- `docs/project/shared/history/ai_system_anomalies/codex/codex_controller_duplicate_task_creation_complete_wait_violation_and_cross_task_communication_approval_anomaly_ja_20260908154353.md`

### Cross-task communication anomaly

- Controllerへの重複途中送信がUser承認待ちとなり、Turnを中断した。
- Cross-task Message Toolは複数回 `user rejected MCP tool call` を返した。
- Codex UI経由の代替はComputer Use安全制約で拒否された。
- Userの再明示指示後の集約報告は最終的にTask間送信成功した。
- 原因はProduct SourceではなくTask Harness／Permission境界側で未確定。本Rework中に原因断定・追加調査を行っていない。

## 11. Acceptance and Exact Next Action

### Bounded Rework Acceptance

- Button readable semantic classes: PASS（Source/Test）
- Disabled／Danger non-color semantics: PASS（Source/Test）
- transient Poll Failure recovery: PASS（Test）
- Fixture two-row comparison: PASS（non-model Test）
- same Production Plan two variants: PASS（non-model integration）
- Wrong Live Config Typed Reject／Call 0: PASS（non-model integration＋UI Test）
- User Mac actual screen: NOT RUN

### Exact Next Action

1. ControllerはChanged 6 Paths、Validation、Open FindingsをIndependent Reviewする。
2. FindingがBlocker／Majorなら、このTaskの新規Authorityで差分Reworkする。MinorはDeferredに維持する。
3. Controller受理後、R5 User Mac Manual Checklistを新bundleでA → B → Cの順に実施する。
4. PASSの場合でもController／UserだけがPhase 9-2 Closure可否を判断する。
5. FAILの場合は、正確なclick順、表示文、HTTP code、Run ID／stateを固定してから次Reworkへ進む。

ここで停止し、Controller Independent Reviewを待つ。
