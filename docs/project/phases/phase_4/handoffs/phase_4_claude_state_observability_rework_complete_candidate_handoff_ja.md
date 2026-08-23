# Phase 4 Claude State／Observability Rework Complete Candidate Handoff

```yaml
document_id: phase_4_claude_state_observability_rework_complete_candidate_20260822093637
status: complete_candidate
phase: phase_4
work_unit: p4_h_wu_005_state_observability_and_semantic_boundary
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）
language: ja
recorded_at: 2026-08-22 09:36:37 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_manual_acceptance_state_observability_rework_handoff_ja_20260822091607.md
git_mutation: NOT_PERFORMED
phase_4_closure: NOT_PERFORMED
phase_5: NOT_STARTED
phase_6_implementation: NOT_STARTED
```

## 0. Execution Order宣言

先行`phase_4_codex_manual_acceptance_ui_rework_handoff_ja_20260822083500.md`（P4-CODEX-012）は、本Cycle開始前に既に`docs/project/phases/phase_4/handoffs/phase_4_claude_manual_acceptance_ui_rework_complete_candidate_handoff_ja.md`としてComplete Candidate化済みである。本Handoffはその実差分（`aria-checked`選択Style Contract修正、Interaction/App Integration Test追加、Generated Static同期）を確認した上で、本Work Unit（P4-CODEX-013〜015）へ進んだ。

## 1. Summary

```text
P4-CODEX-013 (Canonical Mode Selection Sync)         : CLOSED
P4-CODEX-014 (Chat Terminal後のStatus Refresh)        : CLOSED
P4-CODEX-015 (Semantic Capabilityの誤認防止)          : CLOSED
Predecessor P4-CODEX-012                             : docs/project/phases/phase_4/handoffs/phase_4_claude_manual_acceptance_ui_rework_complete_candidate_handoff_ja.md（CLOSED、本Cycleでは無変更）
Semantic Evaluator                                    : NOT IMPLEMENTED／DEFERRED TO PHASE 6
Generated Static Sync                                 : PASS
```

## 2. P4-CODEX-013 — Canonical Mode Selection Sync

### Confirmed Root Cause（再確認）

`GovernancePanel`／`RuntimeGovernancePanel`は`selectedMode`を常にハードコード`"off"`で初期化する一方、`syncedRevision`は`status?.mode.revision`（既に読み込み済みのRevision）で初期化していた。Settings Modalは`open={false}`で`return null`（完全Unmount）するため、再Open時にこれらComponentは再Mountされる——その際、既にServer Statusが存在していれば`syncedRevision`は最初からその値と一致し、`if (status?.mode.revision !== syncedRevision)`分岐が一度も走らず、`selectedMode`が誤って`"off"`のまま固定される。

### 対応内容

`frontend/src/components/GovernancePanel.tsx`／`frontend/src/components/RuntimeGovernancePanel.tsx`の`selectedMode`初期化を、`syncedRevision`と同じ情報源から導出するよう変更した。

```tsx
// Before
const [selectedMode, setSelectedMode] = useState<GovernanceMode>("off");

// After
const [selectedMode, setSelectedMode] = useState<GovernanceMode>(
  () => status?.mode.current_mode ?? "off",
);
```

（`RuntimeGovernancePanel`も同様に`status?.current_mode ?? "off"`。）

Revision差分による再同期Logic自体（`if (status?.mode.revision !== syncedRevision) { ... }`）は無変更——「Userが未Applyの選択中に無関係な同Revision再Renderで強制OFFへ戻す」ことは元々発生しない設計であり、今回もその挙動を壊していない。Apply成功時は`loadRuntimeGovernanceStatus()`／`loadGovernanceStatus()`がServerの新Revision／新Mode付きStatusを返し、既存の再同期分岐がそのまま収束させる。

### Test

`tests/unit`のComponent Testおよび`App.test.tsx`のApp-level Testの両方で固定した。

## 3. P4-CODEX-014 — Chat Terminal後のRuntime Governance Status Refresh

### 対応内容

`frontend/src/App.tsx`の3つのTerminal収束点（`finally`Block）すべてに、`void loadRuntimeGovernanceStatus();`（Fire-and-forget、Best-effort）を追加した。

1. `sendEphemeralMessage()` — Ephemeral Chatの正常Completion／Reject／Error／Cancel全経路（`finally`が必ず実行される）。
2. `sendPersistentMessage()` — Persistent New Turnの同経路（既存の`await loadPersistentDetail()`／`await loadPersistentList()`の後）。
3. `persistentDerivedAction()` — Retry／Regenerate等のDerived Turnの同経路。

`loadRuntimeGovernanceStatus()`自体は`runtimeGovernanceBootstrapEnabled`が`false`なら即Returnする既存のGuardを持ち、かつ内部で自身のFetch失敗を`try/catch`で`capability: "failed"`へ変換して握り潰す（例外を外へ伝播しない）。そのため：

- Status再読失敗はGeneration Result／Conversation Commit／表示済みCanonical Answerに一切影響しない（`void`で切り離し、`finally`本体の後続処理より後に配置）。
- OFF相当（Bootstrap Disabled）時は追加Fetch 0のまま。
- Public／Basic Preview境界（`runtimeGovernanceBootstrapEnabled`が有効化されない構成）にも影響しない。
- 各Terminal収束点で厳密に1回だけ呼び出す（Per-Event Handlerではなく`finally`側にのみ配置——重複Fetchや無限Pollを作らない）。

### Test（`frontend/src/App.test.tsx`）

新規Fetch Route（`persistentTurnStream`／`persistentDerivedStream`、および`/api/v3/runtime-governance/status`）を`installFetchMock`へ追加した上で、下記5件を追加した。

## 4. P4-CODEX-015 — Semantic Capabilityの明示

### 対応内容

`frontend/src/components/RuntimeGovernancePanel.tsx`のTitle直下へ、新規`id="runtime-governance-semantic-boundary-notice"`の`<p>`を追加し、`frontend/src/i18n/translations.ts`へ日本語／英語双方の新規Key`runtimeGovernanceSemanticBoundaryNotice`を追加した。

```text
ja: "Phase 4のARGD／DAGD意味RuleはSemantic Evaluator未接続のためDeferredです。現在のENFORCEは登録済みの構造的Deviation（空Output・Size Budget超過等）だけへ介入します。知ったかぶり・根拠のない断定・推論品質など意味的FailureのJudge／RepairはPhase 6で接続予定です。"
en: "Phase 4's ARGD/DAGD semantic Rules are Deferred because no Semantic Evaluator is connected yet. Enforce today only intervenes on registered structural Deviations (empty output, size-budget overruns, etc). Judging and Repairing semantic Failures — bluffing, unfounded assertions, poor reasoning quality — is planned for Phase 6."
```

さらに§3.3（下記）の一部として、`main_model.pre`／`main_model.post`の各Point行へ`Observation数（Pass/Deviation/Deferred内訳）`を表示し、「ARGD／DAGD由来Descriptorは常にDeferredへ数えられる」ことを実データで裏付けた。

Phase 6のSemantic Evaluator／Judge／Repairは実装していない——本対応はUI／Statusの正確な現状表示のみである。

## 5. P4-CODEX-013 §3.3 — Safe Observation Summary Projection

### 対応内容

`src/margpa_runtime_llm/web/runtime_governance_routes.py`の`GovernancePointStatusResponse`へ、`observation_count`／`pass_count`／`deviation_count`／`deferred_count`（すべて`int | None`）を追加した。新設`_observation_summary()`が同一`StandardGovernanceResult.observations`から一度だけ、明示的な`ObservationOutcome`一致判定で集計する——将来Outcomeが追加された場合も、未知値は`observation_count`（Total）にのみ計上され、`pass_count`へ暗黙的に算入されることはない（If/Elifの明示分岐、`else`句なし）。

```python
def _observation_summary(result: StandardGovernanceResult) -> tuple[int, int, int, int]:
    pass_count = 0
    deviation_count = 0
    deferred_count = 0
    for observation in result.observations:
        if observation.outcome is ObservationOutcome.PASS:
            pass_count += 1
        elif observation.outcome is ObservationOutcome.DEVIATION:
            deviation_count += 1
        elif observation.outcome is ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR:
            deferred_count += 1
    return len(result.observations), pass_count, deviation_count, deferred_count
```

Definition本文／Rule全文／Prompt／Output／User Content／Absolute Path／Raw Exception／Secretは一切含まれない——投影されるのはCountの4整数のみ。

`frontend/src/types.ts`の`RuntimeGovernancePointStatus`へ対応する4 Fieldを追加し、`frontend/src/components/RuntimeGovernancePanel.tsx`のPoint別表示へ`Observations: N (Pass n, Deviation n, Deferred (awaiting semantic evaluation) n)`を追加した。`frontend/src/i18n/translations.ts`へ`runtimeGovernancePointObservationCount`／`runtimeGovernancePointPassCount`／`runtimeGovernancePointDeviationCount`／`runtimeGovernancePointDeferredCount`（ja/en）を追加した。

## 6. Required Tests 実施結果（Exact Test Name／Result）

### 6.1 Panel State（Mode Reopen／Revision Tests）

```text
GovernancePanel.test.tsx
  mounting directly with an Observe status selects Observe, not Off              : PASS
  a new Status Revision re-syncs the selected Mode to the Server's Current Mode  : PASS

RuntimeGovernancePanel.test.tsx
  mounting directly with an Observe status selects Observe, not Off             : PASS
  mounting directly with an Enforce status selects Enforce, not Off             : PASS
  a new Status Revision re-syncs the selected Mode to the Server's Current Mode : PASS

App.test.tsx
  closing and reopening Settings keeps the Server's Current Mode selected,
    for both Phase 3 and Phase 4 Panels                                        : PASS
```

### 6.2 Chat／Status Refresh（Exact Path／Test／Call Count）

```text
Path: /api/v3/runtime-governance/status（GET、再読）

App.test.tsx
  runtime governance status refreshes exactly once after an ephemeral chat
    terminates                                                          : PASS（Call Count: +1 per send）
  runtime governance status refreshes exactly once after a persistent
    turn terminates                                                     : PASS（Call Count: +1 per send）
  runtime governance status refreshes exactly once after a derived
    (retry/regenerate) turn terminates                                  : PASS（Call Count: +1 per action）
  a runtime governance status refresh failure never rewrites the
    completed chat result                                               : PASS（Status GET Reject、
                                                                             Chat Result・エラー表示なし）
  no extra runtime governance status GET happens when the bootstrap tag
    reports disabled                                                    : PASS（Call Count: 0）
```

### 6.3 Observation Count Projection（Exact Contract／Test）

```text
Contract: GovernancePointStatusResponse.{observation_count,pass_count,deviation_count,deferred_count}

test_runtime_governance_web_app.py
  test_observe_status_projects_pass_deviation_and_deferred_observation_counts : PASS
    （observation_count=3, pass_count=1, deviation_count=1, deferred_count=1,
      executed_action_count=0——OBSERVEはAction Resolverへ未到達のままCount可視）
  test_status_reports_zero_observation_counts_when_no_observation_ran         : PASS
    （Definitions-0 Baseline、observation/pass/deviation/deferred count 全て0）

RuntimeGovernancePanel.test.tsx
  shows the per-Point Observation pass/deviation/deferred breakdown          : PASS
```

Raw Content／Path／Exception／Secretの非混入は`test_observe_status_projects_pass_deviation_and_deferred_observation_counts`内で`"a real answer" not in status.text`／`"Traceback" not in status.text`／`"/Users/" not in status.text`として明示的に確認した。

### 6.4 Semantic Boundary

```text
test_runtime_governance_web_app.py
  test_enforce_never_intervenes_with_only_a_deferred_semantic_descriptor : PASS
    （ARGD Descriptorはdeferred_count=1として計上され、pass/deviationへ偽装されない。
      通常回答"a real answer"はEnforceでも無変更のまま通過——
      「ENFORCEが意味的Failureを修復・再生成した」というClaim／Testは作成していない）

RuntimeGovernancePanel.test.tsx
  shows the Semantic Boundary notice — Enforce only intervenes on structural
    Deviations today                                                    : PASS

既存Structural Enforce Regression（無変更、Pass継続）
  test_enforce_mode_rejects_empty_output_with_a_safe_terminal            : PASS
  test_enforce_mode_allows_a_normal_answer_through                      : PASS
```

## 7. Validation ラダー実施結果

```text
Full／Focused／Static : Exact Tool Output — 下記参照。
Generated Static Sync : PASS — 下記§7.4参照。
Root-outside Action    : Verified Fact — 全Command/mkdirはProject Root内相対Pathのみ使用（NOT PERFORMED）。
Git Mutation           : NOT PERFORMED。
Phase 4 Closure        : NOT PERFORMED。
Phase 5／6             : NOT STARTED。
Remaining Major        : NONE。
```

### 7.1 Backend Focused（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest \
    tests/integration/web/test_runtime_governance_web_app.py \
    tests/integration/web/test_runtime_governance_persistent_and_rag.py \
    tests/integration/web/test_runtime_governance_public_basic_call0.py \
    tests/unit/web tests/integration/web \
    -q --basetemp="$PWD/.p4t/p-focused"
165 passed in 2.39s
```

### 7.2 Backend Full／Static（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest -q --basetemp="$PWD/.p4t/p-full"
1048 passed, 3 deselected in 62.69s

$ ./.venv/bin/ruff check src tests
All checks passed!

$ ./.venv/bin/ruff format --check src tests
274 files already formatted

$ ./.venv/bin/mypy src
Success: no issues found in 178 source files
```

### 7.3 Frontend Focused／Full／Static（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" npx vitest run src/App.test.tsx src/components/GovernancePanel.test.tsx \
    src/components/RuntimeGovernancePanel.test.tsx
Test Files  3 passed (3)
     Tests  51 passed (51)

$ TMPDIR="$PWD/.p4t/t" npm run test
Test Files  18 passed (18)
     Tests  155 passed (155)

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
../src/margpa_runtime_llm/web/static/app.js      274.41 kB
✓ built in 86ms

$ git diff --check -- <Exact Allowed Mutation Scope内Files>
(no output — exit 0, no whitespace errors)
```

### 7.4 Generated Static Sync（Evidence）

```text
src/margpa_runtime_llm/web/static/app.css  : 18.76kB -> 18.80kB（P4-CODEX-012由来Selector分、無変更）
src/margpa_runtime_llm/web/static/app.js   : 272.72kB -> 274.41kB（本Cycleの実Component/Translation変更を反映）
src/margpa_runtime_llm/web/static/index.html : 0.68kB（Byte数不変、Buildにより再生成）
Bootstrap Tag 3種（configuration-bootstrap/governance-bootstrap/runtime-governance-bootstrap）:
  Build後もVerbatimで存在することを`grep -c`で確認（結果: 3）。
```

### 7.5 Project-local Test Temp（Exact Path／Cleanup／Postflight）

```text
Exact Base Root : <PROJECT_ROOT>/.p4t
Created         : .p4t/p-c013a〜d（中間検証、都度作成・破棄）, .p4t/p-focused, .p4t/p-full, .p4t/t（最終検証）
Postflight       : `rm -rf .p4t` 実行後 `test -d .p4t` で不存在を確認、
                  `git status --short | grep p4t` で追跡対象からも消えていることを確認済み。
System Temp/`/tmp`/Provider Cache Fallback: 発生なし。
```

## 8. Changed Files（本Cycle、全件）

```text
frontend/src/App.tsx
frontend/src/App.test.tsx
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/components/GovernancePanel.tsx
frontend/src/components/GovernancePanel.test.tsx
frontend/src/components/RuntimeGovernancePanel.tsx
frontend/src/components/RuntimeGovernancePanel.test.tsx

src/margpa_runtime_llm/web/runtime_governance_routes.py
tests/integration/web/test_runtime_governance_web_app.py

src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
```

`tests/integration/web/test_runtime_governance_persistent_and_rag.py`／`tests/integration/web/test_runtime_governance_public_basic_call0.py`はAllowed Scopeに含まれていたが、既存Test実行で新Fieldとの非互換が確認されなかった（Additive Schema変更のため）ため無変更。

## 9. Existing Stable Edit

0件——Requirements／Architecture／ADR／Execution Plan／Acceptance Matrixは無編集（`git status --short`で確認）。Existing History／Existing Handoffの編集・置換・削除もなし。

## 10. Remaining Items

技術的Major Findingの残件なし（NONE）。

「Testが通ったためユーザーMac表示も直った」とは推測しない——本Cycleで行ったのは、Server正本StateのCanonical投影・Chat Terminal後のBest-effort Status再読・Observation Countの安全な投影・Semantic Capability境界の明示、それぞれをComponent／App-level／Backend Integration Testで固定したことのみである。実際のユーザーMac Browser表示の最終確認は、Codex Independent ReviewとユーザーMac再Acceptanceに委ねる。

## 11. Stop

本Handoff作成をもって`COMPLETE_CANDIDATE`として停止する。Git操作、Phase 4 Closure、Phase 5／6開始には進まない。
