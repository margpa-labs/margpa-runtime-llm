---
document_type: phase_recovery_index
language: ja
title: Phase 9-2 IR-P9-2-UI-01 Bounded Rework Recovery
created_at: 2026-09-08T16:21:10+09:00
author_role: 設計者兼実装者役
recording_policy: append_only
status: complete_candidate_for_controller_review
maximum_claim: P9_2_USER_MANUAL_CANDIDATE
supersedes_for_rework_result: phase_9_2_pre_user_manual_ui_blocker_major_rework_recovery_ja_20260908155658.md
---

# Phase 9-2 IR-P9-2-UI-01 Bounded Rework Recovery

## 1. Fixed Point

- Finding: `IR-P9-2-UI-01`（MAJOR）
- Disposition: FIXED CANDIDATE
- Controller Independent Re-review: NOT RUN
- User Mac Manual: NOT RUN
- Phase 9-2 Complete／Phase 9-3／Closure: NOT CLAIMED
- Git write: NOT RUN
- Real Browser／Real Model: NOT RUN

最大Claimは `P9_2_USER_MANUAL_CANDIDATE` のまま維持する。

## 2. Delta Completed

1. 120秒の自動追跡上限到達時、Run list／ComparisonをGET-onlyで最終refreshする。
2. 最終refreshが同じRunのTerminalを返せば、tracking Errorを出さずTerminal表示へ収束する。
3. まだ非Terminalなら同じ `run_id` を保持し、「同じRunの状態を再確認」Buttonを表示する。
4. Recheckは `GET /api/v7/experiment/runs/{same_run_id}` とGET-only refreshだけを使い、`POST /runs` を行わない。
5. RecheckでTerminalを得たら、追跡ErrorとRecheck Buttonを消し、Terminal rowへ収束する。
6. Run state mergeを単調化し、Terminal観測後に後着した同Generationの `planned`／`running` がTerminalを巻き戻さない。
7. Recheck中／Still running／Recheck Actionの日本語・英語表示を追加した。

## 3. Changed Delta Paths

- `frontend/src/components/ExperimentPanel.tsx`
- `frontend/src/components/ExperimentPanel.test.tsx`
- `frontend/src/i18n/translations.ts`
- `src/margpa_runtime_llm/web/static/app.js`

先行Reworkの `TopBar.tsx`／`App.test.tsx` 差分は保持し、本Findingでは変更していない。Backend Source、Data Controls、Provider／Governance Compositionも変更していない。

## 4. Validation

- Frontend Focused: 2 files／47 tests PASS
- Frontend Full: 34 files／337 tests PASS
- TypeScript typecheck: PASS
- ESLint: PASS
- Vite canonical build: PASS（60 modules transformed）
- Built static asset route: 1 test PASS
- `git diff --check`: PASS

先行Reworkで成立済みのBackend Experiment 53 focused／242 expandedは、Backend Source変更がないため反復していない。

新規回帰Test:

1. 120秒後にRecheckを表示し、同じRunのGETでTerminalへ収束、tracking Errorを消し、Run POST回数が1のままである。
2. 120秒境界の最終Run-list refreshがTerminalを返した場合、Recheckもtracking Errorも残さない。
3. Recheck後に古い `running` list responseが後着してもTerminal表示を巻き戻さない。

## 5. Exact Remaining

1. ControllerがIR-P9-2-UI-01差分をIndependent Re-reviewする。
2. 受理後、User Macで155〜160秒級Production Runを含むR5 Checklistを実施する。
3. 自動追跡上限後もRunが非Terminalなら「同じRunの状態を再確認」を押し、同じRunがTerminalへ収束することを実画面確認する。
4. User Manual結果がFAILの場合のみ、同じRun ID、表示Error、HTTP response、最終stateを固定して次のBounded Reworkへ進む。

## 6. Resume Rule

Controller FindingまたはUser Manualの新Evidenceがない限り、成立済みFrontend Full、Backend Test、Buildを反復しない。再開時に新しいRunをPOSTして既存Runの追跡を代替してはならない。
