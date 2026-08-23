# Phase 4 Codex Manual Acceptance UI Rework Handoff

```yaml
document_id: phase_4_codex_manual_acceptance_ui_rework_handoff_20260822083500
status: rework_required
phase: phase_4
work_unit: p4_h_wu_004_manual_acceptance_mode_control_feedback
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-22 08:35:00 JST
trigger: user_mac_manual_acceptance_failure
predecessor: docs/project/phases/phase_4/handoffs/phase_4_claude_third_rework_complete_candidate_handoff_ja.md
supersedes_closure_recommendation: docs/project/phases/phase_4/history/operations/phase_4_codex_final_independent_review_ja_20260822081837.md
git_mutation: forbidden
phase_4_closure: forbidden
phase_5: forbidden
```

## 1. User Finding

ユーザーMac実画面で、Phase 3およびPhase 4の`OFF／OBSERVE／ENFORCE` Mode選択Buttonを押しても、選択状態が変化したことを視覚的に確認できなかった。

Phase 3の`ENFORCE`が仕様上Unavailableであることとは別問題であり、Phase 3の`OFF／OBSERVE`およびPhase 4のAvailable Modeにも同じ症状がある。

```text
Finding ID       : P4-CODEX-012
Severity         : MAJOR
Class            : USER-MAC MANUAL ACCEPTANCE FAILURE
Current Impact   : Mode Selectionの成否をUserが確認不能
Phase 4 Closure  : BLOCKED
```

## 2. Confirmed Root Cause

Frontend ComponentはRadio相当の選択状態を`aria-checked`で表現している。

```tsx
role="radio"
aria-checked={selectedMode === descriptor.mode}
```

対象：

- `frontend/src/components/GovernancePanel.tsx`
- `frontend/src/components/RuntimeGovernancePanel.tsx`

一方、選択Styleは`aria-pressed`だけを参照している。

```css
.configuration-toggle button[aria-pressed="true"] {
  background: var(--accent-strong);
}
```

対象：

- `frontend/src/styles/app.css`
- Build済み`src/margpa_runtime_llm/web/static/app.css`

したがって、React内部の`selectedMode`が更新されても画面上の選択表示が変化しない。Phase 3／4共通のSelector Contract不一致である。

既存Panel Testは初期`aria-checked`状態とUnavailable Modeを確認するが、Mode Button Click後の`aria-checked`遷移および選択ModeをApplyへ渡す動作を直接固定していない。Phase 3のApp TestはApply EndpointとPayloadを確認する一方、視覚状態契約を確認していない。Phase 4については同等のApp-level Apply経路Testも不足している。

## 3. Required Correction

### P4-CODEX-012-A：選択Style Contract

`aria-pressed`を使用する既存Controlを壊さず、Radio Roleの`aria-checked="true"`にも同じ選択Styleを適用する。

例：

```css
.configuration-toggle button[aria-pressed="true"],
.configuration-toggle button[aria-checked="true"] {
  background: var(--accent-strong);
}
```

単純に`aria-pressed`を削除・置換して、既存Controlの表示を壊してはならない。

### P4-CODEX-012-B：Phase 3 Interaction Test

`GovernancePanel`について、少なくとも次を直接Testする。

1. 初期`OFF=true／OBSERVE=false`。
2. `OBSERVE` Click後に`OFF=false／OBSERVE=true`。
3. 続けて`Apply` Clickすると`onApply("observe")`が1回呼ばれる。
4. `ENFORCE`は従来どおりUnavailable／Disabledであり、選択もApplyもされない。

### P4-CODEX-012-C：Phase 4 Interaction Test

`RuntimeGovernancePanel`について、少なくとも次を直接Testする。

1. 初期`OFF=true／OBSERVE=false`。
2. `OBSERVE` Click後に`OFF=false／OBSERVE=true`となり、Applyが`onApply("observe")`を受け取る。
3. Enforce-ready Snapshotでは`ENFORCE`を選択でき、Applyが`onApply("enforce")`を受け取る。
4. Enforce-unavailable Snapshotでは従来どおりDisabledを維持する。

### P4-CODEX-012-D：Phase 4 App Integration

実`App`配線で次を固定する。

1. Configuration ControlとRuntime GovernanceのBootstrapが有効な場合、Advanced ModeへPhase 4 Panelが表示される。
2. Mode選択後のApplyは既存Canonical `/api/v2/configuration/apply`だけを使用する。
3. Request Patchは`{ "main_governance_mode": "observe" }`または選択したExact Modeとなる。
4. 削除済みのRuntime Governance直接Mutation Routeを呼ばない。
5. Apply成功後のStatus再読により、Mode表示とRevisionがServer正本へ再同期する。

### P4-CODEX-012-E：Generated Static

Frontend Source修正後に正規Buildを行い、Python Web Runtimeが配信する次の生成物へ反映する。

```text
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html（Buildが変更した場合のみ）
```

Sourceだけ直してGenerated Staticを古いまま残してはならない。生成物へ手作業で独立Patchを当てず、正規Buildから同期する。

## 4. Exact Allowed Mutation Scope

```text
frontend/src/styles/app.css
frontend/src/components/GovernancePanel.test.tsx
frontend/src/components/RuntimeGovernancePanel.test.tsx
frontend/src/App.test.tsx

src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html

docs/project/phases/phase_4/handoffs/phase_4_claude_manual_acceptance_ui_rework_complete_candidate_handoff_ja.md
docs/project/phases/phase_4/history/index/<本Reworkに必要な新規Append-only Evidence 1件まで>
```

Component Sourceの`GovernancePanel.tsx`／`RuntimeGovernancePanel.tsx`は、現時点では`aria-checked`とState更新が正しいため、原則変更不要。追加の実欠陥を再現Testで確認した場合だけ、Exact理由を新規Completion Handoffへ記録したうえで最小変更を許可する。

## 5. Forbidden Scope

- Backend Governance Domain／Binding／Evaluator／Resolver／Evidence実装の再設計。
- Phase 3の`ENFORCE unavailable`契約変更。
- API SchemaまたはCanonical Configuration Mutation Pathの変更。
- `definitions/`、`runtime_data/`、Model、SecretまたはUser Chat Dataへの接触。
- Project Root外Action、Provider Memory、System Temp fallback。
- Existing Stable Docs／Historyの上書き・削除。
- Git Mutation、Commit、Push、Tag、Release。
- Phase 4 Closure、Phase 5開始。

## 6. Required Validation

Project Root内の短いTemporary Pathだけを使用し、最低限次を実行する。

```text
Frontend Component／App Focused Test : PASS
Frontend Full Test                   : PASS
Frontend Typecheck                   : PASS
Frontend Lint                        : PASS
Frontend Build                       : PASS
Generated Static Sync                : PASS
Relevant Backend Static Web Contract : PASS
git diff --check（Allowed Scope）     : PASS
```

Testでは単なる初期DOM存在確認ではなく、**実Click後の`aria-checked`遷移、Apply Callback Payload、App-level HTTP Patch**を確認する。

Claude側のBrowserを利用可能なら、Build後のローカルTest RuntimeでPhase 3／4の選択表示を確認してEvidence化してよい。ただしUser Chat Dataを含む既存`runtime_data/`は使用せず、新規隔離Test Runtimeだけとする。ユーザーMacの最終Acceptanceを代替したとは主張しない。

## 7. Completion Handoff Contract

Rework完了時は、次を新規Completion Handoffへ記録して停止する。

```text
P4-CODEX-012-A..E        : CLOSED／OPEN
Exact Changed Files      : 全件
Click Transition Tests   : Exact Test Name／Result
Apply Payload Tests      : Exact Test Name／Result
Frontend Full／Static    : Exact Tool Output
Generated Static Sync    : Evidence
Project Root外Action     : Verified Factだけを記録
Git Mutation             : NOT PERFORMED
Phase 4 Closure          : NOT PERFORMED
Phase 5                  : NOT STARTED
Remaining Major          : NONE／Exact Finding
```

「Testが通ったためユーザーMac表示も直った」と推測完了しない。Claude側は`COMPLETE_CANDIDATE`で停止し、Codex Independent ReviewとユーザーMac再Acceptanceを待つ。
