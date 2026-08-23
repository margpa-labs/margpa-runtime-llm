# Phase 4 Codex Manual Acceptance State／Observability Rework Handoff

```yaml
document_id: phase_4_codex_manual_acceptance_state_observability_rework_handoff_20260822091607
status: rework_required
phase: phase_4
work_unit: p4_h_wu_005_state_observability_and_semantic_boundary
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-22 09:16:07 JST
trigger: user_mac_manual_acceptance_followup
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_manual_acceptance_ui_rework_handoff_ja_20260822083500.md
execution_order: predecessor_rework_completion_then_this_handoff
git_mutation: forbidden
phase_4_closure: forbidden
phase_5: forbidden
phase_6_implementation: forbidden
```

## 1. Execution Order

本Handoffは、先行する`phase_4_codex_manual_acceptance_ui_rework_handoff_ja_20260822083500.md`の修正・Validation・Completion Handoff作成が終わった後に実行する。

先行Reworkを中断・混合して同時に完了主張しない。先行Completion HandoffをRecovery Entryとして読み、実差分を確認してから本Work Unitへ入る。

## 2. User Findings

### P4-CODEX-013：Settings再Open時のMode表示がOFFへ戻る

Phase 3／4ともに、`OBSERVE`または`ENFORCE`を適用した後、Settings Modalを閉じて開き直すとMode選択表示が`OFF`へ戻る。

Process-local ModeはServer再起動まで維持される契約であり、Modal再OpenはMode Reset条件ではない。再Open時はServer正本のCurrent Modeを選択表示しなければならない。

Confirmed Root Cause：

- `GovernancePanel`／`RuntimeGovernancePanel`は`selectedMode`を常に`off`で初期化する。
- 同時に`syncedRevision`を現在StatusのRevisionで初期化する。
- 再Mount時にRevision差が存在しないため同期分岐が走らず、Server Statusが`observe`／`enforce`でもLocal Selectionだけ`off`のままとなる。

```text
Finding ID      : P4-CODEX-013
Severity        : MAJOR
Class           : CANONICAL STATE PROJECTION FAILURE
Server Mode     : 維持され得る
Displayed Mode  : 誤ってOFF
```

### P4-CODEX-014：Chat後のOBSERVE Resultが画面へ自動反映されない

Phase 4 Runtime Governance Statusは、App初期化、Mode Applyおよび手動Refresh時には取得されるが、Chat／Generation Terminal後には再取得されない。

さらに現在のPoint Status UIは、Execution State、Selected Rule数、SeverityおよびExecuted Action数だけを表示し、Observationの`pass／deviation／deferred_to_semantic_evaluator`内訳を表示しない。

このため、OBSERVEが内部で実行されても、UserはChat後の結果を画面で確認できない。`OBSERVEは非介入`と`OBSERVE結果が不可視`は別であり、非介入を理由に不可視を許容しない。

```text
Finding ID      : P4-CODEX-014
Severity        : MAJOR
Class           : OBSERVABILITY REFRESH／PROJECTION GAP
Generation Path : 変更禁止
Status Path     : Chat Terminal後に安全に再読
```

### P4-CODEX-015：Semantic Governance Capabilityの誤認防止

ARGD／DAGD由来Descriptorは現状すべて`REQUIRES_SEMANTIC_EVALUATOR`であり、Phase 4のDeterministic Evaluatorはそれらを`DEFERRED_TO_SEMANTIC_EVALUATOR`へ送る。現在介入可能なのはEmpty／Size Budget等の構造的Deviationだけである。

したがって、通常長のQwen回答に含まれる次の意味的FailureはPhase 4では検出・介入しない。

- 知ったかぶり。
- 根拠のない断定。
- 情報不足を無視した回答。
- 前提・文脈・結論の矛盾。
- 推論品質、不適切な確信度、意味的な誤答。

これらはPhase 6で、GD Descriptor → Semantic Evaluation Criteria → Judge Result → Governance Result → Action Resolver → Observe／Enforce／Repairを接続して成立させる。

P4-CODEX-015はPhase 4へSemantic Evaluatorを先行実装する指示ではない。Phase 4 UI／Statusが現在のCapabilityを正確に示し、`ENFORCEを選べる＝意味的Failureへ介入できる`という誤認を起こさないことを要求する。

## 3. Required Correction

### 3.1 Canonical Mode Selection Sync

Phase 3／4 Panelは、Mount時および新しいStatus Revision受信時に、選択ModeをServer StatusのCurrent Modeへ同期する。

必要条件：

1. Modalを閉じて再Openしても、Current Modeが`observe`なら`OBSERVE`を選択表示する。
2. Phase 4 Current Modeが`enforce`なら`ENFORCE`を選択表示する。
3. Server再起動後にServer正本が`off`なら`OFF`へ戻る。
4. Userが未ApplyのModeを選択中に、無関係な同Revision Re-renderだけで強制的にOFFへ戻さない。
5. Apply成功後のStatus再読では、Serverが返したMode／Revisionへ必ず収束する。

初期Stateと`syncedRevision`を別々に誤初期化しない。修正方法はReactの既存設計と整合する最小解を選ぶ。

### 3.2 Chat Terminal後のRuntime Governance Status Refresh

Phase 4 Runtime GovernanceがBootstrap Enabledの場合、GenerationのTerminal収束後に`/api/v3/runtime-governance/status`を再読する。

最低対象：

- Ephemeral Chatの正常Completion／Reject／Error／Cancel。
- Persistent New Turnの正常Completion／Reject／Error／Cancel。
- Retry／Regenerate等のDerived Turn Terminal。

必要条件：

- Status再読失敗がGeneration Result、Conversation Commitまたは表示済みCanonical Answerを失敗へ書き換えない。
- Status再読はBest-effortのObservability更新であり、Model CallやGenerationを再実行しない。
- OFF時のGovernance Point Call 0を壊さない。Status GET自体をGovernance Evaluationとして数えない。
- Public／Basic PreviewのGovernance Call 0／Route非公開境界を壊さない。
- Component Unmount後のState Update、無限Poll、Terminalごとの重複Fetchを作らない。

### 3.3 Safe Observation Summary Projection

`StandardGovernanceResult.observations`から、次のSafe CountをPoint Status APIへ追加してUI表示する。

```text
observation_count
pass_count
deviation_count
deferred_count
```

名称は既存Contract語彙に合わせて調整可能だが、少なくとも`deviation`と`deferred_to_semantic_evaluator`をUserが区別できなければならない。

Security条件：

- Definition本文、Rule全文、Prompt、Output、User Content、Absolute Path、Raw Exception、Secretを返さない。
- Countは同一`StandardGovernanceResult`から一度だけ投影し、再評価しない。
- Observation Outcomeが将来追加された場合、未知値をPassへ数えない。

UIは`main_model.pre`／`main_model.post`ごとにSafe Countを表示する。OBSERVE時にAction 0でも、Deferred／Deviation Countが見えるようにする。

### 3.4 Semantic Capabilityの明示

Phase 4 Runtime Governance Panelへ、少なくとも次を明示する。

```text
Phase 4のARGD／DAGD意味RuleはSemantic Evaluator未接続のためDeferred。
現在のENFORCEは登録済みの構造的Deviationだけへ介入する。
意味的FailureのJudge／RepairはPhase 6で接続予定。
```

日本語／英語双方へ追加する。誤って「ARGD／DAGDが動作していない」とだけ表示せず、Definition Load／Binding／Observationは成立し、意味評価と介入がDeferredである境界を正確に示す。

## 4. Required Tests

### Panel State

- Phase 3 Panelを`current_mode=observe`で初回Mountし、OBSERVEが選択表示される。
- Phase 4 Panelを`current_mode=observe`／`enforce`で初回Mountし、対応Modeが選択表示される。
- Modalを閉じて再OpenするApp-level TestでServer Current Modeを保持する。
- Revision更新時にServer Current Modeへ再同期する。

### Chat／Status Refresh

- Ephemeral Terminal後にRuntime Governance Statusが1回再読される。
- Persistent Terminal後に1回再読される。
- Derived Turn Terminal後に1回再読される。
- Status GET失敗でもChat／Conversation Terminal Resultは維持される。
- Governance Bootstrap Disabledでは追加Status GET 0。

### Observation Projection

- `pass／deviation／deferred`混在ResultをExact Countへ投影する。
- 空Observationは全Count 0。
- Raw Content／Path／Exception／SecretがResponseへ含まれない。
- UIがPoint別Countを表示する。
- OBSERVEではExecuted Action Count 0のままObservation Countを表示する。

### Semantic Boundary

- ARGD／DAGD Semantic DescriptorがPhase 4で`deferred`へ数えられ、PassやDeviationへ偽装されない。
- 通常の意味的FailureをPhase 4 ENFORCEが修復・再生成したというTest／Claimを作らない。
- Empty Output等の既存Structural Enforce Regressionは維持する。

## 5. Exact Allowed Mutation Scope

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
tests/integration/web/test_runtime_governance_persistent_and_rag.py
tests/integration/web/test_runtime_governance_public_basic_call0.py

src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html

docs/project/phases/phase_4/handoffs/phase_4_claude_state_observability_rework_complete_candidate_handoff_ja.md
docs/project/phases/phase_4/history/index/<本Rework用の新規Append-only Evidence 1件まで>
```

先行P4-CODEX-012 Reworkが変更したFileは、そのCompletion Handoffを確認してから必要な箇所だけ再編集する。Generated Staticは正規Frontend Buildから同期する。

Exact実装上、既存Generation Terminalの共通Helperへ最小変更が必要で、上記`App.tsx`だけでは成立しない場合は、勝手にBackend Generation Scopeを拡張せず停止して、必要Pathと理由をCompletionではない新規Scope Requestへ記録する。

## 6. Forbidden Scope

- Phase 6 Semantic Evaluator／Judge／Repairの先行実装。
- ARGD／DAGD Definition内容または`definitions/`の変更。
- Deterministic Evaluator、Binder、Action Resolver、Authority、Policy、Budgetの意味変更。
- Qwen Outputの自動書換え、無制限再生成または隠れたRepair。
- Conversation Storage Schema、RAG、Model Adapterの変更。
- `runtime_data/`、User Chat Data、Model、Secretへの接触。
- Project Root外Action、Provider Memory、System Temp fallback。
- Existing Stable Docs／Historyの上書き・削除。
- Git Mutation、Phase 4 Closure、Phase 5開始、Phase 6開始。

## 7. Validation／Stop Contract

Project-localの短いTemporary Pathだけを使用し、Focused Frontend／Backend、Frontend Full／Typecheck／Lint／Build、Backend関連Regression、Full Testおよび`git diff --check`を実行する。

Completion Handoffには次をExactに記録する。

```text
P4-CODEX-013..015              : CLOSED／OPEN
Predecessor P4-CODEX-012       : Exact Completion Handoff参照
Mode Reopen／Revision Tests     : Exact Test Name／Result
Terminal Status Refresh Matrix : Exact Path／Test／Call Count
Observation Count Projection   : Exact Contract／Test
Semantic Evaluator             : NOT IMPLEMENTED／DEFERRED TO PHASE 6
Generated Static Sync          : PASS／FAIL
Full／Focused／Static           : Exact Tool Output
Root-outside Action            : Verified Factのみ
Git Mutation                   : NOT PERFORMED
Phase 4 Closure                : NOT PERFORMED
Phase 5／6                     : NOT STARTED
Remaining Major                : NONE／Exact Finding
```

Claude側は`COMPLETE_CANDIDATE`で停止する。Codex Independent ReviewとユーザーMac再AcceptanceなしにPhase 4完了を宣言しない。
