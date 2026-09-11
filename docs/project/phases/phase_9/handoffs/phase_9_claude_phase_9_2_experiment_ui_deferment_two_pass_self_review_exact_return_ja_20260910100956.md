# Phase 9-2 Experiment UI延期 最小Rework — 2段階観点入れ替え自己Review Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_experiment_ui_deferment_two_pass_self_review_exact_return_20260910100956
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-10 10:09:56 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_ja_20260910095659.md
trigger: user_direct_instruction_two_pass_perspective_swap_self_review
maximum_claim: P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_SERVED_ARTIFACT_VERIFIED_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 0. 本Returnの位置付け

ユーザーから直接、直前のRound（`phase_9_claude_phase_9_2_experiment_ui_deferment_and_headless_core_minimum_rework_exact_return_ja_20260910095659.md`）に対する「2段階、完全観点入れ替えの自己Review」指示があった。新規Controller Handoffは発行されていないが、既存の運用規則（Codex Returnはexact_return_handoff形式、Append-only、新規Recovery必須）を踏襲してAppend-onlyで記録する。

## 1. Maximum Claim（最大Claim）

`P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_SERVED_ARTIFACT_VERIFIED_CANDIDATE_FOR_CONTROLLER_REVIEW`

前Roundの`P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_CANDIDATE_FOR_CONTROLLER_REVIEW`から一段階前進——今回、**実際に配信される静的Bundle自体**がExperiment入口を含まないことを機械確認できたため、`SERVED_ARTIFACT_VERIFIED`を追加する。

## 2. Review設計（2段階・観点入れ替え）

| Pass | 観点 | 確認方法 |
|---|---|---|
| Pass 1 | Source-level正しさ／取りこぼし——「削除は本当に完全か、他に見落としたMount／Import／CSS／翻訳Keyはないか」 | `frontend/src`全体をGrepし、`TopBar`／`ExperimentPanel`／`experiment-toggle`／`experimentToggleLabel`の全参照箇所を洗い出し |
| Pass 2 | 実配信物（Served Artifact）の観点——「Source上の削除が、実際にUserのBrowserへ届くBuild成果物に反映されているか」 | `src/margpa_runtime_llm/web/static/`（FastAPI `StaticFiles`が配信する実Bundle）の内容を直接Grepし、Source側の変更と乖離していないか確認 |

Pass 1とPass 2は意図的に全く異なる問いを立てている——前者は「Reactの世界で正しいか」、後者は「Backendが実際に返すByte列として正しいか」であり、後者は前RoundのFocused Test（jsdom上のReact Render）やTypecheckでは検出できない種類のGapを狙った。

## 3. Findings

### Finding 1（CRITICAL、Pass 2で検出）— 実配信Static Bundleが未Rebuildのまま

前Roundは`frontend/src/App.tsx`／`TopBar.tsx`を編集し、Focused Test・Typecheck・LintをPASSさせたが、Quota節約のため`npm run build`（`vite build`）を意図的にSkipしていた。

`vite.config.ts`の`build.outDir`は`src/margpa_runtime_llm/web/static/`を直接指しており（`emptyOutDir: true`）、FastAPIの`StaticFiles`はこのDirectoryをそのままUserへ配信する。つまり**Source変更後にBuildを実行するまで、実際にUserのBrowserへ届くApp（`app.js`/`app.css`/`index.html`）は前Round開始前のまま**だった。

確認: Rebuild前の`src/margpa_runtime_llm/web/static/app.js`には`experiment-toggle`文字列が2件、`実験`文字列が2件残存していた（Grep実測）。前Round Returnの「通常UIにExperiment Buttonがない」というMinimum Acceptance Claimは、**Source上は真だが、実配信物としては未達**だった。

**修正**: `npm run build`（`tsc --noEmit && vite build`）を実行し、`src/margpa_runtime_llm/web/static/{app.js,app.css,index.html}`を再生成。Rebuild後、`experiment-toggle`は`app.js`/`app.css`とも0件に減少（Grep再実測）。旧`app.js`385,744 bytes → 新373.34kB（gzip 101.95kB）——`ExperimentPanel`自体もEntry Pointから到達不能になったため、Bundlerが自然にTree-shakingした結果であり、`ExperimentPanel.tsx`Source自体は無削除のまま。

### Finding 2（MINOR、Pass 1で検出）— 死んだCSS Rule

`frontend/src/styles/app.css`の`.experiment-toggle { margin-left: 8px; }`が、Button要素削除後もSourceに残存していた（`.experiment-panel`以下のExperimentPanel内部Style群とは別物で、Toggle Button専用のRuleだった）。

**修正**: 当該Rule自体を削除。直上のBlock Commentは、残る`.experiment-panel*`系RuleがExperimentPanel内部用として引き続き有効である旨を明記する形に更新。

### Finding 3（MINOR、Pass 1で検出）— 死んだ翻訳Key

`frontend/src/i18n/translations.ts`のja/en両方に`experimentToggleLabel`Keyが残存していた（Button削除後、参照元が消滅）。

**修正**: ja/en両方から`experimentToggleLabel`Entryを削除。同ファイルの`experimentPanelTitle`等、`ExperimentPanel.tsx`自身が引き続き使用するKeyは無変更で保持。

## 4. 修正後の検証

| 項目 | 結果 |
|---|---|
| Frontend Typecheck（`npm run build`内の`tsc --noEmit`） | Error 0件 |
| Frontend Build（`vite build`） | 成功、`app.js` 373.34kB（旧385.7kB） |
| 静的Bundle内`experiment-toggle`残存数 | `app.js`: 0件（Rebuild前2件）、`app.css`: 0件（Rebuild前2件） |
| Focused + i18n Test（`App.test.tsx` + `translations.test.ts`） | 43 passed |
| Frontend Full Test Suite（`npm test`） | **339 passed, 34 files, 0 failed**（前Roundは未実施だった項目。今回のFinding修正の波及範囲確認のため実施） |
| Frontend Lint | Error/Warning 0件 |
| Backend Targeted Regression（`tests/integration/web/test_web_app.py`のみ、Full Suiteではない） | 32 passed（静的配信Routeが新Bundleでも正常応答することを確認するため、直接関連するFileのみ実行） |

Backend Full Suite・Real Model・Browserは今回も未実施（既存Handoffの禁止事項を継続して尊重）。

## 5. Files Changed（本Round追加分）

| File | 変更内容 |
|---|---|
| `frontend/src/styles/app.css` | 死んだ`.experiment-toggle`Rule削除、直上Comment更新 |
| `frontend/src/i18n/translations.ts` | 死んだ`experimentToggleLabel`Key削除（ja/en） |
| `src/margpa_runtime_llm/web/static/app.js`（Build成果物、Source編集ではない） | `npm run build`によるRegenerate。実際に配信されるExperiment入口の除去が完了 |
| `src/margpa_runtime_llm/web/static/app.css`（同上） | 同上 |
| `src/margpa_runtime_llm/web/static/index.html`（同上） | 同上（内容差分は軽微） |

前Round分（`App.tsx`／`TopBar.tsx`／`App.test.tsx`）は無変更のまま維持。

## 6. Review A（Pass 1: Source完全性）

- `frontend/src`全体で`TopBar`／`ExperimentPanel`／`experiment-toggle`／`experimentToggleLabel`の残存参照を検索——`ExperimentPanel.tsx`／`ExperimentPanel.test.tsx`自身以外に取りこぼしなし（他Componentからの参照ゼロ）。
- 死んだCSS Rule・翻訳Keyの2件を検出・修正。いずれもSafe（他の`.primary`等共有Classへの影響なし、`translations.test.ts`のKey整合性Testが通過を確認）。

## 7. Review B（Pass 2: 実配信Artifact整合性）

- **Handoffの`required_invariants`「The experiment toggle is absent from the normal UI.」は、Source上のReact Tree構造だけでなく、実際にUserへ配信されるByte列（Static Bundle）でも成立していなければ真の意味で満たされない**——前RoundはSourceのみで判定しており、この観点が漏れていた。
- `vite.config.ts`の`build.outDir`が`src/margpa_runtime_llm/web/static/`を直接指す構成（Node分離Serverを持たない単一Process配信Model）を確認し、Buildが単なる「Optionalな追加検証」ではなく「実配信物を更新する必須Step」であることをArchitecture上で裏付けた。
- 静的配信Route（`/assets/app.js`等）の実応答をTargeted Backend Testで確認し、新Bundleが正常に配信されることも確認済み。

## 8. Open Findings（未解決点、変更なし）

- 前Round同様、`ExperimentPanel.tsx`自体のCancel／Reset／Details／Polling導線の修復はScope外で未着手（Phase 11以降）。
- 今回はFull Test Suiteおよび該当するBackend Regression Fileを実施済み——前Round時点のOpen Finding「Full Test/Build未実施」は本Roundで解消。

## 9. Action Inventory

**Read**: なし（既存Session内Context利用、追加File読込は前Round分と本Round用Grep結果のみ）。

**Bash（Grep／確認系）**: `frontend/src`全体Grep（TopBar／ExperimentPanel／CSS／`.primary`使用箇所）、Static Bundle Grep（Rebuild前後の`experiment-toggle`/`実験`件数）、`vite.config.ts`確認、`git rev-parse HEAD`／`git stash list`（Read-onlyのみ）。

**Edit**: `frontend/src/styles/app.css`（1箇所）、`frontend/src/i18n/translations.ts`（2箇所、ja/en）。

**Bash（Build／Test実行系）**: `npm run build`、`npm test -- src/App.test.tsx src/i18n/translations.test.ts`、`npm test`（Full Suite）、`npm run lint`、`uv run pytest tests/integration/web/test_web_app.py`（Targeted）。

**Git／Process状態**: Git操作は`rev-parse`/`stash list`のRead-onlyのみ。`add`/`commit`/`push`/`stash`/`clean`/`reset`/`checkout`いずれも未実行。HEAD不変（`abbdafa`）。Network、Root外Mutationなし。Real Model、Browser実行なし。新規Task／Subagent／Delegation不使用。

## 10. Exact Next Action

Codex Controller Independent Reviewを待つ。追加Rework、User Manual、Phase Completion、Git操作、次Phaseへの着手のいずれも、本Returnの範囲では行わない。
