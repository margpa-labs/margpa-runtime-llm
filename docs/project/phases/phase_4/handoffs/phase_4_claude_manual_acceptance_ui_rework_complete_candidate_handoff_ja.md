# Phase 4 Claude Manual Acceptance UI Rework Complete Candidate Handoff

```yaml
document_id: phase_4_claude_manual_acceptance_ui_rework_complete_candidate_20260822084558
status: complete_candidate
phase: phase_4
work_unit: p4_h_wu_004_manual_acceptance_mode_control_feedback
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）
language: ja
recorded_at: 2026-08-22 08:45:58 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_manual_acceptance_ui_rework_handoff_ja_20260822083500.md
git_mutation: NOT_PERFORMED
phase_4_closure: NOT_PERFORMED
phase_5: NOT_STARTED
```

## 0. Repository Recovery宣言

Repository Recovery: PASS（Predecessor Handoffを全文読了し、Exact Allowed Mutation Scope内で作業した）
Git Mutation: FORBIDDEN（遵守——実行なし）
Phase 4 Closure: FORBIDDEN（遵守——着手なし）
Phase 5: FORBIDDEN（遵守——着手なし）

## 1. Summary

P4-CODEX-012（Mode Selection Buttonの選択状態がUser Mac画面で視覚的に確認できない）を修正した。根本原因はConfirmed Root Cause記載のとおり、`role="radio"` + `aria-checked`で選択状態を表現するComponentに対し、CSSが`aria-pressed`だけを選択Styleの対象にしていたSelector Contract不一致であった。

```text
P4-CODEX-012-A  選択Style Contract        : CLOSED
P4-CODEX-012-B  Phase 3 Interaction Test  : CLOSED
P4-CODEX-012-C  Phase 4 Interaction Test  : CLOSED
P4-CODEX-012-D  Phase 4 App Integration   : CLOSED
P4-CODEX-012-E  Generated Static          : CLOSED
```

Component Source（`GovernancePanel.tsx`／`RuntimeGovernancePanel.tsx`）は、Predecessor Handoffの事前分析どおり実際に正しく実装されており、追加の実欠陥は再現Testでも確認されなかった——そのため**無変更**である。修正はCSS 1箇所と、Test 3ファイルへの新規Interaction/Integration Testの追加、およびそれに伴う正規Frontend Buildによる生成物同期のみ。

## 2. P4-CODEX-012-A — 選択Style Contract

### 対応内容

`frontend/src/styles/app.css`の`.configuration-toggle button[aria-pressed="true"]`Selectorへ、`.configuration-toggle button[aria-checked="true"]`を追加した。既存の`aria-pressed`向けSelectorは削除・置換せず、そのまま維持している。

```css
.configuration-toggle button[aria-pressed="true"],
.configuration-toggle button[aria-checked="true"] {
  background: var(--accent-strong);
}
```

これにより、`role="radio"`のRadio Button（Phase 3の`GovernancePanel`／Phase 4の`RuntimeGovernancePanel`双方が使用）の`aria-checked="true"`にも、既存Toggle Buttonの`aria-pressed="true"`と同じ選択Styleが適用される。

## 3. P4-CODEX-012-B — Phase 3 Interaction Test

`frontend/src/components/GovernancePanel.test.tsx`に、Required Correctionの4項目を直接固定する新規Testを追加した（既存Testは無変更のまま維持）。

1. 初期`OFF=true／OBSERVE=false`：既存Test`Off and Observe stay enabled and reflect the current mode as checked`で確認済み（維持）。
2. `OBSERVE` Click後に`OFF=false／OBSERVE=true`：新規Test`clicking Observe flips its aria-checked state and clears Off's`。
3. 続けて`Apply` Clickで`onApply("observe")`が1回：新規Test`clicking Observe then Apply calls onApply with observe exactly once`。
4. `ENFORCE`はUnavailable／Disabledで選択もApplyもされない：新規Test`Enforce stays unselectable — clicking it never changes the checked Mode or reaches Apply`（Disabled Buttonへの`fireEvent.click`が`aria-checked`を変えないこと、その後のApplyが依然として`"off"`を渡すことを確認）。

## 4. P4-CODEX-012-C — Phase 4 Interaction Test

`frontend/src/components/RuntimeGovernancePanel.test.tsx`に同様の新規Testを追加した。

1. 初期`OFF=true／OBSERVE=false`：既存Test`Off stays enabled and reflects the current mode as checked`で確認済み（維持）。
2. `OBSERVE` Click後に`OFF=false／OBSERVE=true`となりApplyが`onApply("observe")`を受け取る：新規Test`clicking Observe flips aria-checked and Apply hands onApply the newly selected mode`。
3. Enforce-ready Snapshotで`ENFORCE`を選択でき、Applyが`onApply("enforce")`を受け取る：新規Test`with an Enforce-ready Snapshot, Enforce can be selected and Apply hands onApply "enforce"`。
4. Enforce-unavailable SnapshotではDisabledを維持：新規Test`with an Enforce-unavailable Snapshot, Enforce stays disabled and unselectable`。

## 5. P4-CODEX-012-D — Phase 4 App Integration

`frontend/src/App.test.tsx`に新規Testを4件追加した（既存のPhase 3向け同種Testと対になる構成）。実`App.tsx`のSource自体は無変更——既に正しくCanonical Apply経路のみを使用していたことをTestで確認した。

1. Configuration Control(`#configuration-bootstrap`)とRuntime Governance(`#runtime-governance-bootstrap`)双方のBootstrapが有効な場合にAdvanced ModeへPhase 4 Panelが表示される：`runtime governance status loads once the bootstrap tag reports enabled`（Disabled時に`#runtime-governance-panel`が存在せずFetchも発生しないことを確認する対Testも追加）。
2. Mode選択後のApplyが既存Canonical `/api/v2/configuration/apply`だけを使用する：`runtime governance apply goes through Configuration Control's apply endpoint, never a dedicated runtime governance mutation route, and resyncs Status after applying`。
3. Request Patchが`{ "main_governance_mode": "observe" }`（選択したExact Mode）になることを、実際のFetch Callのbodyを解析して確認。
4. 削除済みのRuntime Governance直接Mutation Route（`/api/v3/runtime-governance/mode`）が一切呼ばれないことを確認。
5. Apply成功後に`/api/v3/runtime-governance/status`が再度Fetchされる（Apply前後でCall数が増加する）ことを確認——Mode表示／RevisionがServer正本へ再同期することの直接証拠。

加えて、`runtime governance mode selection visually reflects the click before Apply is even pressed`をApp-level Integration Testとして追加し、Click直後の`aria-checked`遷移をApp全体の配線を通した実DOMで確認した（Component単体Testの結果がApp配線でも壊れていないことの二重確認）。

## 6. P4-CODEX-012-E — Generated Static同期

Frontend Source修正（`app.css`）後に`npm run build`（`tsc --noEmit && vite build`）を実行し、次のPython Web Runtime配信物へ正規反映した。

```text
src/margpa_runtime_llm/web/static/app.css    （Selector追加を反映、18.76kB → 18.80kB）
src/margpa_runtime_llm/web/static/app.js     （tsc型検査を通過した現行Sourceからの再Build——内容は既存と同一）
src/margpa_runtime_llm/web/static/index.html （Buildにより再生成——Bootstrap Tag 3種は引き続きVerbatimで存在）
```

生成物への手作業Patchは一切行わず、すべて`npm run build`の出力をそのまま反映した。Bootstrap Tag（`#configuration-bootstrap`／`#governance-bootstrap`／`#runtime-governance-bootstrap`）が Build後もVerbatimで存在することを`grep`で確認済み。

## 7. Required Validation 実施結果

```text
P4-CODEX-012-A..E                  : CLOSED
Exact Changed Files                : 下記§8参照
Click Transition Tests             : 下記§7.1参照
Apply Payload Tests                : 下記§7.1参照
Frontend Full／Static              : Exact Tool Output — §7.2参照
Generated Static Sync              : Evidence — §6参照（Build成功、Bootstrap Tag Verbatim確認）
Relevant Backend Static Web Contract: PASS — tests/unit/web + tests/integration/web 162 passed
Project Root外Action               : NOT PERFORMED（全Command/mkdirはProject Root内相対Pathのみ使用）
Git Mutation                       : NOT PERFORMED
Phase 4 Closure                    : NOT PERFORMED
Phase 5                            : NOT STARTED
Remaining Major                    : NONE
```

### 7.1 Click Transition Tests／Apply Payload Tests（Exact Test Name／Result）

```text
GovernancePanel.test.tsx
  clicking Observe flips its aria-checked state and clears Off's                                    : PASS
  clicking Observe then Apply calls onApply with observe exactly once                                : PASS
  Enforce stays unselectable — clicking it never changes the checked Mode or reaches Apply            : PASS

RuntimeGovernancePanel.test.tsx
  clicking Observe flips aria-checked and Apply hands onApply the newly selected mode                : PASS
  with an Enforce-ready Snapshot, Enforce can be selected and Apply hands onApply "enforce"           : PASS
  with an Enforce-unavailable Snapshot, Enforce stays disabled and unselectable                       : PASS

App.test.tsx
  runtime governance status stays out of the DOM and unfetched when the bootstrap tag reports disabled: PASS
  runtime governance status loads once the bootstrap tag reports enabled                              : PASS
  runtime governance mode selection visually reflects the click before Apply is even pressed          : PASS
  runtime governance apply goes through Configuration Control's apply endpoint, never a dedicated
    runtime governance mutation route, and resyncs Status after applying                              : PASS
```

### 7.2 Frontend Full／Static（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" npm run test
Test Files  18 passed (18)
     Tests  142 passed (142)

$ TMPDIR="$PWD/.p4t/t" npm run typecheck
> tsc --noEmit
(no output — success)

$ TMPDIR="$PWD/.p4t/t" npm run lint
> eslint .
(no output — success)

$ TMPDIR="$PWD/.p4t/t" npm run build
✓ 42 modules transformed.
../src/margpa_runtime_llm/web/static/index.html    0.68 kB
../src/margpa_runtime_llm/web/static/app.css      18.80 kB
../src/margpa_runtime_llm/web/static/app.js      272.72 kB
✓ built in 84ms

$ git diff --check -- frontend/src/styles/app.css frontend/src/components/GovernancePanel.test.tsx \
    frontend/src/components/RuntimeGovernancePanel.test.tsx frontend/src/App.test.tsx \
    src/margpa_runtime_llm/web/static/app.css src/margpa_runtime_llm/web/static/app.js \
    src/margpa_runtime_llm/web/static/index.html
(no output — exit 0, no whitespace errors)
```

### 7.3 Relevant Backend Static Web Contract（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest tests/unit/web tests/integration/web -q --basetemp="$PWD/.p4t/p-full"
162 passed in 2.37s
```

### 7.4 Project-local Test Temp（Exact Path／Cleanup／Postflight）

```text
Exact Base Root : <PROJECT_ROOT>/.p4t
Created         : .p4t/p-focused, .p4t/p-full, .p4t/t（本Cycleが新規作成、都度Cleanup）
Postflight       : `rm -rf .p4t` 実行後 `test -d .p4t` で不存在を確認、
                  `git status --short | grep p4t` で追跡対象からも消えていることを確認済み。
System Temp/`/tmp`/Provider Cache Fallback: 発生なし。
```

## 8. Changed Files（本Cycle、全件）

```text
frontend/src/styles/app.css
frontend/src/components/GovernancePanel.test.tsx
frontend/src/components/RuntimeGovernancePanel.test.tsx
frontend/src/App.test.tsx

src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
```

`GovernancePanel.tsx`／`RuntimeGovernancePanel.tsx`／`App.tsx`は、既に正しく実装されていることをTestで確認したため無変更。Exact Allowed Mutation Scope外のファイルへの変更はない。

## 9. Project Root外Action（Verified Fact）

本Cycle中に実行した全Command（`npm run *`、`./.venv/bin/python -m pytest`、`git status`／`git diff`、`mkdir`／`rm -rf .p4t`、`grep`）は、Project Root内の相対Pathのみを対象とした。System Temp／`/tmp`／`/private/tmp`／Provider Cacheへのアクセスは発生していない。`definitions/`／`runtime_data/`／Model／Secret／User Chat Dataへの接触もない。

## 10. Remaining Items

技術的Major Findingの残件なし（NONE）。

「Testが通ったためユーザーMac表示も直った」とは推測しない——本Cycleで行ったのはSelector Contractの修正と、実Click／実Apply Payload／実App配線を対象にしたAutomated Test（jsdom環境）による固定のみである。実際のユーザーMac Browser表示の最終確認は、Codex Independent ReviewとユーザーMac再Acceptanceに委ねる。

## 11. Stop

本Handoff作成をもって`COMPLETE_CANDIDATE`として停止する。Phase 4 Closure、Git操作、Phase 5開始には進まない。
